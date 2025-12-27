
# ============================================================================
# DOSYA: src/modules/accessibility.py
# ============================================================================

from typing import Dict, Any, Optional

from src.api.metro_api_client import MetroAPIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AccessibilityModule:
    """Erişilebilirlik modülü"""
    
    def __init__(self, metro_client: MetroAPIClient):
        self.metro = metro_client
    
    async def get_accessibility_info(self, station: Optional[str] = None) -> str:
        """Erişilebilirlik bilgisi"""
        
        if station:
            return await self.get_station_accessibility(station)
        
        return self._general_accessibility_info()
    
    async def get_station_accessibility(self, station: str) -> str:
        """İstasyon erişilebilirlik bilgisi"""
        
        try:
            # İstasyon bilgisini al
            stations = await self.metro.get_stations()
            
            for s in stations:
                if station.lower() in str(s.get("Name", "")).lower():
                    # TODO: Detaylı erişilebilirlik bilgisi
                    return f"""♿ **{s.get('Name')} İstasyonu Erişilebilirlik**

✅ **Mevcut Olanaklar:**
• Asansör
• Yürüyen merdiven
• Engelli tuvaleti
• Sesli anons sistemi
• Kabartma harita

📍 Engelli şarj noktaları için istasyon personeline başvurabilirsiniz.

Daha fazla bilgi için istasyon görevlilerimiz yardımcı olabilir.

Başka yardımcı olabilir miyim?"""
            
            return f"'{station}' istasyonu bulunamadı. Lütfen istasyon adını kontrol edin."
            
        except Exception as e:
            logger.error("Accessibility error", station=station, error=str(e))
            return self._general_accessibility_info()
    
    def _general_accessibility_info(self) -> str:
        """Genel erişilebilirlik bilgisi"""
        return """♿ **Metro Erişilebilirlik Hizmetleri**

✅ **Tüm İstasyonlarda:**
• Asansör
• Yürüyen merdiven
• Engelli tuvaleti
• Sesli anons sistemi

🔋 **Engelli Şarj Noktaları:**
Birçok istasyonda elektrikli tekerlekli sandalye şarj noktaları mevcuttur.

📞 **Yardım:**
• İstasyon personeli
• 153 İBB Çözüm Merkezi

Belirli bir istasyon hakkında bilgi almak ister misiniz?"""
    
    async def handle_query(self, message: str, entities: Dict) -> str:
        """Erişilebilirlik sorgusu işle"""
        
        station = entities.get("station")
        return await self.get_accessibility_info(station)
