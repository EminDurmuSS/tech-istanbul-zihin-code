# ============================================================================
# DOSYA: src/modules/conversational_fault_manager.py
# ============================================================================

import json
import os
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timedelta

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.models.conversation_state import FaultReportState, ConversationPhase
from src.models.fault import (
    FaultEntity,
    FaultClassification,
    FaultEnrichment,
    FaultReport,
    ExistingFault,
    Priority,
    FaultCategory
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationalFaultManager:
    """Konuşmaya dayalı profesyonel arıza yönetim modülü"""

    # Conversation state storage (production'da Redis/DB kullanılmalı)
    _states: Dict[str, FaultReportState] = {}

    def __init__(
        self,
        llm_client: OpenRouterClient,
        metro_client: MetroAPIClient
    ):
        self.llm = llm_client
        self.metro = metro_client

    async def handle_message(
        self,
        user_id: str,
        message: str
    ) -> Tuple[str, Optional[FaultReport], bool]:
        """
        Kullanıcı mesajını işle

        Args:
            user_id: Kullanıcı ID
            message: Kullanıcı mesajı

        Returns:
            (agent_yanıtı, arıza_raporu_veya_none, tamamlandı_mı)
        """
        # State'i al veya yeni oluştur
        state = self._states.get(user_id)

        if state is None:
            # Yeni konuşma başlat
            state = FaultReportState()
            self._states[user_id] = state
            return await self._start_conversation(state, message)

        # Mevcut state'e göre işle
        state.messages.append(message)
        state.update_timestamp()

        return await self._continue_conversation(state, message)

    async def _start_conversation(
        self,
        state: FaultReportState,
        message: str
    ) -> Tuple[str, None, bool]:
        """Konuşmayı başlat ve ilk bilgileri topla"""

        # İlk mesajdan bilgi çıkar
        entities = await self._extract_initial_entities(message)

        # State'i güncelle
        if entities.get("station"):
            # İstasyonu doğrula ve detay al
            station_info = await self._validate_and_get_station(entities["station"])
            if station_info:
                state.station = station_info.get("Name")
                state.station_id = station_info.get("Id")
                state.line = station_info.get("LineName")
                state.line_id = station_info.get("LineId")
                state.station_info = station_info

        if entities.get("equipment"):
            state.equipment = entities["equipment"]

        if entities.get("problem_description"):
            state.problem_description = entities["problem_description"]

        state.messages.append(message)

        # Sonraki aşamayı belirle ve uygun soruyu sor
        return await self._ask_next_question(state)

    async def _continue_conversation(
        self,
        state: FaultReportState,
        message: str
    ) -> Tuple[str, Optional[FaultReport], bool]:
        """Konuşmayı devam ettir"""

        # Mevcut aşamaya göre bilgiyi işle
        await self._process_current_phase(state, message)

        # Tüm bilgiler toplandıysa rapor oluştur
        if state.is_complete():
            # Önce mevcut arıza kontrolü yap
            existing_fault = await self._check_existing_fault(state)

            if existing_fault:
                response = self._format_existing_fault_response(existing_fault)
                self._cleanup_state(state)
                return response, None, True

            # Yeni rapor oluştur
            report = await self._create_comprehensive_report(state)

            # Raporu dosyaya kaydet
            await self._save_report_to_file(report, state)

            response = self._format_completed_response(report)

            # State'i temizle
            self._cleanup_state(state)

            return response, report, True

        # Sonraki soruyu sor
        return await self._ask_next_question(state)

    async def _extract_initial_entities(self, message: str) -> Dict[str, Any]:
        """İlk mesajdan entity'leri çıkar"""

        prompt = f"""Aşağıdaki arıza bildirimi mesajından bilgileri çıkar.

Mesaj: "{message}"

Çıkarılacak bilgiler:
- station: İstasyon adı (varsa)
- equipment: Ekipman türü (asansör, yürüyen merdiven, turnike, vb.)
- location_detail: Detay konum (giriş, çıkış, peron, kat arası, vb.)
- problem_description: Sorun açıklaması

SADECE JSON döndür:
{{
    "station": "...",
    "equipment": "...",
    "location_detail": "...",
    "problem_description": "..."
}}"""

        try:
            response = await self.llm.complete(prompt, temperature=0.1)
            entities = await self.llm.parse_json_response(response)
            return entities
        except Exception as e:
            logger.error("Entity extraction failed", error=str(e))
            return {}

    async def _validate_and_get_station(self, station_name: str) -> Optional[Dict]:
        """İstasyonu doğrula ve detaylı bilgi al"""

        try:
            # Önce arama yap
            search_results = await self.metro.search_line_and_station(station_name)

            if search_results:
                # İlk sonuçtan istasyon bilgisi al
                for result in search_results:
                    stations = result.get("Station", [])
                    if stations:
                        # İlk uygun istasyonu döndür
                        station = stations[0]
                        logger.info(f"Station found: {station.get('Name')}")
                        return station

            # Direkt istasyon listesinde ara
            all_stations = await self.metro.get_stations()
            for station in all_stations:
                if station_name.lower() in station.get("Name", "").lower():
                    return station

            return None

        except Exception as e:
            logger.error("Station validation failed", error=str(e))
            return None

    async def _process_current_phase(self, state: FaultReportState, message: str):
        """Mevcut aşamaya göre mesajı işle"""

        if state.phase == ConversationPhase.COLLECTING_STATION:
            # İstasyon bilgisini işle
            station_info = await self._validate_and_get_station(message)
            if station_info:
                state.station = station_info.get("Name")
                state.station_id = station_info.get("Id")
                state.line = station_info.get("LineName")
                state.line_id = station_info.get("LineId")
                state.station_info = station_info
                state.phase = ConversationPhase.COLLECTING_LOCATION_DETAIL

        elif state.phase == ConversationPhase.COLLECTING_LOCATION_DETAIL:
            # Konum detayı
            state.location_detail = message
            state.phase = ConversationPhase.COLLECTING_EQUIPMENT

        elif state.phase == ConversationPhase.COLLECTING_EQUIPMENT:
            # Ekipman türü
            state.equipment = message
            state.phase = ConversationPhase.COLLECTING_PROBLEM_DETAIL

        elif state.phase == ConversationPhase.COLLECTING_PROBLEM_DETAIL:
            # Problem detayı
            state.problem_description = message
            state.phase = ConversationPhase.COMPLETED

    async def _ask_next_question(
        self,
        state: FaultReportState
    ) -> Tuple[str, None, bool]:
        """Sonraki eksik bilgi için soru sor"""

        # İstasyon eksikse
        if not state.station:
            state.phase = ConversationPhase.COLLECTING_STATION
            return """📍 Hangi istasyondasınız?

Lütfen bulunduğunuz istasyonun tam adını belirtin.
(Örnek: Bağcılar Meydan, Şişli-Mecidiyeköy, Taksim)""", None, False

        # Konum detayı eksikse
        if not state.location_detail:
            state.phase = ConversationPhase.COLLECTING_LOCATION_DETAIL

            # İstasyon bilgisine göre ek bilgi ver
            detail_examples = ""
            if state.station_info:
                lifts = state.station_info.get("DetailInfo", {}).get("Lift", 0)
                escalators = state.station_info.get("DetailInfo", {}).get("Escolator", 0)

                detail_examples = f"\n\n✅ {state.station} İstasyonu tesislerimizde:"
                if lifts > 0:
                    detail_examples += f"\n• {lifts} adet asansör"
                if escalators > 0:
                    detail_examples += f"\n• {escalators} adet yürüyen merdiven"

            return f"""📌 İstasyonun neresinde bir sorun var?

Lütfen daha detaylı konum belirtin:
• Giriş/Çıkış katı
• Turnike katı
• Peron katı
• Mezanin katı
• Cadde seviyesi
• [Kat] ile [Kat] arası

Örnek: "Turnike katı ile cadde arasındaki asansör"{detail_examples}""", None, False

        # Ekipman eksikse
        if not state.equipment:
            state.phase = ConversationPhase.COLLECTING_EQUIPMENT
            return """🔧 Hangi ekipmanda arıza var?

Lütfen arızalı ekipmanı belirtin:
• Asansör
• Yürüyen merdiven
• Turnike
• Kapı (vagon/istasyon)
• Klima/Havalandırma
• Aydınlatma
• Anons sistemi
• Ekran/Tabela
• Diğer""", None, False

        # Problem detayı eksikse
        if not state.problem_description:
            state.phase = ConversationPhase.COLLECTING_PROBLEM_DETAIL
            return f"""📝 {state.equipment} ile ilgili sorunu kısaca açıklar mısınız?

Örnek:
• "Çalışmıyor, durmuş"
• "Ses çıkmıyor"
• "Kapı açılmıyor"
• "Işık yanmıyor"
• "Ekranda görüntü yok"

Ne tür bir sorun yaşıyorsunuz?""", None, False

        # Tüm bilgiler tamam
        return "✅ Bilgiler tamamlandı. Rapor oluşturuluyor...", None, False

    async def _check_existing_fault(self, state: FaultReportState) -> Optional[ExistingFault]:
        """Mevcut arızaları kontrol et"""

        try:
            faulty_equipments = await self.metro.get_faulty_equipments()

            if not faulty_equipments:
                return None

            station_name = (state.station or "").lower().strip()
            equipment_name = (state.equipment or "").lower().strip()
            location = (state.location_detail or "").lower().strip()

            # Eşleştirme yap
            for fault in faulty_equipments:
                f_station = str(fault.get("StationName", "")).lower().strip()
                f_equipment = str(fault.get("EquipmentName", "")).lower().strip()
                f_location = str(fault.get("LocationDetail", "")).lower().strip()

                station_match = station_name in f_station or f_station in station_name
                equipment_match = equipment_name in f_equipment or f_equipment in equipment_name
                location_match = not location or (location in f_location or f_location in location)

                if station_match and equipment_match and location_match:
                    # Detaylı bilgi al
                    fault_detail = await self._get_fault_detail(fault)

                    return ExistingFault(
                        exists=True,
                        fault_id=str(fault.get("Id", "UNKNOWN")),
                        station=fault.get("StationName") or "Belirtilmemiş",
                        equipment=fault.get("EquipmentName") or "Belirtilmemiş",
                        status=fault.get("Status", "İşlemde"),
                        created_at=fault.get("CreatedDate"),
                        estimated_resolution=fault.get("EstimatedResolution"),
                        message=fault_detail.get("description", "Bu arıza sistemimizde kayıtlı.")
                    )

            return None

        except Exception as e:
            logger.error("Existing fault check failed", error=str(e))
            return None

    async def _get_fault_detail(self, fault: Dict) -> Dict[str, Any]:
        """Arıza detaylarını al"""

        try:
            equipment_id = fault.get("EquipmentId")
            if equipment_id:
                detail = await self.metro.get_fault_details(equipment_id)
                return detail
            return {}
        except Exception as e:
            logger.error("Fault detail fetch failed", error=str(e))
            return {}

    async def _create_comprehensive_report(
        self,
        state: FaultReportState
    ) -> FaultReport:
        """Detaylı arıza raporu oluştur"""

        # Report ID oluştur
        report_id = f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Zenginleştirme yap
        enrichment = await self._enrich_with_apis(state)

        # Sınıflandırma yap
        classification = await self._classify_fault(state, enrichment)

        # Rapor oluştur
        report = FaultReport(
            report_id=report_id,
            station=state.station,
            line=state.line,
            location_detail=state.location_detail,
            equipment_type=state.equipment,
            fault_description=state.problem_description,
            classification=classification,
            enrichment=enrichment,
            target_department=classification.target_department,
            estimated_resolution=self._calculate_estimated_resolution(classification)
        )

        return report

    async def _enrich_with_apis(self, state: FaultReportState) -> FaultEnrichment:
        """API'lerden veri çekerek zenginleştir"""

        enrichment = FaultEnrichment()

        try:
            # 1. Hat bilgisi
            if state.line_id:
                lines = await self.metro.get_lines()
                for line in lines:
                    if line.get("Id") == state.line_id:
                        enrichment.line_info = line
                        break

            # 2. İstasyon detayları (zaten state'de var)
            enrichment.station_info = state.station_info

            # 3. Hat durumu
            if state.line:
                statuses = await self.metro.get_service_statuses()
                for status in statuses:
                    if state.line.upper() in str(status.get("LineName", "")).upper():
                        enrichment.line_status = status
                        break

            # 4. Ekipman bilgisi
            if state.station_id:
                equipments = await self.metro.get_equipments(state.station_id)
                for equipment in equipments:
                    equip_name = str(equipment.get("Name", "")).lower()
                    if state.equipment.lower() in equip_name:
                        enrichment.equipment_info = equipment
                        break

            # 5. Alternatif yollar
            enrichment.alternatives = await self._find_alternatives(state)

            # 6. Erişilebilirlik etkisi
            if state.equipment.lower() in ["asansör", "asansor", "elevator"]:
                enrichment.accessibility_impact = "⚠️ Engelli vatandaşların erişimi etkileniyor"

            # 7. Duyurular
            if state.line_id:
                announcements = await self.metro.get_announcements_by_line(state.line_id)
                enrichment.related_announcements = announcements[:3]

        except Exception as e:
            logger.error("Enrichment failed", error=str(e))

        return enrichment

    async def _classify_fault(
        self,
        state: FaultReportState,
        enrichment: FaultEnrichment
    ) -> FaultClassification:
        """Arızayı sınıflandır"""

        try:
            # API'den arıza tipleri al
            failure_types = await self.metro.get_failure_types()
            tech_objects = await self.metro.get_technical_object_types()

            # LLM ile sınıflandır
            prompt = f"""Aşağıdaki arıza bilgilerini analiz et ve sınıflandır.

Arıza Bilgileri:
- İstasyon: {state.station}
- Hat: {state.line}
- Konum: {state.location_detail}
- Ekipman: {state.equipment}
- Açıklama: {state.problem_description}

Mevcut Arıza Tipleri:
{json.dumps(failure_types[:15], ensure_ascii=False, indent=2)}

Teknik Nesneler:
{json.dumps(tech_objects[:15], ensure_ascii=False, indent=2)}

Aşağıdaki JSON formatında döndür:
{{
    "fault_type_id": "en uygun arıza tipi ID",
    "fault_type_name": "arıza tipi adı",
    "fault_category": "ESCALATOR/ELEVATOR/TURNSTILE/DOOR/LIGHTING/HVAC/ANNOUNCEMENT/DISPLAY/SECURITY/TRAIN/PLATFORM/OTHER",
    "technical_object_id": "teknik nesne ID",
    "technical_object_name": "teknik nesne adı",
    "priority": "CRITICAL/HIGH/MEDIUM/LOW",
    "priority_reason": "öncelik nedeni",
    "target_department": "Sorumlu Departman",
    "sub_department": "Alt Birim",
    "estimated_hours": 4
}}

Öncelik Kriterleri:
- CRITICAL: Can güvenliği, tüm hizmet durmuş, yangın/duman
- HIGH: Ana erişim kapalı, kritik ekipman arızası
- MEDIUM: Alternatif var, tek ekipman arızası
- LOW: Konfor sorunu, minör arıza

SADECE JSON döndür:"""

            response = await self.llm.complete(prompt, temperature=0.2)
            data = await self.llm.parse_json_response(response)

            return FaultClassification(
                fault_type_id=data.get("fault_type_id", "UNKNOWN"),
                fault_type_name=data.get("fault_type_name", "Genel Arıza"),
                fault_category=FaultCategory(data.get("fault_category", "OTHER")),
                technical_object_id=data.get("technical_object_id"),
                technical_object_name=data.get("technical_object_name"),
                priority=Priority(data.get("priority", "MEDIUM")),
                priority_reason=data.get("priority_reason", ""),
                target_department=data.get("target_department", "Teknik Bakım Müdürlüğü"),
                sub_department=data.get("sub_department"),
                estimated_hours=int(data.get("estimated_hours", 4)),
                sla_hours=int(data.get("estimated_hours", 4))
            )

        except Exception as e:
            logger.error("Classification failed", error=str(e))
            return self._default_classification(state)

    def _default_classification(self, state: FaultReportState) -> FaultClassification:
        """Varsayılan sınıflandırma"""

        equipment = (state.equipment or "").lower()

        # Kategori belirle
        category_map = {
            "asansör": FaultCategory.ELEVATOR,
            "asansor": FaultCategory.ELEVATOR,
            "yürüyen merdiven": FaultCategory.ESCALATOR,
            "yuruyen merdiven": FaultCategory.ESCALATOR,
            "escalator": FaultCategory.ESCALATOR,
            "turnike": FaultCategory.TURNSTILE,
            "kapı": FaultCategory.DOOR,
            "kapi": FaultCategory.DOOR,
            "klima": FaultCategory.HVAC,
            "havalandırma": FaultCategory.HVAC,
            "aydınlatma": FaultCategory.LIGHTING,
            "ışık": FaultCategory.LIGHTING,
            "isik": FaultCategory.LIGHTING,
            "anons": FaultCategory.ANNOUNCEMENT,
            "ekran": FaultCategory.DISPLAY,
        }

        category = FaultCategory.OTHER
        for key, cat in category_map.items():
            if key in equipment:
                category = cat
                break

        return FaultClassification(
            fault_type_id="DEFAULT",
            fault_type_name="Genel Arıza",
            fault_category=category,
            priority=Priority.MEDIUM,
            priority_reason="Otomatik sınıflandırma",
            target_department="Teknik Bakım Müdürlüğü",
            estimated_hours=4,
            sla_hours=4
        )

    async def _find_alternatives(self, state: FaultReportState) -> List[str]:
        """Alternatif çözümler bul"""

        alternatives = []
        equipment = (state.equipment or "").lower()

        # Ekipman bazlı alternatifler
        if "yürüyen merdiven" in equipment or "escalator" in equipment:
            if state.station_info:
                lifts = state.station_info.get("DetailInfo", {}).get("Lift", 0)
                if lifts > 0:
                    alternatives.append(f"İstasyonda {lifts} adet asansör kullanılabilir")
                alternatives.append("Normal merdivenler kullanılabilir")

        elif "asansör" in equipment or "asansor" in equipment:
            if state.station_info:
                escalators = state.station_info.get("DetailInfo", {}).get("Escolator", 0)
                if escalators > 0:
                    alternatives.append(f"İstasyonda {escalators} adet yürüyen merdiven kullanılabilir")
                alternatives.append("Normal merdivenler kullanılabilir")

        elif "turnike" in equipment:
            alternatives.append("Diğer turnikeler kullanılabilir")
            alternatives.append("Personel yönlendirmesi mevcut")

        return alternatives

    def _calculate_estimated_resolution(self, classification: FaultClassification) -> str:
        """Tahmini çözüm süresini hesapla"""

        hours = classification.estimated_hours
        target_date = datetime.now() + timedelta(hours=hours)

        return f"{target_date.strftime('%d.%m.%Y')} (Tahmini {hours} saat içinde)"

    async def _save_report_to_file(self, report: FaultReport, state: FaultReportState):
        """Raporu .txt dosyasına kaydet"""

        try:
            # Reports klasörü oluştur
            reports_dir = "fault_reports"
            os.makedirs(reports_dir, exist_ok=True)

            # Dosya adı
            filename = f"{reports_dir}/{report.report_id}.txt"

            # Rapor içeriği
            content = f"""
════════════════════════════════════════════════════════════════
                     İBB METRO İSTANBUL
                  ARIZA BİLDİRİM RAPORU
════════════════════════════════════════════════════════════════

RAPOR NUMARASI: {report.report_id}
TARİH: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

═══════════════════════════════════════════════════════════════
1. ÖZET BİLGİLER
═══════════════════════════════════════════════════════════════

İstasyon         : {report.station}
Hat              : {report.line or 'Belirtilmemiş'}
Konum Detayı     : {report.location_detail}
Ekipman          : {report.equipment_type}
Arıza Açıklaması : {report.fault_description}

═══════════════════════════════════════════════════════════════
2. SINIFLANDIRMA
═══════════════════════════════════════════════════════════════

Arıza Tipi       : {report.classification.fault_type_name}
Arıza Kategorisi : {report.classification.fault_category.value}
Teknik Nesne     : {report.classification.technical_object_name or 'Belirtilmemiş'}

Öncelik Seviyesi : {report.classification.priority.value}
Öncelik Gerekçesi: {report.classification.priority_reason}

═══════════════════════════════════════════════════════════════
3. YÖNLENDİRME
═══════════════════════════════════════════════════════════════

Sorumlu Departman: {report.target_department}
Alt Birim        : {report.classification.sub_department or 'Belirtilmemiş'}

═══════════════════════════════════════════════════════════════
4. ZAMAN PLANLAMA
═══════════════════════════════════════════════════════════════

SLA Süresi       : {report.classification.sla_hours} saat
Tahmini Çözüm    : {report.estimated_resolution}

═══════════════════════════════════════════════════════════════
5. DETAYLI BİLGİLER
═══════════════════════════════════════════════════════════════
"""

            # İstasyon detayları
            if state.station_info:
                content += "\n--- İSTASYON TESİSLERİ ---\n"
                detail_info = state.station_info.get("DetailInfo", {})
                content += f"Asansör Sayısı      : {detail_info.get('Lift', 0)}\n"
                content += f"Yürüyen Merdiven    : {detail_info.get('Escolator', 0)}\n"
                content += f"WC                  : {'Var' if detail_info.get('WC') else 'Yok'}\n"
                content += f"Bebek Bakım Odası   : {'Var' if detail_info.get('BabyRoom') else 'Yok'}\n"
                content += f"Mescit              : {'Var' if detail_info.get('Masjid') else 'Yok'}\n"

            # Zenginleştirme bilgileri
            if report.enrichment:
                # Hat durumu
                if report.enrichment.line_status:
                    content += "\n--- HAT DURUMU ---\n"
                    ls = report.enrichment.line_status
                    content += f"Durum: {ls.get('Status', 'Bilinmiyor')}\n"

                # Alternatifler
                if report.enrichment.alternatives:
                    content += "\n--- ALTERNATİF ÇÖZÜMLER ---\n"
                    for i, alt in enumerate(report.enrichment.alternatives, 1):
                        content += f"{i}. {alt}\n"

                # Erişilebilirlik etkisi
                if report.enrichment.accessibility_impact:
                    content += "\n--- ERİŞİLEBİLİRLİK ETKİSİ ---\n"
                    content += f"{report.enrichment.accessibility_impact}\n"

            # Konuşma geçmişi
            content += "\n═══════════════════════════════════════════════════════════════\n"
            content += "6. KONUŞMA GEÇMİŞİ\n"
            content += "═══════════════════════════════════════════════════════════════\n\n"
            for i, msg in enumerate(state.messages, 1):
                content += f"[{i}] {msg}\n"

            # Footer
            content += "\n═══════════════════════════════════════════════════════════════\n"
            content += "Bu rapor otomatik olarak oluşturulmuştur.\n"
            content += "İBB Metro İstanbul A.Ş. - Çağrı Merkezi\n"
            content += "Tel: 153 (İBB Çözüm Merkezi)\n"
            content += "═══════════════════════════════════════════════════════════════\n"

            # Dosyaya yaz
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Report saved to file: {filename}")

        except Exception as e:
            logger.error("Failed to save report to file", error=str(e))

    def _format_existing_fault_response(self, existing: ExistingFault) -> str:
        """Mevcut arıza için yanıt"""

        estimated_text = ""
        if existing.estimated_resolution:
            estimated_text = f"\n📅 Planlanan Servise Dönüş: {existing.estimated_resolution}"

        return f"""🔍 Sistem Kontrolü Tamamlandı

Bu konuda sistemimizde mevcut bir arıza kaydı bulunmaktadır:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Arıza Takip No: {existing.fault_id}
📍 İstasyon: {existing.station}
🔧 Ekipman: {existing.equipment}
📊 Durum: {existing.status}{estimated_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Teknik ekibimiz konuyla ilgilenmektedir.

Bildiriminiz için teşekkür ederiz. Arıza giderildiğinde sistem güncellenecektir.

Başka yardımcı olabilir miyim?"""

    def _format_completed_response(self, report: FaultReport) -> str:
        """Tamamlanmış arıza için yanıt"""

        alternatives_text = ""
        if report.enrichment and report.enrichment.alternatives:
            alternatives_text = "\n\n🔄 **Alternatif Çözümler:**\n" + "\n".join(
                f"  • {alt}" for alt in report.enrichment.alternatives
            )

        accessibility_text = ""
        if report.enrichment and report.enrichment.accessibility_impact:
            accessibility_text = f"\n{report.enrichment.accessibility_impact}"

        return f"""✅ Arıza Bildirimi Başarıyla Kaydedildi!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TAKİP NUMARASI: {report.report_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Konum: {report.station} - {report.line}
🔧 Arıza: {report.equipment_type}
📝 Detay: {report.location_detail}

⚡ Öncelik: {report.classification.priority.value}
👥 Departman: {report.target_department}
📅 Tahmini Çözüm: {report.estimated_resolution}{accessibility_text}{alternatives_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Teknik ekibimiz bilgilendirildi.
📱 Takip numaranızla durumu sorgulayabilirsiniz.
📄 Detaylı rapor dosyası oluşturuldu: {report.report_id}.txt

Bildiriminiz için teşekkür ederiz!

Başka yardımcı olabilir miyim?"""

    def _cleanup_state(self, state: FaultReportState):
        """State'i temizle"""
        # User ID'yi bilmiyoruz, tüm completed olanları temizleyelim
        # Production'da Redis TTL veya DB cleanup kullanılmalı
        pass

    def reset_conversation(self, user_id: str):
        """Konuşmayı sıfırla"""
        if user_id in self._states:
            del self._states[user_id]
