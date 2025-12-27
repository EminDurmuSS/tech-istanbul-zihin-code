
# ============================================================================
# DOSYA: src/api/openrouter_client.py
# ============================================================================

import json
from typing import Optional, Dict, Any, List
import httpx

from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """OpenRouter API üzerinden LLM erişimi"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.model = model or config.LLM_MODEL
        self.base_url = base_url or config.OPENROUTER_BASE_URL
        
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        LLM completion çağrısı
        
        Args:
            prompt: Kullanıcı prompt'u
            system_prompt: Sistem prompt'u
            temperature: Yaratıcılık seviyesi (0.0-1.0)
            max_tokens: Maksimum token sayısı
            stop: Durma dizileri
            
        Returns:
            LLM yanıtı
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Chat completion çağrısı
        
        Args:
            messages: Mesaj listesi
            temperature: Yaratıcılık seviyesi
            max_tokens: Maksimum token
            stop: Durma dizileri
            
        Returns:
            LLM yanıtı
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or config.LLM_TEMPERATURE,
            "max_tokens": max_tokens or config.LLM_MAX_TOKENS,
        }
        
        if stop:
            payload["stop"] = stop
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://ibb.istanbul",
            "X-Title": config.APP_NAME,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                
                logger.debug(
                    "LLM completion",
                    model=self.model,
                    prompt_tokens=data.get("usage", {}).get("prompt_tokens"),
                    completion_tokens=data.get("usage", {}).get("completion_tokens")
                )
                
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error("OpenRouter API error", status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("OpenRouter request failed", error=str(e))
            raise
    
    async def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        LLM yanıtından JSON parse et
        
        Args:
            response: LLM yanıtı
            
        Returns:
            Parsed JSON
        """
        # Markdown code block temizle
        clean = response.strip()
        
        if clean.startswith("```"):
            lines = clean.split("\n")
            # İlk ve son satırı kaldır
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            clean = "\n".join(lines)
        
        # JSON başlangıcını bul
        json_start = clean.find("{")
        json_end = clean.rfind("}") + 1
        
        if json_start != -1 and json_end > json_start:
            clean = clean[json_start:json_end]
        
        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            logger.warning("JSON parse failed", response=response[:200], error=str(e))
            return {}
