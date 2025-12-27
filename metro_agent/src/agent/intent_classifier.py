
# ============================================================================
# DOSYA: src/agent/intent_classifier.py
# ============================================================================

import json
from typing import Dict, Any

from src.api.openrouter_client import OpenRouterClient
from src.models.report import Intent, IntentType
from src.utils.logger import get_logger
from src.utils.data_loader import get_intent_examples_for_prompt

logger = get_logger(__name__)


class IntentClassifier:
    """LLM tabanlı intent sınıflandırıcı"""

    @staticmethod
    def _build_system_prompt() -> str:
        """Intent examples ile sistem promptunu oluştur"""
        examples = get_intent_examples_for_prompt()

        base_prompt = """Sen İBB Metro İstanbul çağrı merkezi asistanısın.
Kullanıcı mesajlarını analiz edip intent'lerini ve entity'lerini belirliyorsun.

Intent türleri:
- fault_report: Kullanıcı bir arıza bildiriyor (bozuk, çalışmıyor, arızalı, kırık)
- fault_inquiry: Mevcut bir arızayı sorguluyor (arıza var mı, düzeldi mi, ne oldu)
- service_status: Hat/istasyon çalışıyor mu sorusu (sefer var mı, açık mı)
- direction_help: Nasıl giderim, hangi yön, aktarma soruları
- timetable: Sefer saatleri, ilk/son sefer, kaç dakikada bir
- fare_info: Ücret, bilet fiyatı, kart yükleme soruları
- station_info: İstasyon adresi, çıkışlar, nerede
- accessibility: Engelli erişimi, asansör, şarj noktası
- announcements: Duyurular, bakım bilgisi, ne zaman açılacak
- general_faq: Diğer genel sorular"""

        if examples:
            base_prompt += f"\n\nÖrnek kullanıcı mesajları:{examples}"

        base_prompt += """

Çıkarılacak entity'ler (sadece metinde geçenleri çıkar):
- station: İstasyon adı
- line: Hat adı/numarası (M1, M2, M7, T1 vb.)
- equipment: Ekipman türü (asansör, yürüyen merdiven, turnike, kapı, klima, ışık, anons, ekran)
- location_detail: Konum detayı (giriş, çıkış, peron, platform)
- destination: Varış noktası (yön sorularında)
- time_context: Zaman bağlamı (şu an, yarın, akşam, hafta sonu)
- problem_description: Sorun açıklaması (arıza için)

ÖNEMLİ: Metinde açıkça belirtilmeyen entity'leri null yap.

SADECE aşağıdaki JSON formatında yanıt ver, başka bir şey yazma:
{
    "intent": "intent_type",
    "confidence": 0.0-1.0,
    "entities": {
        "station": "...",
        "line": "...",
        "equipment": "...",
        "location_detail": "...",
        "destination": "...",
        "time_context": "...",
        "problem_description": "..."
    }
}"""
        return base_prompt
    
    # Keyword-based fallback patterns
    INTENT_KEYWORDS = {
        IntentType.FAULT_REPORT: [
            "arıza", "bozuk", "çalışmıyor", "kırık", "hasarlı", "sorun var",
            "durmuş", "çalışmıyor", "arızalı", "bozulmuş"
        ],
        IntentType.FAULT_INQUIRY: [
            "arıza var mı", "sorun var mı", "düzeldi mi", "tamir edildi mi",
            "ne zaman düzelir", "hala bozuk mu"
        ],
        IntentType.SERVICE_STATUS: [
            "çalışıyor mu", "sefer var mı", "açık mı", "kapalı mı",
            "normal mi", "durum"
        ],
        IntentType.DIRECTION_HELP: [
            "nasıl giderim", "nasıl ulaşırım", "hangi yön", "nerede inmeli",
            "aktarma", "rota", "yol", "ulaşım"
        ],
        IntentType.TIMETABLE: [
            "saat kaçta", "ilk sefer", "son sefer", "kaç dakikada",
            "sefer aralığı", "ne zaman", "tarife"
        ],
        IntentType.FARE_INFO: [
            "fiyat", "ücret", "kaç tl", "kaç lira", "bilet", "istanbulkart",
            "yükleme", "bakiye"
        ],
        IntentType.STATION_INFO: [
            "istasyon", "adres", "nerede", "çıkış", "giriş", "konum"
        ],
        IntentType.ACCESSIBILITY: [
            "engelli", "tekerlekli sandalye", "asansör var mı", "şarj noktası",
            "erişim", "wheelchair"
        ],
        IntentType.ANNOUNCEMENTS: [
            "duyuru", "bakım", "yenilik", "açılış", "ne zaman açılacak",
            "proje", "inşaat"
        ],
    }
    
    def __init__(self, llm_client: OpenRouterClient):
        self.llm = llm_client
        self.system_prompt = self._build_system_prompt()

    async def classify(self, message: str) -> Intent:
        """
        Kullanıcı mesajını sınıflandır

        Args:
            message: Kullanıcı mesajı

        Returns:
            Intent objesi
        """
        try:
            # LLM ile sınıflandır
            response = await self.llm.complete(
                prompt=f"Mesaj: {message}",
                system_prompt=self.system_prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            data = await self.llm.parse_json_response(response)
            
            if data and "intent" in data:
                intent_type = self._parse_intent_type(data["intent"])
                
                # Entity'leri temizle (null olanları kaldır)
                entities = {
                    k: v for k, v in data.get("entities", {}).items()
                    if v is not None and v != "null" and v != ""
                }
                
                return Intent(
                    type=intent_type,
                    confidence=float(data.get("confidence", 0.8)),
                    entities=entities
                )
            
            # Fallback
            return self._keyword_classify(message)
            
        except Exception as e:
            logger.warning("LLM classification failed", error=str(e))
            return self._keyword_classify(message)
    
    def _parse_intent_type(self, intent_str: str) -> IntentType:
        """Intent string'i enum'a çevir"""
        try:
            return IntentType(intent_str.lower())
        except ValueError:
            return IntentType.GENERAL_FAQ
    
    def _keyword_classify(self, message: str) -> Intent:
        """Keyword tabanlı fallback sınıflandırma"""
        
        message_lower = message.lower()
        
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return Intent(
                        type=intent_type,
                        confidence=0.6,
                        entities=self._extract_basic_entities(message)
                    )
        
        return Intent(
            type=IntentType.GENERAL_FAQ,
            confidence=0.5,
            entities={}
        )
    
    def _extract_basic_entities(self, message: str) -> Dict[str, Any]:
        """Basit entity extraction"""
        entities = {}
        message_lower = message.lower()
        
        # Hat tespiti
        import re
        line_match = re.search(r'm\d+[ab]?|t\d+|f\d+', message_lower)
        if line_match:
            entities["line"] = line_match.group().upper()
        
        # Ekipman tespiti
        equipment_keywords = {
            "yürüyen merdiven": "yürüyen merdiven",
            "merdiven": "yürüyen merdiven",
            "asansör": "asansör",
            "turnike": "turnike",
            "kapı": "kapı",
            "klima": "klima",
            "ışık": "aydınlatma",
            "anons": "anons sistemi",
        }
        
        for keyword, equipment in equipment_keywords.items():
            if keyword in message_lower:
                entities["equipment"] = equipment
                break
        
        return entities
