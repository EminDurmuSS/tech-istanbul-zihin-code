
# ============================================================================
# DOSYA: src/models/report.py
# ============================================================================

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Intent türleri"""
    FAULT_REPORT = "fault_report"
    FAULT_INQUIRY = "fault_inquiry"
    SERVICE_STATUS = "service_status"
    DIRECTION_HELP = "direction_help"
    TIMETABLE = "timetable"
    FARE_INFO = "fare_info"
    STATION_INFO = "station_info"
    ACCESSIBILITY = "accessibility"
    ANNOUNCEMENTS = "announcements"
    GENERAL_FAQ = "general_faq"


class Intent(BaseModel):
    """Intent sınıflandırma sonucu"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = {}


class UserResponse(BaseModel):
    """Kullanıcıya dönecek yanıt"""
    text: str
    quick_replies: List[str] = []
    attachments: List[Dict[str, Any]] = []


class InternalReport(BaseModel):
    """İç kullanım raporu"""
    report_id: Optional[str] = None
    intent: Intent
    entities: Dict[str, Any] = {}
    actions_taken: List[str] = []
    data: Dict[str, Any] = {}
    created_at: datetime = datetime.now()


class AgentResponse(BaseModel):
    """Agent tam yanıt"""
    user_message: str
    intent: Intent
    response: UserResponse
    internal_report: Optional[InternalReport] = None
    actions: List[str] = []
    processing_time_ms: Optional[int] = None
