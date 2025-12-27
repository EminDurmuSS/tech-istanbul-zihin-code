
# ============================================================================
# DOSYA: src/modules/fault_manager.py
# ============================================================================

import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.modules.smart_api_router import SmartAPIRouter
from src.modules.enhanced_fault_reporter import EnhancedFaultReporter
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
from src.utils.validators import normalize_station_name, extract_equipment_type
from src.utils.data_loader import (
    get_department_info,
    get_sla_hours,
    get_priority_from_description
)

logger = get_logger(__name__)


class FaultManager:
    """Arıza yönetim modülü"""
    
    ENTITY_EXTRACTION_PROMPT = """Aşağıdaki kullanıcı mesajından arıza bilgilerini JSON formatında çıkar.

Mesaj: "{message}"

Çıkarılacak bilgiler:
- station: İstasyon adı (null eğer belirtilmemişse)
- line: Hat adı/numarası - M1, M2, M7 vb. (null eğer belirtilmemişse)
- equipment: Arızalı ekipman türü (asansör, yürüyen merdiven, turnike, kapı, klima, aydınlatma, anons sistemi, ekran vb.)
- location_detail: Konum detayı (giriş, çıkış, peron, kat vb.)
- problem_description: Sorunun kısa açıklaması
- severity_hint: Aciliyet ipucu (can güvenliği, erişim engeli, konfor sorunu vb.)

SADECE JSON döndür, başka açıklama yapma:"""

    CLASSIFICATION_PROMPT = """Arıza bilgilerini analiz et ve sınıflandır.

Arıza bilgileri:
{fault_info}

Mevcut arıza türleri:
{fault_types}

Mevcut teknik nesne türleri:
{technical_objects}

Aşağıdaki JSON formatında sınıflandırma yap:
{{
    "fault_type_id": "en uygun arıza tipi ID",
    "fault_type_name": "arıza tipi adı",
    "fault_category": "ESCALATOR/ELEVATOR/TURNSTILE/DOOR/LIGHTING/HVAC/ANNOUNCEMENT/DISPLAY/SECURITY/TRAIN/PLATFORM/OTHER",
    "technical_object_id": "teknik nesne ID (varsa)",
    "technical_object_name": "teknik nesne adı",
    "priority": "CRITICAL/HIGH/MEDIUM/LOW",
    "priority_reason": "öncelik gerekçesi (kısa)",
    "target_department": "yönlendirilecek departman",
    "sub_department": "alt birim (varsa)",
    "estimated_hours": tahmini çözüm süresi (saat, integer)
}}

Öncelik kriterleri:
- CRITICAL: Can güvenliği, tren durması, yangın/duman
- HIGH: Hizmet kesintisi, ana erişim engeli
- MEDIUM: Ekipman arızası, alternatif mevcut
- LOW: Konfor, minör sorunlar

SADECE JSON döndür:"""

    REPORT_PROMPT = """İBB için profesyonel ve detaylı bir arıza raporu oluştur.

Arıza Bilgileri:
{fault_data}

Sınıflandırma:
{classification}

Zenginleştirme Verileri:
{enrichment}

Aşağıdaki formatta Türkçe rapor oluştur:

## ARIZA RAPORU - {report_id}

### ÖZET
[1-2 cümle net özet]

### KONUM BİLGİLERİ
- Hat: [hat adı]
- İstasyon: [istasyon adı]
- Detay Konum: [konum detayı]

### ARIZA DETAYLARI
- Arıza Türü: [tür]
- Arıza Tipi: [tip]
- Ekipman: [ekipman]
- Açıklama: [açıklama]

### ÖNCELİK DEĞERLENDİRMESİ
- Seviye: [CRITICAL/HIGH/MEDIUM/LOW]
- Gerekçe: [gerekçe]
- SLA: [saat] saat

### ETKİ ANALİZİ
[Yolcu etkisi, erişilebilirlik etkisi, alternatifler]

### YÖNLENDİRME
- Departman: [departman]
- Alt Birim: [alt birim]

### ÖNERİLEN AKSİYONLAR
1. [aksiyon 1]
2. [aksiyon 2]
3. [aksiyon 3]

### VATANDAŞ YÖNLENDİRME
[Alternatif erişim yolları ve öneriler]"""

    def __init__(
        self,
        llm_client: OpenRouterClient,
        metro_client: MetroAPIClient
    ):
        self.llm = llm_client
        self.metro = metro_client
        self.api_router = SmartAPIRouter(metro_client, llm_client)
        self.enhanced_reporter = EnhancedFaultReporter(metro_client, llm_client, self.api_router)
    
    async def handle_fault_report(
        self,
        message: str,
        entities: Optional[Dict] = None
    ) -> Tuple[str, Optional[FaultReport]]:
        """
        Arıza bildirimi işle
        
        Args:
            message: Kullanıcı mesajı
            entities: Önceden çıkarılmış entity'ler (opsiyonel)
            
        Returns:
            (kullanıcı_yanıtı, arıza_raporu)
        """
        try:
            # 1. Entity extraction
            if entities is None:
                entities = await self.extract_entities(message)
            
            fault_entity = FaultEntity(**entities)
            
            # 2. Mevcut arıza kontrolü
            existing = await self.check_existing_fault(fault_entity)
            if existing:
                response = self._format_existing_fault_response(existing)
                return response, None
            
            # 3. Arıza sınıflandırma
            classification = await self.classify_fault(fault_entity)
            
            # 4. Zenginleştirme
            enrichment = await self.enrich_fault(fault_entity)
            
            # 5. Rapor oluştur
            report = await self.create_report(
                fault_entity,
                classification,
                enrichment
            )
            
            # 6. Kullanıcı yanıtı
            response = self._format_new_fault_response(report, enrichment)
            
            return response, report
            
        except Exception as e:
            logger.error("Fault handling error", error=str(e))
            return self._format_error_response(), None
    
    async def extract_entities(self, message: str) -> Dict[str, Any]:
        """Mesajdan entity'leri çıkar"""
        
        prompt = self.ENTITY_EXTRACTION_PROMPT.format(message=message)
        
        response = await self.llm.complete(prompt, temperature=0.1)
        entities = await self.llm.parse_json_response(response)
        
        # Fallback: basit keyword extraction
        if not entities.get("equipment"):
            entities["equipment"] = extract_equipment_type(message)
        
        if not entities.get("station"):
            entities["station"] = None
        else:
            entities["station"] = normalize_station_name(entities["station"])
        
        return entities
    
    async def check_existing_fault(
        self,
        fault_entity: FaultEntity
    ) -> Optional[ExistingFault]:
        """Mevcut arızaları kontrol et - API'den arızalı ekipmanları çek"""

        try:
            # GetFaultyEquipments API'si ile aktif arızaları al
            response = await self.metro.get_faulty_equipments()

            # Response yapısını kontrol et
            if isinstance(response, dict):
                faults = response.get("Data", [])
            else:
                faults = response if isinstance(response, list) else []

            if not faults:
                logger.info("No active faults in system")
                return None

            station = (fault_entity.station or "").lower().strip()
            equipment = (fault_entity.equipment or "").lower().strip()

            logger.debug(f"Checking for faults - Station: {station}, Equipment: {equipment}")
            logger.debug(f"Total active faults: {len(faults)}")

            # Arıza eşleştirme
            for fault in faults:
                fault_station = str(fault.get("StationName", "")).lower().strip()
                fault_equipment = str(fault.get("EquipmentName", "")).lower().strip()
                fault_type = str(fault.get("FaultType", "")).lower().strip()

                # İstasyon eşleşmesi
                station_match = False
                if station:
                    # Tam eşleşme veya kısmi eşleşme
                    station_match = (
                        station == fault_station or
                        station in fault_station or
                        fault_station in station
                    )

                # Ekipman eşleşmesi
                equipment_match = False
                if equipment:
                    # Ekipman tiplerini normalize et
                    equip_normalized = self._normalize_equipment(equipment)
                    fault_equip_normalized = self._normalize_equipment(fault_equipment)

                    equipment_match = (
                        equip_normalized == fault_equip_normalized or
                        equip_normalized in fault_equip_normalized or
                        fault_equip_normalized in equip_normalized or
                        equip_normalized in fault_type or
                        fault_type in equip_normalized
                    )

                # Eşleşme varsa
                if station_match and equipment_match:
                    logger.info(f"Existing fault found - ID: {fault.get('Id')}")

                    return ExistingFault(
                        exists=True,
                        fault_id=str(fault.get("Id", "UNKNOWN")),
                        station=fault.get("StationName", "Belirtilmemiş"),
                        equipment=fault.get("EquipmentName", "Belirtilmemiş"),
                        status=fault.get("Status", "İşlemde"),
                        created_at=fault.get("CreatedDate"),
                        estimated_resolution=fault.get("EstimatedResolution"),
                        message="Bu arıza sistemimizde zaten kayıtlı."
                    )

            logger.info("No matching fault found - will create new")
            return None

        except Exception as e:
            logger.error("Existing fault check failed", error=str(e))
            # Hata durumunda None dön (yeni arıza olarak işlensin)
            return None

    def _normalize_equipment(self, equipment: str) -> str:
        """Ekipman tipini normalize et"""
        equipment = equipment.lower().strip()

        # Türkçe karakter düzeltmeleri
        replacements = {
            "asansör": "asansor",
            "yürüyen merdiven": "yuruyen merdiven",
            "turnike": "turnike",
            "kapı": "kapi",
            "ışık": "isik",
            "aydınlatma": "aydinlatma",
            "klima": "klima",
            "havalandırma": "havalandirma"
        }

        for key, value in replacements.items():
            if key in equipment:
                return value

        return equipment
    
    async def classify_fault(
        self,
        fault_entity: FaultEntity
    ) -> FaultClassification:
        """Arızayı sınıflandır"""
        
        try:
            # API'den arıza türlerini al
            fault_types = await self.metro.get_failure_types()
            tech_objects = await self.metro.get_technical_object_types()
            
            prompt = self.CLASSIFICATION_PROMPT.format(
                fault_info=json.dumps(fault_entity.model_dump(), ensure_ascii=False),
                fault_types=json.dumps(fault_types[:20], ensure_ascii=False),
                technical_objects=json.dumps(tech_objects[:20], ensure_ascii=False)
            )
            
            response = await self.llm.complete(prompt, temperature=0.2)
            data = await self.llm.parse_json_response(response)
            
            return FaultClassification(
                fault_type_id=data.get("fault_type_id", "UNKNOWN"),
                fault_type_name=data.get("fault_type_name", "Belirsiz"),
                fault_category=FaultCategory(data.get("fault_category", "OTHER")),
                technical_object_id=data.get("technical_object_id"),
                technical_object_name=data.get("technical_object_name"),
                priority=Priority(data.get("priority", "MEDIUM")),
                priority_reason=data.get("priority_reason", ""),
                target_department=data.get("target_department", "Teknik Bakım"),
                sub_department=data.get("sub_department"),
                estimated_hours=int(data.get("estimated_hours", 4)),
                sla_hours=int(data.get("estimated_hours", 4))
            )
            
        except Exception as e:
            logger.warning("Fault classification failed", error=str(e))
            return self._default_classification(fault_entity)
    
    async def enrich_fault(
        self,
        fault_entity: FaultEntity
    ) -> FaultEnrichment:
        """Arıza verilerini zenginleştir"""
        
        enrichment = FaultEnrichment()
        
        try:
            # Hizmet durumu
            statuses = await self.metro.get_service_statuses()
            if fault_entity.line:
                for status in statuses:
                    if fault_entity.line.upper() in str(status.get("LineName", "")).upper():
                        enrichment.line_status = status
                        break
            
            # İstasyon bilgisi
            if fault_entity.station:
                stations = await self.metro.get_stations()
                for station in stations:
                    if fault_entity.station.lower() in str(station.get("Name", "")).lower():
                        enrichment.station_info = station
                        break
            
            # Alternatifler
            enrichment.alternatives = self._find_alternatives(fault_entity)
            
            # Erişilebilirlik etkisi
            if fault_entity.equipment in ["asansör", "yürüyen merdiven"]:
                enrichment.accessibility_impact = "Engelli erişimi etkileniyor"
            
        except Exception as e:
            logger.warning("Fault enrichment failed", error=str(e))
        
        return enrichment
    
    async def create_report(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        enrichment: FaultEnrichment
    ) -> FaultReport:
        """
        Arıza raporu oluştur (Enhanced Reporter kullanarak)
        """
        try:
            # Enhanced reporter ile zenginleştirilmiş rapor oluştur
            comprehensive_report = await self.enhanced_reporter.create_comprehensive_report(
                fault_entity,
                classification,
                channel="phone"
            )

            # FaultReport objesi oluştur
            report_id = comprehensive_report["report_id"]

            return FaultReport(
                report_id=report_id,
                station=fault_entity.station or "Belirtilmedi",
                line=fault_entity.line,
                location_detail=fault_entity.location_detail,
                equipment_type=fault_entity.equipment or "Belirtilmedi",
                fault_description=fault_entity.problem_description or "",
                classification=classification,
                enrichment=enrichment,
                target_department=classification.target_department,
                estimated_resolution=f"{classification.estimated_hours} saat"
            )

        except Exception as e:
            logger.error("Enhanced report creation failed, using fallback", error=str(e))

            # Fallback: basit rapor
            report_id = f"MET-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            return FaultReport(
                report_id=report_id,
                station=fault_entity.station or "Belirtilmedi",
                line=fault_entity.line,
                location_detail=fault_entity.location_detail,
                equipment_type=fault_entity.equipment or "Belirtilmedi",
                fault_description=fault_entity.problem_description or "",
                classification=classification,
                enrichment=enrichment,
                target_department=classification.target_department,
                estimated_resolution=f"{classification.estimated_hours} saat"
            )
    
    def _default_classification(
        self,
        fault_entity: FaultEntity
    ) -> FaultClassification:
        """Varsayılan sınıflandırma"""

        # Ekipman tipine göre varsayılan kategori
        equipment = (fault_entity.equipment or "").lower()

        category_map = {
            "asansör": FaultCategory.ELEVATOR,
            "yürüyen merdiven": FaultCategory.ESCALATOR,
            "turnike": FaultCategory.TURNSTILE,
            "kapı": FaultCategory.DOOR,
            "klima": FaultCategory.HVAC,
            "aydınlatma": FaultCategory.LIGHTING,
            "ışık": FaultCategory.LIGHTING,
            "anons": FaultCategory.ANNOUNCEMENT,
            "ekran": FaultCategory.DISPLAY,
        }

        category = FaultCategory.OTHER
        for key, cat in category_map.items():
            if key in equipment:
                category = cat
                break

        # Açıklamadan priority çıkar
        description = fault_entity.problem_description or ""
        priority = get_priority_from_description(description)

        # Department bilgisini data'dan al
        dept_info = get_department_info(category.value)
        target_department = dept_info.get("name", "Genel Bakım Müdürlüğü")
        sub_department = dept_info.get("sub_unit")

        # SLA saatini data'dan al
        sla_hours = get_sla_hours(category.value, priority)

        return FaultClassification(
            fault_type_id="DEFAULT",
            fault_type_name="Genel Arıza",
            fault_category=category,
            priority=Priority(priority),
            priority_reason="Otomatik sınıflandırma",
            target_department=target_department,
            sub_department=sub_department,
            estimated_hours=int(sla_hours),
            sla_hours=int(sla_hours)
        )
    
    def _find_alternatives(self, fault_entity: FaultEntity) -> list:
        """Alternatif yollar bul"""
        alternatives = []
        
        equipment = (fault_entity.equipment or "").lower()
        
        if "yürüyen merdiven" in equipment:
            alternatives.append("Merdiven veya asansör kullanılabilir")
        elif "asansör" in equipment:
            alternatives.append("Yürüyen merdiven veya merdiven kullanılabilir")
        elif "turnike" in equipment:
            alternatives.append("Diğer turnikeler kullanılabilir")
        
        return alternatives
    
    def _format_existing_fault_response(self, existing: ExistingFault) -> str:
        """Mevcut arıza için yanıt"""
        return f"""Anlıyorum, bu konuda bilgi vereyim.

📋 **Bu arıza sistemimizde zaten kayıtlı**

- Arıza ID: {existing.fault_id}
- İstasyon: {existing.station}
- Ekipman: {existing.equipment}
- Durum: {existing.status}

Teknik ekibimiz konuyla ilgileniyor. Düzeldiğinde bilgilendirileceksiniz.

Başka yardımcı olabilir miyim?"""
    
    def _format_new_fault_response(
        self,
        report: FaultReport,
        enrichment: FaultEnrichment
    ) -> str:
        """Yeni arıza için yanıt"""
        
        alternatives_text = ""
        if enrichment.alternatives:
            alternatives_text = "\n\n🔄 **Alternatifler:**\n" + "\n".join(
                f"• {alt}" for alt in enrichment.alternatives
            )
        
        accessibility_text = ""
        if enrichment.accessibility_impact:
            accessibility_text = f"\n⚠️ {enrichment.accessibility_impact}"
        
        return f"""Arıza bildirimi alındı! 🚇

📋 **Takip Numaranız: {report.report_id}**

📍 Konum: {report.station}
🔧 Arıza: {report.equipment_type}
⏱️ Tahmini Çözüm: {report.estimated_resolution}
📌 Departman: {report.target_department}{accessibility_text}{alternatives_text}

Teknik ekibimiz bilgilendirildi. Durumu takip edebilirsiniz.

Başka yardımcı olabilir miyim?"""
    
    def _format_error_response(self) -> str:
        """Hata yanıtı"""
        return """Üzgünüm, arıza kaydı oluşturulurken bir sorun oluştu.

Lütfen birkaç dakika sonra tekrar deneyin veya 153 numaralı İBB Çözüm Merkezi'ni arayın.

Başka yardımcı olabilir miyim?"""

