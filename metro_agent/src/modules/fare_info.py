# ============================================================================
# DOSYA: src/modules/fare_info.py
# ============================================================================

from typing import Dict, Any

from src.api.metro_api_client import MetroAPIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FareInfoModule:
    """Ücret bilgisi modülü"""
    
    def __init__(self, metro_client: MetroAPIClient):
        self.metro = metro_client
    
    async def get_fare_info(self) -> str:
        """Güncel ücret bilgisi"""
        
        try:
            prices = await self.metro.get_ticket_prices("tr")
            
            if prices:
                # Fiyat listesini formatla
                fare_text = self._format_prices(prices)
                return fare_text
            
            return self._default_fare_info()
            
        except Exception as e:
            logger.error("Fare info error", error=str(e))
            return self._default_fare_info()
    
    def _format_prices(self, prices: list) -> str:
        """Fiyat listesini formatla"""
        
        response = "💳 **Güncel Toplu Taşıma Ücretleri**\n\n"
        
        for price in prices[:10]:  # İlk 10 fiyat
            name = price.get("Name", "")
            amount = price.get("Price", "")
            if name and amount:
                response += f"• {name}: {amount} TL\n"
        
        response += """
📍 **İstanbulkart Yükleme Noktaları:**
• Biletmatikler (metro istasyonları)
• İBB Mobil uygulaması
• PTT şubeleri
• Anlaşmalı bankalar

ℹ️ Öğrenci, 60+ ve engelli indirimleri mevcuttur.

Başka yardımcı olabilir miyim?"""
        
        return response
    
    def _default_fare_info(self) -> str:
        """Varsayılan ücret bilgisi"""
        return """💳 **Toplu Taşıma Ücret Bilgisi**

Güncel ücret tarifesi için:
• 🌐 iett.istanbul
• 📱 Metro İstanbul uygulaması
• 📞 153 İBB Çözüm Merkezi

📍 **İstanbulkart Yükleme:**
• Biletmatikler
• İBB Mobil
• PTT şubeleri

ℹ️ Öğrenci, 60+ ve engelli indirimleri mevcuttur.

Başka yardımcı olabilir miyim?"""
    
    async def handle_query(self, message: str, entities: Dict) -> str:
        """Ücret sorgusu işle"""
        return await self.get_fare_info()

