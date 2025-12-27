
# ============================================================================
# DOSYA: src/modules/service_status.py
# ============================================================================

from typing import Optional, List, Dict, Any

from src.api.metro_api_client import MetroAPIClient
from src.utils.logger import get_logger
from src.utils.validators import extract_line_from_text

logger = get_logger(__name__)


class ServiceStatusModule:
    """Hizmet durumu modülü"""
    
    STATUS_EMOJIS = {
        "normal": "✅",
        "gecikme": "⚠️",
        "kısmi": "🔶",
        "kapalı": "🔴",
    }
    
    def __init__(self, metro_client: MetroAPIClient):
        self.metro = metro_client
    
    async def get_all_statuses(self) -> str:
        """Tüm hatların durumunu döndür"""
        
        try:
            statuses = await self.metro.get_service_statuses()
            
            if not statuses:
                return "Hizmet durumu bilgisi şu an alınamıyor. Lütfen daha sonra tekrar deneyin."
            
            # Normal ve sorunlu hatları ayır
            normal_lines = []
            problem_lines = []
            
            for status in statuses:
                line_name = status.get("LineName", "Bilinmiyor")
                status_text = status.get("Status", "Bilinmiyor")
                
                if "normal" in status_text.lower():
                    normal_lines.append(line_name)
                else:
                    problem_lines.append(f"{line_name}: {status_text}")
            
            response = "🚇 **Metro Hatları Genel Durumu**\n\n"
            
            if problem_lines:
                response += "⚠️ **Dikkat Gerektiren Hatlar:**\n"
                for line in problem_lines:
                    response += f"• {line}\n"
                response += "\n"
            
            response += f"✅ **Normal Sefer:** {len(normal_lines)}/{len(statuses)} hat\n"
            
            response += "\nBelirli bir hat hakkında detay ister misiniz?"
            
            return response
            
        except Exception as e:
            logger.error("Service status error", error=str(e))
            return "Hizmet durumu bilgisi alınamadı. Lütfen daha sonra tekrar deneyin."
    
    async def get_line_status(self, line: str) -> str:
        """Belirli bir hattın durumunu döndür"""
        
        try:
            statuses = await self.metro.get_service_statuses()
            line_upper = line.upper()
            
            for status in statuses:
                line_name = status.get("LineName", "")
                if line_upper in line_name.upper():
                    status_text = status.get("Status", "Bilinmiyor")
                    
                    emoji = "✅" if "normal" in status_text.lower() else "⚠️"
                    
                    return f"""🚇 **{line_name}** Hizmet Durumu:

{emoji} {status_text}

Başka yardımcı olabilir miyim?"""
            
            return f"'{line}' hattı bulunamadı. Lütfen hat numarasını kontrol edin (M1, M2, M7 vb.)."
            
        except Exception as e:
            logger.error("Line status error", line=line, error=str(e))
            return "Hat durumu bilgisi alınamadı. Lütfen daha sonra tekrar deneyin."
    
    async def handle_query(self, message: str, entities: Dict) -> str:
        """Hizmet durumu sorgusunu işle"""

        line = entities.get("line") or extract_line_from_text(message)

        if line:
            return await self.get_line_status(line)
        else:
            return await self.get_all_statuses()

