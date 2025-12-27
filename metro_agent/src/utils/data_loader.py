
# ============================================================================
# DOSYA: src/utils/data_loader.py
# ============================================================================

import json
from pathlib import Path
from typing import Dict, Any, List
from functools import lru_cache

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


@lru_cache(maxsize=1)
def load_station_mappings() -> Dict[str, Any]:
    """İstasyon alias ve hat mapping verilerini yükle"""

    try:
        file_path = DATA_DIR / "station_mappings.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info("Station mappings loaded",
                   aliases_count=len(data.get("aliases", {})),
                   stations_count=len(data.get("lines", {})))
        return data

    except FileNotFoundError:
        logger.error("Station mappings file not found", path=str(file_path))
        return {"aliases": {}, "lines": {}}

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in station mappings", error=str(e))
        return {"aliases": {}, "lines": {}}


@lru_cache(maxsize=1)
def load_department_routing() -> Dict[str, Any]:
    """Department routing ve SLA verilerini yükle"""

    try:
        file_path = DATA_DIR / "department_routing.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info("Department routing loaded",
                   departments_count=len(data.get("departments", {})),
                   priority_rules_count=len(data.get("priority_rules", [])))
        return data

    except FileNotFoundError:
        logger.error("Department routing file not found", path=str(file_path))
        return {"departments": {}, "priority_rules": []}

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in department routing", error=str(e))
        return {"departments": {}, "priority_rules": []}


@lru_cache(maxsize=1)
def load_intent_examples() -> Dict[str, List[str]]:
    """Intent örneklerini yükle"""

    try:
        file_path = DATA_DIR / "intent_examples.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_examples = sum(len(examples) for examples in data.values())
        logger.info("Intent examples loaded",
                   intent_types=len(data),
                   total_examples=total_examples)
        return data

    except FileNotFoundError:
        logger.error("Intent examples file not found", path=str(file_path))
        return {}

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in intent examples", error=str(e))
        return {}


def get_station_aliases() -> Dict[str, str]:
    """İstasyon alias mapping'ini döndür"""
    data = load_station_mappings()
    return data.get("aliases", {})


def get_station_lines() -> Dict[str, List[str]]:
    """İstasyon hat mapping'ini döndür"""
    data = load_station_mappings()
    return data.get("lines", {})


def get_department_info(equipment_category: str) -> Dict[str, Any]:
    """Ekipman kategorisine göre department bilgisi döndür"""
    data = load_department_routing()
    departments = data.get("departments", {})
    return departments.get(equipment_category, departments.get("OTHER", {}))


def get_sla_hours(equipment_category: str, priority: str) -> float:
    """SLA süresini döndür (saat cinsinden)"""
    dept_info = get_department_info(equipment_category)
    sla_hours = dept_info.get("sla_hours", {})
    return sla_hours.get(priority, 4)  # Default 4 saat


def get_priority_from_description(description: str) -> str:
    """Açıklama metninden priority çıkar"""
    data = load_department_routing()
    priority_rules = data.get("priority_rules", [])

    description_lower = description.lower()

    for rule in priority_rules:
        condition = rule.get("condition", "").lower()
        if condition in description_lower:
            return rule.get("priority", "MEDIUM")

    return "MEDIUM"  # Default priority


def get_intent_examples_for_prompt() -> str:
    """LLM prompt'u için intent örneklerini formatla"""
    examples = load_intent_examples()

    if not examples:
        return ""

    formatted = []
    for intent_type, example_list in examples.items():
        formatted.append(f"\n{intent_type}:")
        for example in example_list[:3]:  # Her intent için ilk 3 örnek
            formatted.append(f"  - \"{example}\"")

    return "\n".join(formatted)


def validate_data_files() -> bool:
    """Tüm data dosyalarının yüklenebilir olduğunu kontrol et"""

    try:
        station_data = load_station_mappings()
        dept_data = load_department_routing()
        intent_data = load_intent_examples()

        # Temel validasyonlar
        assert "aliases" in station_data, "Station mappings 'aliases' anahtarı eksik"
        assert "lines" in station_data, "Station mappings 'lines' anahtarı eksik"
        assert "departments" in dept_data, "Department routing 'departments' anahtarı eksik"
        assert "priority_rules" in dept_data, "Department routing 'priority_rules' anahtarı eksik"
        assert len(intent_data) > 0, "Intent examples boş"

        logger.info("Data validation successful")
        return True

    except AssertionError as e:
        logger.error("Data validation failed", error=str(e))
        return False

    except Exception as e:
        logger.error("Data validation error", error=str(e))
        return False


# Başlangıçta cache'i doldur
def preload_data():
    """Uygulama başlangıcında tüm dataları yükle"""
    load_station_mappings()
    load_department_routing()
    load_intent_examples()
    logger.info("All data files preloaded")
