
# ============================================================================
# DOSYA: src/api/metro_api_client.py
# ============================================================================

from typing import List, Dict, Any, Optional
import httpx
import asyncio

from src.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetroAPIClient:
    """Metro İstanbul API İstemcisi"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = None,
        max_retries: int = 3
    ):
        self.base_url = base_url or config.METRO_API_BASE_URL
        self.api_key = api_key or config.METRO_API_KEY
        self.timeout = timeout or config.METRO_API_TIMEOUT
        self.max_retries = max_retries

        # Known problematic endpoints that should be handled gracefully
        self.problematic_endpoints = {
            "GetAnnouncementsByLine": "Hat duyuruları şu anda alınamıyor"
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Any:
        """
        API isteği yap (with retry logic)

        Args:
            method: HTTP method (GET/POST)
            endpoint: API endpoint
            data: POST data
            retry_count: Current retry attempt

        Returns:
            API yanıtı (Data key'i extract edilmiş)
        """
        url = f"{self.base_url}/{endpoint}"

        # API isteği
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            # Increase timeout for known slow endpoints
            timeout = float(self.timeout)
            if any(prob_ep in endpoint for prob_ep in self.problematic_endpoints.keys()):
                timeout = min(timeout * 1.5, 90)  # Max 90 seconds

            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                else:
                    response = await client.post(url, headers=headers, json=data)

                response.raise_for_status()
                result = response.json()

                # Metro API response format: {"Success": bool, "Error": {...}, "Data": [...]}
                # Data key'ini extract et
                if isinstance(result, dict):
                    if result.get("Success") and "Data" in result:
                        data_result = result.get("Data", [])
                        # Handle None data
                        if data_result is None:
                            data_result = []
                        logger.debug("API request success",
                                   endpoint=endpoint,
                                   count=len(data_result) if isinstance(data_result, list) else 0)
                        return data_result
                    elif not result.get("Success"):
                        error = result.get("Error", {})
                        logger.error("Metro API returned error",
                                   endpoint=endpoint,
                                   error_title=error.get("Title"),
                                   error_message=error.get("Message"))
                        # Empty response dön hata yerine (graceful degradation)
                        return []

                logger.debug("API request success", endpoint=endpoint)
                return result if result is not None else []

        except httpx.HTTPStatusError as e:
            # Check if this is a known problematic endpoint
            endpoint_name = endpoint.split('/')[-1].split('?')[0]
            if endpoint_name in self.problematic_endpoints and e.response.status_code == 500:
                logger.warning(
                    f"Known problematic endpoint failed: {endpoint_name}",
                    status=e.response.status_code,
                    message=self.problematic_endpoints[endpoint_name]
                )
                return []

            # Retry logic for temporary failures (429, 502, 503, 504)
            if e.response.status_code in [429, 502, 503, 504] and retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Retrying {endpoint} after {wait_time}s (attempt {retry_count + 1}/{self.max_retries})",
                    status=e.response.status_code
                )
                await asyncio.sleep(wait_time)
                return await self._request(method, endpoint, data, retry_count + 1)

            logger.error("Metro API HTTP error",
                        endpoint=endpoint,
                        status=e.response.status_code,
                        response_text=e.response.text[:200] if e.response.text else "No response text")
            return []

        except httpx.TimeoutException:
            # Retry on timeout
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count
                logger.warning(
                    f"Timeout, retrying {endpoint} after {wait_time}s (attempt {retry_count + 1}/{self.max_retries})"
                )
                await asyncio.sleep(wait_time)
                return await self._request(method, endpoint, data, retry_count + 1)

            logger.error("Metro API timeout after retries", endpoint=endpoint, retries=retry_count)
            return []

        except Exception as e:
            logger.error("Metro API request failed", endpoint=endpoint, error=str(e), error_type=type(e).__name__)
            return []
    
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
        boarding_station_id: int,
        direction_id: int,
        date_time: Optional[str] = None
    ) -> List[Dict]:
        """
        Sefer tarifesini al

        Args:
            boarding_station_id: Biniş istasyon ID
            direction_id: Yön ID
            date_time: Tarih/saat (opsiyonel, ISO format)
        """
        from datetime import datetime
        if not date_time:
            date_time = datetime.now().isoformat()

        return await self._post("GetTimeTable", {
            "BoardingStationId": boarding_station_id,
            "DirectionId": direction_id,
            "DateTime": date_time
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
        boarding_station_id: int,
        direction_id: int,
        date_time: Optional[str] = None
    ) -> List[Dict]:
        """
        İstasyonların başlangıç istasyonuna olan uzaklık sürelerini listeler

        Args:
            boarding_station_id: Biniş istasyon ID
            direction_id: Yön ID
            date_time: Tarih/saat (opsiyonel)
        """
        from datetime import datetime
        if not date_time:
            date_time = datetime.now().isoformat()

        return await self._post("GetStationBetweenTime", {
            "BoardingStationId": boarding_station_id,
            "DirectionId": direction_id,
            "DateTime": date_time
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

