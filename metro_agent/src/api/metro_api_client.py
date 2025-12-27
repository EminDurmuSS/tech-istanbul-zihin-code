
# ============================================================================
# DOSYA: src/api/metro_api_client.py
# ============================================================================

from typing import List, Dict, Any, Optional
import httpx

from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetroAPIClient:
    """Metro İstanbul API İstemcisi"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = None
    ):
        self.base_url = base_url or config.METRO_API_BASE_URL
        self.api_key = api_key or config.METRO_API_KEY
        self.timeout = timeout or config.METRO_API_TIMEOUT
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None
    ) -> Any:
        """
        API isteği yap

        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint
            data: POST data

        Returns:
            API yanıtı
        """
        url = f"{self.base_url}/{endpoint}"

        # API isteği
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, headers=headers, json=data)

                response.raise_for_status()
                result = response.json()

                logger.debug("API request success", endpoint=endpoint)
                return result

        except httpx.HTTPStatusError as e:
            logger.error("Metro API error", endpoint=endpoint, status=e.response.status_code)
            raise
        except httpx.TimeoutException:
            logger.error("Metro API timeout", endpoint=endpoint)
            raise
        except Exception as e:
            logger.error("Metro API request failed", endpoint=endpoint, error=str(e))
            raise
    
    async def _get(self, endpoint: str) -> Any:
        """GET isteği"""
        return await self._request("GET", endpoint)

    async def _post(self, endpoint: str, data: Dict) -> Any:
        """POST isteği"""
        return await self._request("POST", endpoint, data=data)
    
    # =========================================================================
    # HAT & İSTASYON
    # =========================================================================
    
    async def get_lines(self) -> List[Dict]:
        """Tüm hat bilgilerini al"""
        return await self._get("GetLines")
    
    async def get_stations(self) -> List[Dict]:
        """Tüm istasyon bilgilerini al"""
        return await self._get("GetStations")
    
    async def get_stations_by_line(self, line_id: int) -> List[Dict]:
        """Hat ID'sine göre istasyonları al"""
        return await self._get(f"GetStationById/{line_id}")
    
    async def search_line_and_station(self, text: str) -> List[Dict]:
        """Hat ve istasyon ara"""
        return await self._get(f"GetLineAndStationSearch/{text}")
    
    async def get_railway_groups(self) -> List[Dict]:
        """Raylı sistem gruplarını al"""
        return await self._get("GetRailwayGroups")
    
    # =========================================================================
    # HİZMET DURUMU
    # =========================================================================
    
    async def get_service_statuses(self) -> List[Dict]:
        """Hatların hizmet durumunu al"""
        return await self._get("GetServiceStatuses")
    
    # =========================================================================
    # ARIZA YÖNETİMİ
    # =========================================================================
    
    async def get_failure_types(self) -> List[Dict]:
        """Arıza tiplerini al"""
        return await self._get("GetFailureTypes")
    
    async def get_failures_types(self) -> List[Dict]:
        """Arıza türlerini al"""
        return await self._get("GetFailuresTypes")
    
    async def get_technical_object_types(self) -> List[Dict]:
        """Teknik nesne türlerini al"""
        return await self._get("GetTechnicalObjectTypes")
    
    async def get_faulty_equipments(self) -> List[Dict]:
        """Arızalı ekipman listesini al"""
        return await self._get("GetFaultyEquipments")
    
    async def get_fault_details(self, equipment_id: int) -> Dict:
        """Arızalı ekipman detaylarını al"""
        return await self._post(
            "GetFaultyEquipmentDetails",
            {"equipmentId": equipment_id}
        )
    
    # =========================================================================
    # SEFER & TARİFE
    # =========================================================================
    
    async def get_ticket_prices(self, language: str = "tr") -> List[Dict]:
        """Bilet fiyatlarını al"""
        return await self._get(f"GetTicketPrice/{language}")
    
    async def get_timetable(
        self,
        line_id: int,
        station_id: int,
        direction: int
    ) -> Dict:
        """Sefer tarifesini al"""
        return await self._post("GetTimeTable", {
            "LineId": line_id,
            "StationId": station_id,
            "Direction": direction
        })
    
    # =========================================================================
    # YÖN & ROTALAMA
    # =========================================================================
    
    async def get_directions(self) -> List[Dict]:
        """Hat yön bilgilerini al"""
        return await self._get("GetDirections")
    
    async def get_direction_by_line(self, line_id: int) -> List[Dict]:
        """Hat ID'sine göre yön bilgisi al"""
        return await self._get(f"GetDirectionById/{line_id}")
    
    async def get_direction_by_line_and_station(
        self,
        line_id: int,
        station_id: int
    ) -> Dict:
        """Hat ve istasyon ID'sine göre yön bilgisi"""
        return await self._post("GetDirectionsByLineIdAndStationId", {
            "LineId": line_id,
            "StationId": station_id
        })
    
    async def get_station_between_time(
        self,
        line_id: int,
        from_station: int,
        to_station: int
    ) -> Dict:
        """İstasyonlar arası süreyi al"""
        return await self._post("GetStationBetweenTime", {
            "LineId": line_id,
            "FromStationId": from_station,
            "ToStationId": to_station
        })
    
    # =========================================================================
    # DUYURULAR & HABERLER
    # =========================================================================
    
    async def get_announcements(self, language: str = "tr") -> List[Dict]:
        """Duyuruları al"""
        return await self._get(f"GetAnnouncements/{language}")
    
    async def get_announcements_by_line(
        self,
        line_id: int,
        language: str = "tr"
    ) -> List[Dict]:
        """Hat bazlı duyuruları al"""
        return await self._post("GetAnnouncementsByLine", {
            "LineId": line_id,
            "Language": language
        })
    
    async def get_news(self, language: str = "tr") -> List[Dict]:
        """Haberleri al"""
        return await self._get(f"GetNews/{language}")
    
    async def get_activities(self) -> List[Dict]:
        """Etkinlikleri al"""
        return await self._get("GetActivities")
    
    async def get_faq(self) -> List[Dict]:
        """Sıkça sorulan soruları al"""
        return await self._get("FrequentlyAskedQuestions")
    
    # =========================================================================
    # HARİTA & ERİŞİLEBİLİRLİK
    # =========================================================================
    
    async def get_maps(self) -> List[Dict]:
        """Ağ haritası bilgilerini al"""
        return await self._get("GetMaps")
    
    async def get_addresses(self, language: str = "tr") -> List[Dict]:
        """Adres bilgilerini al"""
        return await self._get(f"GetAddresses/{language}")
    
    async def get_line_projects(self) -> List[Dict]:
        """Devam eden projeleri al"""
        return await self._get("GetLineProjects")
    
    # =========================================================================
    # V3 ENDPOINTS
    # =========================================================================
    
    async def get_stations_v3(self) -> List[Dict]:
        """V3: İstasyon ve yön bilgisi"""
        return await self._get("../V3/GetStations")
    
    async def get_equipments(self, station_id: Optional[int] = None) -> List[Dict]:
        """V3: Ekipman listesi"""
        data = {}
        if station_id:
            data["StationId"] = station_id
        return await self._post("../V3/GetEquipments", data)

