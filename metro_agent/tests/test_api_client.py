

# ============================================================================
# DOSYA: tests/test_api_client.py
# ============================================================================

import pytest
from unittest.mock import AsyncMock, patch
import httpx


class TestMetroAPIClient:
    """Metro API client testleri"""
    
    @pytest.mark.asyncio
    async def test_get_lines(self):
        """Hat listesi testi"""
        from src.api.metro_api_client import MetroAPIClient
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = [
                {"Id": 1, "Name": "M1A"},
                {"Id": 2, "Name": "M2"}
            ]
            mock_response.raise_for_status = lambda: None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            client = MetroAPIClient()

            lines = await client.get_lines()
            
            assert len(lines) == 2
            assert lines[0]["Name"] == "M1A"
    
    @pytest.mark.asyncio
    async def test_get_service_statuses(self):
        """Hizmet durumu testi"""
        from src.api.metro_api_client import MetroAPIClient
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = [
                {"LineName": "M7", "Status": "Normal Sefer"}
            ]
            mock_response.raise_for_status = lambda: None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            client = MetroAPIClient()

            statuses = await client.get_service_statuses()
            
            assert len(statuses) == 1
            assert statuses[0]["LineName"] == "M7"


class TestOpenRouterClient:
    """OpenRouter client testleri"""
    
    @pytest.mark.asyncio
    async def test_complete(self):
        """LLM completion testi"""
        from src.api.openrouter_client import OpenRouterClient
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [
                    {"message": {"content": "Test response"}}
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5}
            }
            mock_response.raise_for_status = lambda: None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance
            
            client = OpenRouterClient()
            response = await client.complete("Test prompt")
            
            assert response == "Test response"
