
# ============================================================================
# DOSYA: tests/test_fault_manager.py
# ============================================================================

import pytest
from unittest.mock import AsyncMock, patch


class TestFaultManager:
    """Fault manager testleri"""
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self):
        """Entity extraction testi"""
        from src.modules.fault_manager import FaultManager
        from src.api.openrouter_client import OpenRouterClient
        from src.api.metro_api_client import MetroAPIClient
        
        mock_llm = AsyncMock(spec=OpenRouterClient)
        mock_llm.complete.return_value = '{"station": "Mecidiyeköy", "equipment": "yürüyen merdiven", "problem_description": "durmuş"}'
        mock_llm.parse_json_response.return_value = {
            "station": "Mecidiyeköy",
            "equipment": "yürüyen merdiven",
            "problem_description": "durmuş"
        }
        
        mock_metro = AsyncMock(spec=MetroAPIClient)
        
        manager = FaultManager(mock_llm, mock_metro)
        
        entities = await manager.extract_entities(
            "Mecidiyeköy istasyonunda yürüyen merdiven durmuş"
        )
        
        assert entities.get("station") == "mecidiyeköy"
        assert entities.get("equipment") == "yürüyen merdiven"
    
    @pytest.mark.asyncio
    async def test_existing_fault_check(self):
        """Mevcut arıza kontrolü testi"""
        from src.modules.fault_manager import FaultManager
        from src.models.fault import FaultEntity
        from src.api.openrouter_client import OpenRouterClient
        from src.api.metro_api_client import MetroAPIClient
        
        mock_llm = AsyncMock(spec=OpenRouterClient)
        mock_metro = AsyncMock(spec=MetroAPIClient)
        mock_metro.get_faulty_equipments.return_value = [
            {
                "Id": 123,
                "StationName": "Levent",
                "EquipmentName": "Yürüyen Merdiven A1",
                "Status": "İşlemde"
            }
        ]
        
        manager = FaultManager(mock_llm, mock_metro)
        
        fault_entity = FaultEntity(
            station="Levent",
            equipment="yürüyen merdiven"
        )
        
        existing = await manager.check_existing_fault(fault_entity)
        
        assert existing is not None
        assert existing.exists == True
        assert existing.fault_id == "123"

