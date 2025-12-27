# ============================================================================
# DOSYA: src/modules/enhanced_fault_reporter.py
# AÇIKLAMA: Geliştirilmiş Arıza Rapor Sistemi - İBB için zengin raporlar
# ============================================================================

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.modules.smart_api_router import SmartAPIRouter
from src.models.fault import (
    FaultEntity,
    FaultClassification,
    FaultEnrichment,
    FaultReport,
    Priority
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedFaultReporter:
    """
    Geliştirilmiş arıza rapor sistemi

    İBB için çok detaylı, zenginleştirilmiş arıza raporları oluşturur.
    Tüm ilgili API'lerden veri toplayıp analiz eder.
    """

    REPORT_GENERATION_PROMPT = """İBB Metro İstanbul için profesyonel ve çok detaylı bir arıza raporu oluştur.

Arıza Bilgileri:
{fault_info}

Sınıflandırma:
{classification}

API'den Toplanan Veriler:
{api_data}

Aşağıdaki formatta TÜRKÇE, DETAYLI ve PROFESYONEL bir rapor oluştur:

## ARIZA RAPORU #{report_id}
Oluşturma Tarihi: {timestamp}

### 📋 ÖZET BİLGİLER
**Durum:** {status}
**Öncelik:** {priority}
**Tahmini Çözüm Süresi:** {estimated_hours} saat
**Hedef Departman:** {department}

### 📍 KONUM DETAYLARI
**Hat:** {line}
**İstasyon:** {station}
**Konum Detayı:** {location}
**İstasyon Bilgileri:**
  - Asansör Sayısı: {elevator_count}
  - Yürüyen Merdiven Sayısı: {escalator_count}
  - Engelli WC: {disabled_wc}
  - Bebek Bakım Odası: {baby_room}

### 🔧 ARIZA DETAYLARI
**Ekipman Türü:** {equipment_type}
**Arıza Kategorisi:** {fault_category}
**Arıza Tipi:** {fault_type}
**Teknik Nesne:** {technical_object}
**Sorun Açıklaması:** {problem_description}

### ⚡ ÖNCELİK DEĞERLENDİRMESİ
**Öncelik Seviyesi:** {priority_level}
**Gerekçe:** {priority_reason}
**SLA (Hizmet Seviyesi Anlaşması):** {sla_hours} saat
**Can Güvenliği Riski:** {safety_risk}
**Hizmet Kesintisi:** {service_interruption}

### 👥 ETKİ ANALİZİ
**Yolcu Etkisi:** {passenger_impact}
**Erişilebilirlik Etkisi:** {accessibility_impact}
**Alternatif Erişim Yolları:** {alternatives}
**Etkilenen Alan:** {affected_area}
**Günlük Ortalama Yolcu (tahmini):** {daily_passengers}

### 🚦 HİZMET DURUMU
**Hat Durumu:** {line_status}
**Mevcut Duyurular:** {announcements}
**Benzer Arızalar:** {similar_faults}

### 🎯 YÖNLENDİRME
**Hedef Departman:** {target_department}
**Alt Birim:** {sub_department}
**Bildirilmesi Gerekenler:** {notifications}
**İlgili Kişiler:** {contacts}

### ✅ ÖNERİLEN AKSİYONLAR
1. **Acil Müdahale:**
   - {action_1}

2. **Teknik Değerlendirme:**
   - {action_2}

3. **Yolcu Yönlendirme:**
   - {action_3}

4. **İletişim:**
   - {action_4}

5. **Takip:**
   - {action_5}

### 💡 VATANDAŞ YÖNLENDİRME
**Alternatif Ulaşım:**
{citizen_guidance}

**Tahmini Düzeltme Süresi:** {estimated_fix_time}
**Bilgilendirme Kanalları:** Metro İstanbul mobil uygulaması, metro.istanbul websitesi

### 📊 TEKNİK VERİLER
```json
{technical_data}
```

### 📝 NOTLAR
{additional_notes}

---
**Rapor ID:** {report_id}
**Oluşturan Sistem:** Metro Agent v1.0
**Kanal:** {channel}
"""

    def __init__(
        self,
        metro_client: MetroAPIClient,
        llm_client: OpenRouterClient,
        api_router: SmartAPIRouter
    ):
        self.metro = metro_client
        self.llm = llm_client
        self.api_router = api_router

    async def create_comprehensive_report(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        channel: str = "phone"
    ) -> Dict[str, Any]:
        """
        Kapsamlı arıza raporu oluştur

        Args:
            fault_entity: Arıza entity bilgileri
            classification: Arıza sınıflandırması
            channel: Bildiri kanalı

        Returns:
            Detaylı rapor dict'i
        """
        try:
            logger.info("Creating comprehensive fault report", station=fault_entity.station)

            # 1. API Router ile tüm ilgili verileri topla
            api_data = await self._collect_all_relevant_data(fault_entity, classification)

            # 2. Verileri analiz et ve zenginleştir
            enriched_data = await self._enrich_with_analysis(
                fault_entity,
                classification,
                api_data
            )

            # 3. Detaylı rapor oluştur
            report = await self._generate_detailed_report(
                fault_entity,
                classification,
                api_data,
                enriched_data,
                channel
            )

            logger.info("Comprehensive report created", report_id=report["report_id"])

            return report

        except Exception as e:
            logger.error("Report creation failed", error=str(e))
            return self._create_minimal_report(fault_entity, classification)

    async def _collect_all_relevant_data(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification
    ) -> Dict[str, Any]:
        """Tüm ilgili API verilerini topla"""

        # API Router kullanarak otomatik veri toplama
        entities = {
            "station": fault_entity.station,
            "line": fault_entity.line,
            "equipment": fault_entity.equipment
        }

        api_data = await self.api_router.route_query(
            query=f"{fault_entity.station} {fault_entity.equipment} arıza",
            entities=entities,
            intent_type="FAULT_REPORT"
        )

        return api_data

    async def _enrich_with_analysis(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        api_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verileri analiz et ve zenginleştir"""

        enriched = {}

        # İstasyon analizi
        stations = api_data.get("stations", [])
        if stations and fault_entity.station:
            station_info = self._find_station_info(fault_entity.station, stations)
            if station_info:
                enriched["station_details"] = station_info
                enriched["elevator_count"] = station_info.get("DetailInfo", {}).get("Lift", 0)
                enriched["escalator_count"] = station_info.get("DetailInfo", {}).get("Escolator", 0)
                enriched["disabled_wc"] = "Var" if station_info.get("DetailInfo", {}).get("WC") else "Yok"
                enriched["baby_room"] = "Var" if station_info.get("DetailInfo", {}).get("BabyRoom") else "Yok"

        # Hat durumu analizi
        service_statuses = api_data.get("service_status", [])
        if service_statuses:
            enriched["line_status"] = service_statuses[0] if service_statuses else {}

        # Mevcut arızalar analizi
        faulty_equipments = api_data.get("faulty_equipments", [])
        similar_faults = self._find_similar_faults(fault_entity, faulty_equipments)
        enriched["similar_faults"] = similar_faults
        enriched["similar_fault_count"] = len(similar_faults)

        # Duyurular
        announcements = api_data.get("announcements", [])
        relevant_announcements = announcements[:3] if announcements else []
        enriched["relevant_announcements"] = relevant_announcements

        # Risk değerlendirmesi
        enriched["safety_risk"] = self._assess_safety_risk(classification, fault_entity)
        enriched["service_interruption"] = self._assess_service_interruption(classification)
        enriched["passenger_impact"] = self._estimate_passenger_impact(fault_entity, classification)
        enriched["accessibility_impact"] = self._assess_accessibility_impact(fault_entity)

        # Alternatif erişim yolları
        enriched["alternatives"] = self._generate_alternatives(fault_entity, enriched)

        # Aksiyon önerileri
        enriched["recommended_actions"] = self._generate_action_plan(classification, fault_entity)

        # Vatandaş yönlendirme
        enriched["citizen_guidance"] = self._generate_citizen_guidance(fault_entity, enriched)

        return enriched

    async def _generate_detailed_report(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        api_data: Dict[str, Any],
        enriched_data: Dict[str, Any],
        channel: str
    ) -> Dict[str, Any]:
        """Detaylı rapor oluştur"""

        report_id = f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        timestamp = datetime.now().isoformat()

        # LLM ile narrative rapor oluştur
        narrative = await self._generate_narrative_report(
            fault_entity,
            classification,
            api_data,
            enriched_data,
            report_id,
            timestamp,
            channel
        )

        # Yapılandırılmış veri
        structured_data = {
            "report_id": report_id,
            "timestamp": timestamp,
            "channel": channel,
            "status": "NEW",

            # Konum
            "location": {
                "line": fault_entity.line or "Belirtilmedi",
                "station": fault_entity.station or "Belirtilmedi",
                "location_detail": fault_entity.location_detail or "Belirtilmedi",
                "station_details": enriched_data.get("station_details", {})
            },

            # Arıza
            "fault": {
                "equipment_type": fault_entity.equipment or "Belirtilmedi",
                "problem_description": fault_entity.problem_description or "Belirtilmedi",
                "category": classification.fault_category.value,
                "type_id": classification.fault_type_id,
                "type_name": classification.fault_type_name,
                "technical_object_id": classification.technical_object_id,
                "technical_object_name": classification.technical_object_name
            },

            # Öncelik
            "priority": {
                "level": classification.priority.value,
                "reason": classification.priority_reason,
                "sla_hours": classification.sla_hours,
                "estimated_hours": classification.estimated_hours,
                "safety_risk": enriched_data.get("safety_risk", "Düşük"),
                "service_interruption": enriched_data.get("service_interruption", "Yok")
            },

            # Etki
            "impact": {
                "passenger_impact": enriched_data.get("passenger_impact", "Düşük"),
                "accessibility_impact": enriched_data.get("accessibility_impact", "Yok"),
                "alternatives": enriched_data.get("alternatives", []),
                "estimated_affected_passengers": self._estimate_daily_passengers(fault_entity)
            },

            # Yönlendirme
            "routing": {
                "target_department": classification.target_department,
                "sub_department": classification.sub_department,
                "notifications": self._get_notification_list(classification)
            },

            # Aksiyonlar
            "actions": enriched_data.get("recommended_actions", []),

            # Bağlam
            "context": {
                "line_status": enriched_data.get("line_status", {}),
                "similar_faults": enriched_data.get("similar_faults", []),
                "similar_fault_count": enriched_data.get("similar_fault_count", 0),
                "relevant_announcements": enriched_data.get("relevant_announcements", [])
            },

            # Vatandaş yönlendirme
            "citizen_info": {
                "guidance": enriched_data.get("citizen_guidance", ""),
                "estimated_fix_time": f"{classification.estimated_hours} saat"
            },

            # Narrative rapor
            "narrative_report": narrative,

            # Ham API verileri (debug için)
            "raw_api_data": {
                "stations_count": len(api_data.get("stations", [])),
                "faulty_equipments_count": len(api_data.get("faulty_equipments", [])),
                "announcements_count": len(api_data.get("announcements", []))
            }
        }

        return structured_data

    async def _generate_narrative_report(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        api_data: Dict[str, Any],
        enriched_data: Dict[str, Any],
        report_id: str,
        timestamp: str,
        channel: str
    ) -> str:
        """Narrative (anlatı) rapor oluştur"""

        try:
            # Tüm verileri formatlı bir şekilde LLM'e gönder
            prompt_data = {
                "report_id": report_id,
                "timestamp": timestamp,
                "channel": channel,
                "fault_info": fault_entity.model_dump(),
                "classification": classification.model_dump(),
                "enriched": enriched_data
            }

            prompt = self.REPORT_GENERATION_PROMPT.format(
                report_id=report_id,
                timestamp=timestamp,
                status="YENİ",
                priority=classification.priority.value,
                estimated_hours=classification.estimated_hours,
                department=classification.target_department,
                line=fault_entity.line or "Belirtilmedi",
                station=fault_entity.station or "Belirtilmedi",
                location=fault_entity.location_detail or "Belirtilmedi",
                elevator_count=enriched_data.get("elevator_count", "Bilinmiyor"),
                escalator_count=enriched_data.get("escalator_count", "Bilinmiyor"),
                disabled_wc=enriched_data.get("disabled_wc", "Bilinmiyor"),
                baby_room=enriched_data.get("baby_room", "Bilinmiyor"),
                equipment_type=fault_entity.equipment or "Belirtilmedi",
                fault_category=classification.fault_category.value,
                fault_type=classification.fault_type_name,
                technical_object=classification.technical_object_name or "Belirtilmedi",
                problem_description=fault_entity.problem_description or "Belirtilmedi",
                priority_level=classification.priority.value,
                priority_reason=classification.priority_reason,
                sla_hours=classification.sla_hours,
                safety_risk=enriched_data.get("safety_risk", "Düşük"),
                service_interruption=enriched_data.get("service_interruption", "Yok"),
                passenger_impact=enriched_data.get("passenger_impact", "Düşük"),
                accessibility_impact=enriched_data.get("accessibility_impact", "Yok"),
                alternatives=", ".join(enriched_data.get("alternatives", [])),
                affected_area=f"{fault_entity.station} istasyonu {fault_entity.location_detail or ''}",
                daily_passengers=self._estimate_daily_passengers(fault_entity),
                line_status=str(enriched_data.get("line_status", {}).get("Status", "Normal")),
                announcements=str(len(enriched_data.get("relevant_announcements", []))),
                similar_faults=str(enriched_data.get("similar_fault_count", 0)),
                target_department=classification.target_department,
                sub_department=classification.sub_department or "Belirlenmedi",
                notifications="İlgili departmanlara otomatik bildirim gönderildi",
                contacts="Departman koordinatörü",
                action_1=enriched_data.get("recommended_actions", [])[0] if len(enriched_data.get("recommended_actions", [])) > 0 else "Belirlenmedi",
                action_2=enriched_data.get("recommended_actions", [])[1] if len(enriched_data.get("recommended_actions", [])) > 1 else "Belirlenmedi",
                action_3=enriched_data.get("recommended_actions", [])[2] if len(enriched_data.get("recommended_actions", [])) > 2 else "Belirlenmedi",
                action_4=enriched_data.get("recommended_actions", [])[3] if len(enriched_data.get("recommended_actions", [])) > 3 else "Belirlenmedi",
                action_5=enriched_data.get("recommended_actions", [])[4] if len(enriched_data.get("recommended_actions", [])) > 4 else "Belirlenmedi",
                citizen_guidance=enriched_data.get("citizen_guidance", "Alternatif yollar kullanılabilir"),
                estimated_fix_time=f"{classification.estimated_hours} saat",
                technical_data=json.dumps(prompt_data, ensure_ascii=False, indent=2),
                additional_notes="Otomatik oluşturulmuş rapor - İnsan kontrolü önerilir"
            )

            narrative = await self.llm.complete(prompt, temperature=0.3, max_tokens=2000)
            return narrative

        except Exception as e:
            logger.error("Narrative generation failed", error=str(e))
            return self._create_simple_narrative(fault_entity, classification, report_id)

    def _find_station_info(self, station_name: str, stations: List[Dict]) -> Optional[Dict]:
        """İstasyon bilgisini bul"""
        if not station_name:
            return None

        station_name_lower = station_name.lower()
        for station in stations:
            name = str(station.get("Name", "")).lower()
            if station_name_lower in name or name in station_name_lower:
                return station
        return None

    def _find_similar_faults(
        self,
        fault_entity: FaultEntity,
        faulty_equipments: List[Dict]
    ) -> List[Dict]:
        """Benzer arızaları bul"""
        similar = []

        equipment = (fault_entity.equipment or "").lower()

        for fault in faulty_equipments:
            fault_equipment = str(fault.get("EquipmentName", "")).lower()
            fault_type = str(fault.get("FaultType", "")).lower()

            if equipment in fault_equipment or equipment in fault_type:
                similar.append(fault)

        return similar[:5]  # En fazla 5 tane

    def _assess_safety_risk(
        self,
        classification: FaultClassification,
        fault_entity: FaultEntity
    ) -> str:
        """Can güvenliği riskini değerlendir"""
        if classification.priority == Priority.CRITICAL:
            return "YÜKSEK"
        elif "yangın" in (fault_entity.problem_description or "").lower():
            return "YÜKSEK"
        elif "duman" in (fault_entity.problem_description or "").lower():
            return "YÜKSEK"
        elif classification.priority == Priority.HIGH:
            return "ORTA"
        else:
            return "DÜŞÜK"

    def _assess_service_interruption(self, classification: FaultClassification) -> str:
        """Hizmet kesintisini değerlendir"""
        if classification.priority == Priority.CRITICAL:
            return "TAM KESİNTİ"
        elif classification.priority == Priority.HIGH:
            return "KISMI KESİNTİ"
        elif classification.priority == Priority.MEDIUM:
            return "PERFORMANS DÜŞÜKLÜĞÜ"
        else:
            return "MINIMAL ETKİ"

    def _estimate_passenger_impact(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification
    ) -> str:
        """Yolcu etkisini tahmin et"""
        if classification.fault_category.value in ["ESCALATOR", "ELEVATOR"]:
            return "ORTA - Erişilebilirlik etkileniyor"
        elif classification.fault_category.value == "TURNSTILE":
            return "YÜKSEK - Giriş/çıkış etkileniyor"
        elif classification.fault_category.value == "TRAIN":
            return "ÇOK YÜKSEK - Sefer düzeni etkileniyor"
        else:
            return "DÜŞÜK - Konfor etkileniyor"

    def _assess_accessibility_impact(self, fault_entity: FaultEntity) -> str:
        """Erişilebilirlik etkisini değerlendir"""
        equipment = (fault_entity.equipment or "").lower()

        if "asansör" in equipment:
            return "YÜKSEK - Engelli erişimi kesintiye uğramış"
        elif "yürüyen merdiven" in equipment:
            return "ORTA - Alternatif erişim mevcut"
        else:
            return "YOK"

    def _generate_alternatives(
        self,
        fault_entity: FaultEntity,
        enriched_data: Dict[str, Any]
    ) -> List[str]:
        """Alternatif yollar üret"""
        alternatives = []

        equipment = (fault_entity.equipment or "").lower()

        if "asansör" in equipment:
            if enriched_data.get("escalator_count", 0) > 0:
                alternatives.append("Yürüyen merdiven kullanılabilir")
            alternatives.append("Merdiven kullanılabilir")
        elif "yürüyen merdiven" in equipment:
            if enriched_data.get("elevator_count", 0) > 0:
                alternatives.append("Asansör kullanılabilir")
            alternatives.append("Merdiven kullanılabilir")
        elif "turnike" in equipment:
            alternatives.append("Diğer turnikeler kullanılabilir")

        return alternatives

    def _generate_action_plan(
        self,
        classification: FaultClassification,
        fault_entity: FaultEntity
    ) -> List[str]:
        """Aksiyon planı oluştur"""
        actions = []

        # Önceliğe göre aksiyon
        if classification.priority == Priority.CRITICAL:
            actions.append("ACİL - Teknik ekip derhal yönlendirilmeli")
            actions.append("Güvenlik ekibini bilgilendir")
            actions.append("Yolcuları tahliye et (gerekirse)")
        elif classification.priority == Priority.HIGH:
            actions.append("Teknik ekip 1 saat içinde müdahale etmeli")
            actions.append("Alternatif yollar için yönlendirme yapılmalı")
        else:
            actions.append("Normal bakım sürecinde değerlendirilmeli")

        # Ekipman türüne göre
        actions.append(f"{classification.target_department} bilgilendirildi")
        actions.append("Durum takip sistemine kaydedildi")

        # Vatandaş bilgilendirme
        actions.append("Mobil uygulama ve web sitesinde duyuru yapılmalı")

        return actions

    def _generate_citizen_guidance(
        self,
        fault_entity: FaultEntity,
        enriched_data: Dict[str, Any]
    ) -> str:
        """Vatandaş yönlendirme metni oluştur"""
        alternatives = enriched_data.get("alternatives", [])

        if alternatives:
            return f"Alternatif olarak {', '.join(alternatives).lower()}. Lütfen istasyon personelinden yardım isteyebilirsiniz."
        else:
            return "Lütfen istasyon personelinden yardım isteyiniz. En kısa sürede sorun giderilecektir."

    def _get_notification_list(self, classification: FaultClassification) -> List[str]:
        """Bildirilecek kişiler/birimler listesi"""
        notifications = [
            classification.target_department
        ]

        if classification.sub_department:
            notifications.append(classification.sub_department)

        if classification.priority == Priority.CRITICAL:
            notifications.extend([
                "Operasyon Merkezi",
                "Güvenlik Müdürlüğü",
                "Genel Müdürlük"
            ])
        elif classification.priority == Priority.HIGH:
            notifications.append("Operasyon Merkezi")

        return notifications

    def _estimate_daily_passengers(self, fault_entity: FaultEntity) -> str:
        """Günlük yolcu sayısı tahmini"""
        # Basit tahmin - gerçek verilerle güncellenebilir
        station = (fault_entity.station or "").lower()

        # Büyük istasyonlar
        major_stations = ["kadıköy", "taksim", "mecidiyeköy", "atatürk havalimanı", "şişli", "yenikapı"]

        if any(major in station for major in major_stations):
            return "50,000+"
        else:
            return "10,000-30,000"

    def _create_minimal_report(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification
    ) -> Dict[str, Any]:
        """Minimal rapor (hata durumunda fallback)"""
        report_id = f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        return {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "status": "NEW",
            "location": {
                "station": fault_entity.station or "Belirtilmedi",
                "line": fault_entity.line
            },
            "fault": {
                "equipment_type": fault_entity.equipment or "Belirtilmedi",
                "problem_description": fault_entity.problem_description or "Belirtilmedi"
            },
            "priority": {
                "level": classification.priority.value,
                "sla_hours": classification.sla_hours
            },
            "routing": {
                "target_department": classification.target_department
            }
        }

    def _create_simple_narrative(
        self,
        fault_entity: FaultEntity,
        classification: FaultClassification,
        report_id: str
    ) -> str:
        """Basit narrative rapor"""
        return f"""# ARIZA RAPORU #{report_id}

**İstasyon:** {fault_entity.station or 'Belirtilmedi'}
**Hat:** {fault_entity.line or 'Belirtilmedi'}
**Ekipman:** {fault_entity.equipment or 'Belirtilmedi'}
**Sorun:** {fault_entity.problem_description or 'Belirtilmedi'}

**Öncelik:** {classification.priority.value}
**Departman:** {classification.target_department}
**Tahmini Çözüm:** {classification.estimated_hours} saat

Detaylı rapor oluşturulamadı - Manuel kontrol gerekli.
"""
