# ============================================================================
# DOSYA: src/agent/metro_agent.py
# ============================================================================

import time
from typing import Optional, Dict, Any

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.agent.intent_classifier import IntentClassifier
from src.agent.response_formatter import ResponseFormatter
from src.modules.fault_manager import FaultManager
from src.modules.service_status import ServiceStatusModule
from src.modules.direction_helper import DirectionHelper
from src.modules.timetable import TimetableModule
from src.modules.fare_info import FareInfoModule
from src.modules.accessibility import AccessibilityModule
from src.models.report import Intent, IntentType, AgentResponse, UserResponse, InternalReport
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetroAgent:
    """Ana Metro Agent sınıfı"""
    
    GENERAL_SYSTEM_PROMPT = """Sen İBB Metro İstanbul çağrı merkezi asistanısın.
Vatandaşlara yardımcı, profesyonel ve samimi bir şekilde yanıt veriyorsun.

Kurallar:
1. Kısa ve net yanıtlar ver
2. Uygun emoji kullan ama abartma (🚇 ✅ 📍 ⏱️)
3. Takip numarası varsa vurgula
4. Alternatif çözümler sun
5. Her zaman "Başka yardımcı olabilir miyim?" ile bitir
6. Türkçe yanıt ver"""
    
    def __init__(self):
        # API clients
        self.llm = OpenRouterClient()
        self.metro = MetroAPIClient()
        
        # Core components
        self.intent_classifier = IntentClassifier(self.llm)
        self.response_formatter = ResponseFormatter()
        
        # Modules
        self.fault_manager = FaultManager(self.llm, self.metro)
        self.service_status = ServiceStatusModule(self.metro)
        self.direction_helper = DirectionHelper(self.metro, self.llm)
        self.timetable = TimetableModule(self.metro)
        self.fare_info = FareInfoModule(self.metro)
        self.accessibility = AccessibilityModule(self.metro)
        
        logger.info("MetroAgent initialized")
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        channel: str = "api"
    ) -> AgentResponse:
        """
        Kullanıcı mesajını işle
        
        Args:
            message: Kullanıcı mesajı
            user_id: Kullanıcı ID (opsiyonel)
            channel: Kanal (phone, app, web, api)
            
        Returns:
            AgentResponse objesi
        """
        start_time = time.time()
        
        try:
            # 1. Intent sınıflandır
            intent = await self.intent_classifier.classify(message)
            
            logger.info(
                "Intent classified",
                intent=intent.type.value,
                confidence=intent.confidence,
                entities=intent.entities
            )
            
            # 2. Intent'e göre işle
            response_text, internal_report, actions = await self._route_intent(
                message, intent
            )
            
            # 3. Response formatla
            user_response = self.response_formatter.format_response(
                response_text, intent
            )
            
            # 4. Processing time hesapla
            processing_time = int((time.time() - start_time) * 1000)
            
            return AgentResponse(
                user_message=message,
                intent=intent,
                response=user_response,
                internal_report=internal_report,
                actions=actions,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Message processing error", error=str(e))
            
            return AgentResponse(
                user_message=message,
                intent=Intent(type=IntentType.GENERAL_FAQ, confidence=0, entities={}),
                response=self.response_formatter.format_error_response(),
                actions=["log_error"]
            )
    
    async def _route_intent(
        self,
        message: str,
        intent: Intent
    ) -> tuple:
        """Intent'e göre yönlendir"""
        
        entities = intent.entities
        internal_report = None
        actions = ["log_query"]
        
        # FAULT REPORT
        if intent.type == IntentType.FAULT_REPORT:
            response_text, report = await self.fault_manager.handle_fault_report(
                message, entities
            )
            if report:
                internal_report = InternalReport(
                    report_id=report.report_id,
                    intent=intent,
                    entities=entities,
                    actions_taken=["create_ticket", "notify_department"],
                    data=report.model_dump()
                )
                actions = ["create_ticket", "notify_department", "log_call"]
            return response_text, internal_report, actions
        
        # FAULT INQUIRY
        elif intent.type == IntentType.FAULT_INQUIRY:
            existing = await self.fault_manager.check_existing_fault(
                entities.get("station", ""),
                entities.get("equipment", "")
            )
            if existing:
                response_text = f"""🔍 **Arıza Durumu Sorgusu**

{existing.message}

Başka yardımcı olabilir miyim?"""
            else:
                response_text = """Belirttiğiniz konumda kayıtlı bir arıza bulunamadı.

Yeni bir arıza bildirmek ister misiniz?

Başka yardımcı olabilir miyim?"""
            return response_text, None, actions
        
        # SERVICE STATUS
        elif intent.type == IntentType.SERVICE_STATUS:
            response_text = await self.service_status.handle_query(message, entities)
            return response_text, None, actions
        
        # DIRECTION HELP
        elif intent.type == IntentType.DIRECTION_HELP:
            response_text = await self.direction_helper.handle_query(message, entities)
            return response_text, None, actions
        
        # TIMETABLE
        elif intent.type == IntentType.TIMETABLE:
            response_text = await self.timetable.handle_query(message, entities)
            return response_text, None, actions
        
        # FARE INFO
        elif intent.type == IntentType.FARE_INFO:
            response_text = await self.fare_info.handle_query(message, entities)
            return response_text, None, actions
        
        # ACCESSIBILITY
        elif intent.type == IntentType.ACCESSIBILITY:
            response_text = await self.accessibility.handle_query(message, entities)
            return response_text, None, actions
        
        # ANNOUNCEMENTS
        elif intent.type == IntentType.ANNOUNCEMENTS:
            response_text = await self._handle_announcements(entities)
            return response_text, None, actions
        
        # GENERAL FAQ & fallback
        else:
            response_text = await self._handle_general(message, entities)
            return response_text, None, actions
    
    async def _handle_announcements(self, entities: Dict) -> str:
        """Duyuruları işle"""
        try:
            announcements = await self.metro.get_announcements("tr")
            
            if not announcements:
                return """📢 **Duyurular**

Şu an aktif duyuru bulunmamaktadır.

Metro İstanbul uygulaması veya metro.istanbul üzerinden güncel duyuruları takip edebilirsiniz.

Başka yardımcı olabilir miyim?"""
            
            response = "📢 **Güncel Duyurular**\n\n"
            
            for announcement in announcements[:5]:
                title = announcement.get("Title", "")
                if title:
                    response += f"• {title}\n"
            
            response += "\nDetaylar için metro.istanbul adresini ziyaret edebilirsiniz.\n\nBaşka yardımcı olabilir miyim?"
            
            return response
            
        except Exception as e:
            logger.error("Announcements error", error=str(e))
            return """Duyurular yüklenirken bir sorun oluştu.

metro.istanbul adresinden güncel duyuruları kontrol edebilirsiniz.

Başka yardımcı olabilir miyim?"""
    
    async def _handle_general(self, message: str, entities: Dict) -> str:
        """Genel sorular"""
        try:
            # FAQ'dan cevap ara
            faq = await self.metro.get_faq()
            
            message_lower = message.lower()
            for item in faq:
                question = str(item.get("Question", "")).lower()
                if any(word in question for word in message_lower.split() if len(word) > 3):
                    answer = item.get("Answer", "")
                    if answer:
                        return f"""ℹ️ {answer}

Başka yardımcı olabilir miyim?"""
            
            # LLM ile genel yanıt
            prompt = f"""Kullanıcı sorusu: "{message}"

Metro İstanbul ve toplu taşıma ile ilgili kısa ve yardımcı bir yanıt ver.
Eğer soru metro ile ilgili değilse, nazikçe metro hizmetleri hakkında yardımcı olabileceğini belirt.
"Başka yardımcı olabilir miyim?" ile bitir."""
            
            response = await self.llm.complete(
                prompt,
                system_prompt=self.GENERAL_SYSTEM_PROMPT,
                temperature=0.5
            )
            
            return response
            
        except Exception as e:
            logger.error("General query error", error=str(e))
            return """Size nasıl yardımcı olabilirim?

📌 Yapabileceğim işlemler:
• Arıza bildirimi
• Hat durumu sorgulama
• Sefer bilgisi
• Yön tarifi
• Ücret bilgisi
• Erişilebilirlik bilgisi

Başka yardımcı olabilir miyim?"""