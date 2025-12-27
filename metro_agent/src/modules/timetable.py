# ============================================================================
# DOSYA: src/modules/timetable.py
# ============================================================================

from typing import Dict, Any, Optional

from src.api.metro_api_client import MetroAPIClient
from src.utils.logger import get_logger
from src.utils.validators import extract_line_from_text

logger = get_logger(__name__)


class TimetableModule:
    """Sefer tarifesi modülü"""
    
    # Genel çalışma saatleri (güncel bilgi için API kullanılmalı)
    DEFAULT_HOURS = {
        "weekday": {"first": "06:00", "last": "00:00"},
        "weekend": {"first": "06:30", "last": "00:00"},
    }
    
    def __init__(self, metro_client: MetroAPIClient):
        self.metro = metro_client
    
    async def get_general_info(self) -> str:
        """Genel sefer bilgisi"""
        return """⏱️ **Metro Sefer Bilgileri**

🕕 **Çalışma Saatleri:**
- Hafta içi: 06:00 - 00:00
- Hafta sonu: 06:30 - 00:00

⏰ **Sefer Aralıkları:**
- Zirve saatler (07:30-09:30, 17:00-19:30): 2-4 dakika
- Normal saatler: 4-8 dakika
- Gece saatleri: 8-12 dakika

📱 Anlık sefer bilgisi için Metro İstanbul uygulamasını kullanabilirsiniz.

Belirli bir hat veya istasyon için bilgi ister misiniz?"""
    
    async def get_line_timetable(self, line: str, station: Optional[str] = None) -> str:
        """Hat bazlı sefer tarifesi"""
        
        try:
            # TODO: API'den detaylı bilgi çek
            
            return f"""⏱️ **{line.upper()} Hattı Sefer Bilgileri**

🕕 **Çalışma Saatleri:**
- İlk sefer: 06:00
- Son sefer: 00:00

⏰ **Ortalama Sefer Aralığı:**
- Zirve: 3-5 dakika
- Normal: 5-8 dakika

📍 Belirli bir istasyon için daha detaylı bilgi verebilirim.

Başka yardımcı olabilir miyim?"""
            
        except Exception as e:
            logger.error("Timetable error", line=line, error=str(e))
            return await self.get_general_info()
    
    async def handle_query(self, message: str, entities: Dict) -> str:
        """Sefer sorgusu işle"""
        
        line = entities.get("line") or extract_line_from_text(message)
        station = entities.get("station")
        
        if line:
            return await self.get_line_timetable(line, station)
        else:
            return await self.get_general_info()

