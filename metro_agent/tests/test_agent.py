
# ============================================================================
# DOSYA: tests/test_agent.py
# ============================================================================

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Test için mock config
import os
os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["LLM_MODEL"] = "test-model"


class TestIntentClassifier:
    """Intent classifier testleri"""
    
    @pytest.mark.asyncio
    async def test_fault_report_classification(self):
        """Arıza bildirimi intent testi"""
        from src.agent.intent_classifier import IntentClassifier
        from src.api.openrouter_client import OpenRouterClient
        from src.models.report import IntentType
        
        # Mock LLM client
        mock_llm = AsyncMock(spec=OpenRouterClient)
        mock_llm.complete.return_value = '{"intent": "fault_report", "confidence": 0.95, "entities": {"station": "Levent", "equipment": "yürüyen merdiven"}}'
        mock_llm.parse_json_response.return_value = {
            "intent": "fault_report",
            "confidence": 0.95,
            "entities": {"station": "Levent", "equipment": "yürüyen merdiven"}
        }
        
        classifier = IntentClassifier(mock_llm)
        
        intent = await classifier.classify("Levent istasyonunda yürüyen merdiven bozuk")
        
        assert intent.type == IntentType.FAULT_REPORT
        assert intent.confidence >= 0.9
        assert "station" in intent.entities
    
    @pytest.mark.asyncio
    async def test_service_status_classification(self):
        """Hizmet durumu intent testi"""
        from src.agent.intent_classifier import IntentClassifier
        from src.api.openrouter_client import OpenRouterClient
        from src.models.report import IntentType
        
        mock_llm = AsyncMock(spec=OpenRouterClient)
        mock_llm.complete.return_value = '{"intent": "service_status", "confidence": 0.9, "entities": {"line": "M2"}}'
        mock_llm.parse_json_response.return_value = {
            "intent": "service_status",
            "confidence": 0.9,
            "entities": {"line": "M2"}
        }
        
        classifier = IntentClassifier(mock_llm)
        
        intent = await classifier.classify("M2 çalışıyor mu?")
        
        assert intent.type == IntentType.SERVICE_STATUS
    
    @pytest.mark.asyncio
    async def test_keyword_fallback(self):
        """Keyword fallback testi"""
        from src.agent.intent_classifier import IntentClassifier
        from src.api.openrouter_client import OpenRouterClient
        from src.models.report import IntentType
        
        mock_llm = AsyncMock(spec=OpenRouterClient)
        mock_llm.complete.side_effect = Exception("LLM error")
        
        classifier = IntentClassifier(mock_llm)
        
        intent = await classifier.classify("arıza var asansör bozuk")
        
        # Fallback çalışmalı
        assert intent.type == IntentType.FAULT_REPORT
        assert intent.confidence < 0.7  # Fallback düşük confidence


class TestMetroAgent:
    """Metro agent testleri"""
    
    @pytest.mark.asyncio
    async def test_process_message(self):
        """Mesaj işleme testi"""
        from src.agent.metro_agent import MetroAgent
        from src.models.report import IntentType
        
        with patch('src.agent.metro_agent.OpenRouterClient') as mock_llm_class, \
             patch('src.agent.metro_agent.MetroAPIClient') as mock_metro_class:
            
            # Mock setup
            mock_llm = AsyncMock()
            mock_llm.complete.return_value = '{"intent": "service_status", "confidence": 0.9, "entities": {"line": "M7"}}'
            mock_llm.parse_json_response.return_value = {
                "intent": "service_status",
                "confidence": 0.9,
                "entities": {"line": "M7"}
            }
            mock_llm_class.return_value = mock_llm
            
            mock_metro = AsyncMock()
            mock_metro.get_service_statuses.return_value = [
                {"LineName": "M7", "Status": "Normal Sefer"}
            ]
            mock_metro_class.return_value = mock_metro
            
            agent = MetroAgent()
            response = await agent.process_message("M7 çalışıyor mu?")
            
            assert response is not None
            assert "M7" in response.response.text or "normal" in response.response.text.lower()
