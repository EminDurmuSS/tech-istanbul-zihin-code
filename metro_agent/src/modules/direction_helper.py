
# ============================================================================
# DOSYA: src/modules/direction_helper.py
# ============================================================================

from typing import Optional, Dict, Any, List

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DirectionHelper:
    """Yön buldurma modülü"""
    
    DIRECTION_PROMPT = """Kullanıcı İstanbul metrosunda yol tarifi istiyor.

Başlangıç: {start}
Hedef: {destination}

Mevcut metro hatları ve istasyonları:
{lines_info}

Kısa ve net bir yol tarifi ver. Aktarma gerekiyorsa belirt.
Format:
1. Hangi istasyondan hangi hatta binilecek
2. Hangi yöne gidilecek
3. Nerede inilecek / aktarma yapılacak
4. Tahmini süre (varsa)

Türkçe yanıt ver:"""
    
    def __init__(
        self,
        metro_client: MetroAPIClient,
        llm_client: Optional[OpenRouterClient] = None
    ):
        self.metro = metro_client
        self.llm = llm_client
    
    async def get_directions(
        self,
        start: str,
        destination: str
    ) -> str:
        """Yön tarifi al"""
        
        try:
            # Basit durumlar için statik yanıt
            if not self.llm:
                return self._basic_direction_response(start, destination)
            
            # LLM ile yön tarifi
            lines = await self.metro.get_lines()
            stations = await self.metro.get_stations()
            
            lines_info = self._format_lines_info(lines, stations)
            
            prompt = self.DIRECTION_PROMPT.format(
                start=start,
                destination=destination,
                lines_info=lines_info
            )
            
            response = await self.llm.complete(prompt, temperature=0.3)
            
            return f"""🚇 **{start} → {destination}** Rotası:

{response}

📱 Detaylı rota için Metro İstanbul uygulamasını kullanabilirsiniz.

Başka yardımcı olabilir miyim?"""
            
        except Exception as e:
            logger.error("Direction error", error=str(e))
            return self._basic_direction_response(start, destination)
    
    def _basic_direction_response(self, start: str, destination: str) -> str:
        """Basit yön yanıtı"""
        return f"""🚇 **{start} → {destination}** için yol tarifi:

En doğru rota için Metro İstanbul uygulamasındaki "Nasıl Giderim?" özelliğini kullanmanızı öneririm.

📱 Uygulama: Metro Istanbul (App Store / Play Store)
🌐 Web: metro.istanbul

Başka yardımcı olabilir miyim?"""
    
    def _format_lines_info(self, lines: List, stations: List) -> str:
        """Hat bilgilerini formatla"""
        info = []
        for line in lines[:10]:  # İlk 10 hat
            name = line.get("Name", "")
            info.append(f"- {name}")
        return "\n".join(info)
    
    async def handle_query(self, message: str, entities: Dict) -> str:
        """Yön sorgusunu işle"""
        
        station = entities.get("station", "")
        destination = entities.get("destination", "")
        
        if not station or not destination:
            return """Yön bulmak için nereden nereye gideceğinizi belirtir misiniz?

Örnek: "Taksim'den Kadıköy'e nasıl giderim?"

Başka yardımcı olabilir miyim?"""
        
        return await self.get_directions(station, destination)

