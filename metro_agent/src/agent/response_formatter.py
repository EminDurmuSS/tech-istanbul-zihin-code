
# ============================================================================
# DOSYA: src/agent/response_formatter.py
# ============================================================================

from typing import Optional, Dict, Any, List

from src.models.report import UserResponse, Intent, IntentType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """Yanıt formatlayıcı"""
    
    # Intent bazlı emoji mapping
    INTENT_EMOJIS = {
        IntentType.FAULT_REPORT: "🔧",
        IntentType.FAULT_INQUIRY: "🔍",
        IntentType.SERVICE_STATUS: "🚇",
        IntentType.DIRECTION_HELP: "🗺️",
        IntentType.TIMETABLE: "⏱️",
        IntentType.FARE_INFO: "💳",
        IntentType.STATION_INFO: "📍",
        IntentType.ACCESSIBILITY: "♿",
        IntentType.ANNOUNCEMENTS: "📢",
        IntentType.GENERAL_FAQ: "ℹ️",
    }
    
    # Quick reply önerileri
    QUICK_REPLIES = {
        IntentType.FAULT_REPORT: [
            "Başka bir sorun var",
            "Takip numarası sorgula",
            "Ana menü"
        ],
        IntentType.SERVICE_STATUS: [
            "Başka hat sorgula",
            "Tüm hatlar",
            "Duyurular"
        ],
        IntentType.DIRECTION_HELP: [
            "Alternatif rota",
            "Sefer saatleri",
            "Hat durumu"
        ],
        IntentType.GENERAL_FAQ: [
            "Arıza bildir",
            "Hat durumu",
            "Sefer saatleri",
            "Ücret bilgisi"
        ],
    }
    
    def format_response(
        self,
        text: str,
        intent: Intent,
        include_quick_replies: bool = True
    ) -> UserResponse:
        """
        Yanıtı formatla
        
        Args:
            text: Yanıt metni
            intent: Intent bilgisi
            include_quick_replies: Quick reply ekle
            
        Returns:
            UserResponse objesi
        """
        quick_replies = []
        
        if include_quick_replies:
            quick_replies = self.QUICK_REPLIES.get(
                intent.type,
                self.QUICK_REPLIES[IntentType.GENERAL_FAQ]
            )
        
        return UserResponse(
            text=text,
            quick_replies=quick_replies,
            attachments=[]
        )
    
    def format_error_response(self, error_type: str = "general") -> UserResponse:
        """Hata yanıtı"""
        
        messages = {
            "general": "Bir hata oluştu. Lütfen tekrar deneyin.",
            "api": "Servis şu an yanıt vermiyor. Birkaç dakika sonra tekrar deneyin.",
            "not_found": "İstediğiniz bilgi bulunamadı.",
            "invalid": "Geçersiz istek. Lütfen farklı bir şekilde sorun.",
        }
        
        return UserResponse(
            text=messages.get(error_type, messages["general"]),
            quick_replies=["Tekrar dene", "Ana menü", "Operatör"]
        )
    
    def add_footer(self, text: str) -> str:
        """Standart footer ekle"""
        if "Başka yardımcı olabilir miyim?" not in text:
            text += "\n\nBaşka yardımcı olabilir miyim?"
        return text

