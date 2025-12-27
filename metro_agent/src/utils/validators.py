#============================================================================
# DOSYA: src/utils/validators.py
# ============================================================================

import re
from typing import Optional, Tuple

from src.utils.data_loader import get_station_aliases

# Hat kodu pattern'leri
LINE_PATTERNS = {
    r"m1a?": "M1A",
    r"m1b?": "M1B",
    r"m2": "M2",
    r"m3": "M3",
    r"m4": "M4",
    r"m5": "M5",
    r"m6": "M6",
    r"m7": "M7",
    r"m8": "M8",
    r"m9": "M9",
    r"m11": "M11",
    r"t1": "T1",
    r"t4": "T4",
    r"t5": "T5",
    r"f1": "F1",
    r"f2": "F2",
    r"marmaray": "MARMARAY",
}


def normalize_station_name(name: str) -> str:
    """İstasyon adını normalize et"""
    if not name:
        return ""

    # Küçük harfe çevir ve boşlukları temizle
    normalized = name.lower().strip()

    # Data dosyasından alias mapping'i al
    station_aliases = get_station_aliases()

    # Alias kontrolü
    if normalized in station_aliases:
        return station_aliases[normalized]

    return normalized


def validate_station_name(name: str, known_stations: list = None) -> Tuple[bool, Optional[str]]:
    """İstasyon adını doğrula"""
    if not name or len(name) < 2:
        return False, None
    
    normalized = normalize_station_name(name)
    
    if known_stations:
        # Bilinen istasyonlarla eşleştir
        for station in known_stations:
            station_lower = station.lower()
            if normalized in station_lower or station_lower in normalized:
                return True, station
    
    return True, normalized


def validate_line_code(code: str) -> Tuple[bool, Optional[str]]:
    """Hat kodunu doğrula"""
    if not code:
        return False, None
    
    code_lower = code.lower().strip()
    
    for pattern, line_code in LINE_PATTERNS.items():
        if re.match(pattern, code_lower):
            return True, line_code
    
    return False, None


def extract_line_from_text(text: str) -> Optional[str]:
    """Metinden hat kodunu çıkar"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    for pattern, line_code in LINE_PATTERNS.items():
        if re.search(pattern, text_lower):
            return line_code
    
    return None


def extract_equipment_type(text: str) -> Optional[str]:
    """Metinden ekipman türünü çıkar"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    equipment_keywords = {
        "yürüyen merdiven": ["yürüyen merdiven", "yuruyen merdiven", "merdiven"],
        "asansör": ["asansör", "asansor", "lift"],
        "turnike": ["turnike", "geçiş", "kart okuyucu"],
        "kapı": ["kapı", "kapi", "door"],
        "klima": ["klima", "havalandırma", "soğutma", "ısıtma"],
        "aydınlatma": ["ışık", "isik", "aydınlatma", "lamba", "karanlık"],
        "anons": ["anons", "hoparlör", "ses", "duyuru"],
        "ekran": ["ekran", "display", "bilgi ekranı", "tabela"],
    }
    
    for equipment, keywords in equipment_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return equipment
    
    return None