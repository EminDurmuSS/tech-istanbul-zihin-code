

# ============================================================================
# DOSYA: src/models/fault.py
# ============================================================================

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class Priority(str, Enum):
    """Arıza öncelik seviyeleri"""
    CRITICAL = "CRITICAL"  # Güvenlik, acil durum
    HIGH = "HIGH"          # Hizmet kesintisi
    MEDIUM = "MEDIUM"      # Ekipman arızası
    LOW = "LOW"            # Minör sorunlar


class FaultType(str, Enum):
    """Arıza tipleri"""
    MECHANICAL = "MECHANICAL"           # Mekanik
    ELECTRICAL = "ELECTRICAL"           # Elektrik
    ELECTRONIC = "ELECTRONIC"           # Elektronik
    SOFTWARE = "SOFTWARE"               # Yazılım
    INFRASTRUCTURE = "INFRASTRUCTURE"   # Altyapı
    OTHER = "OTHER"                     # Diğer


class FaultCategory(str, Enum):
    """Arıza kategorileri"""
    ESCALATOR = "ESCALATOR"             # Yürüyen merdiven
    ELEVATOR = "ELEVATOR"               # Asansör
    TURNSTILE = "TURNSTILE"             # Turnike
    DOOR = "DOOR"                       # Kapı
    LIGHTING = "LIGHTING"               # Aydınlatma
    HVAC = "HVAC"                       # Klima/Havalandırma
    ANNOUNCEMENT = "ANNOUNCEMENT"       # Anons sistemi
    DISPLAY = "DISPLAY"                 # Bilgi ekranları
    SECURITY = "SECURITY"               # Güvenlik sistemleri
    TRAIN = "TRAIN"                     # Tren/vagon
    PLATFORM = "PLATFORM"               # Peron
    OTHER = "OTHER"                     # Diğer


class FaultEntity(BaseModel):
    """Arıza bildirimi entity'leri"""
    station: Optional[str] = None
    line: Optional[str] = None
    equipment: Optional[str] = None
    location_detail: Optional[str] = None
    problem_description: Optional[str] = None
    severity_hint: Optional[str] = None


class FaultClassification(BaseModel):
    """Arıza sınıflandırma sonucu"""
    fault_type_id: str
    fault_type_name: str
    fault_category: FaultCategory
    technical_object_id: Optional[str] = None
    technical_object_name: Optional[str] = None
    priority: Priority
    priority_reason: str
    target_department: str
    sub_department: Optional[str] = None
    estimated_hours: int = 4
    sla_hours: int = 4


class FaultEnrichment(BaseModel):
    """Arıza zenginleştirme verileri"""
    station_info: Optional[Dict[str, Any]] = None
    line_info: Optional[Dict[str, Any]] = None
    line_status: Optional[Dict[str, Any]] = None
    equipment_info: Optional[Dict[str, Any]] = None
    passenger_stats: Optional[Dict[str, Any]] = None
    alternatives: List[str] = []
    similar_faults: List[Dict[str, Any]] = []
    related_announcements: List[Dict[str, Any]] = []
    accessibility_impact: Optional[str] = None


class FaultReport(BaseModel):
    """Tam arıza raporu"""
    report_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    channel: str = "phone"
    
    # Konum bilgileri
    station: str
    line: Optional[str] = None
    location_detail: Optional[str] = None
    
    # Arıza bilgileri
    equipment_type: str
    fault_description: str
    
    # Sınıflandırma
    classification: FaultClassification
    
    # Zenginleştirme
    enrichment: Optional[FaultEnrichment] = None
    
    # Yönlendirme
    target_department: str
    estimated_resolution: str
    
    # Durum
    status: str = "NEW"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExistingFault(BaseModel):
    """Mevcut arıza bilgisi"""
    exists: bool = True
    fault_id: str
    station: Optional[str] = "Belirtilmemiş"
    equipment: Optional[str] = "Belirtilmemiş"
    status: str = "Bilinmiyor"
    created_at: Optional[str] = None
    estimated_resolution: Optional[str] = None
    message: str = "Bu arıza sistemimizde kayıtlı."
