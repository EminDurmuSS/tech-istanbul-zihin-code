# ============================================================================
# DOSYA: src/models/conversation_state.py
# ============================================================================

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ConversationPhase(str, Enum):
    """Konuşma aşamaları"""
    INITIAL_REPORT = "initial_report"
    COLLECTING_STATION = "collecting_station"
    COLLECTING_LOCATION_DETAIL = "collecting_location_detail"
    COLLECTING_EQUIPMENT = "collecting_equipment"
    COLLECTING_PROBLEM_DETAIL = "collecting_problem_detail"
    CONFIRMING = "confirming"
    COMPLETED = "completed"


class FaultReportState(BaseModel):
    """Arıza bildirimi konuşma durumu"""
    phase: ConversationPhase = ConversationPhase.INITIAL_REPORT

    # Toplanan bilgiler
    station: Optional[str] = None
    station_id: Optional[int] = None
    line: Optional[str] = None
    line_id: Optional[int] = None
    location_detail: Optional[str] = None
    equipment: Optional[str] = None
    equipment_type_normalized: Optional[str] = None
    problem_description: Optional[str] = None
    severity_hint: Optional[str] = None

    # Zenginleştirilmiş veriler
    station_info: Optional[Dict[str, Any]] = None
    line_info: Optional[Dict[str, Any]] = None
    equipment_info: Optional[Dict[str, Any]] = None

    # Metadata
    created_at: datetime = datetime.now()
    last_updated: datetime = datetime.now()
    messages: List[str] = []

    def is_complete(self) -> bool:
        """Tüm gerekli bilgiler toplandı mı?"""
        return all([
            self.station,
            self.location_detail,
            self.equipment,
            self.problem_description
        ])

    def get_missing_fields(self) -> List[str]:
        """Eksik alanları döndür"""
        missing = []
        if not self.station:
            missing.append("station")
        if not self.location_detail:
            missing.append("location_detail")
        if not self.equipment:
            missing.append("equipment")
        if not self.problem_description:
            missing.append("problem_description")
        return missing

    def update_timestamp(self):
        """Son güncelleme zamanını güncelle"""
        self.last_updated = datetime.now()
