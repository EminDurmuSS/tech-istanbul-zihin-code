
# ============================================================================
# DOSYA: src/models/station.py
# ============================================================================

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class Station(BaseModel):
    """İstasyon modeli"""
    id: int
    name: str
    name_en: Optional[str] = None
    line_id: int
    line_name: Optional[str] = None
    order: int = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_transfer: bool = False
    transfer_lines: List[str] = []
    facilities: List[str] = []


class Line(BaseModel):
    """Hat modeli"""
    id: int
    name: str
    name_en: Optional[str] = None
    code: str  # M1, M2, M7 etc.
    color: Optional[str] = None
    stations: List[Station] = []
    is_active: bool = True
    start_station: Optional[str] = None
    end_station: Optional[str] = None


class Direction(BaseModel):
    """Yön bilgisi"""
    line_id: int
    direction_value: int  # 1: pozitif, 2: negatif
    direction_name: str
    terminal_station: str


class StationInfo(BaseModel):
    """Detaylı istasyon bilgisi"""
    station: Station
    directions: List[Direction] = []
    exits: List[Dict[str, Any]] = []
    facilities: Dict[str, Any] = {}
    accessibility: Dict[str, Any] = {}
    nearby_places: List[str] = []
