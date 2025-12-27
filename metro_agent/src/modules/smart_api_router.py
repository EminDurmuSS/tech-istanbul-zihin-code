# ============================================================================
# DOSYA: src/modules/smart_api_router.py
# AÇIKLAMA: Akıllı API Router - Kullanıcı sorgusuna göre otomatik API seçimi
# ============================================================================

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataSource(str, Enum):
    """Veri kaynakları"""
    LINES = "lines"
    STATIONS = "stations"
    SERVICE_STATUS = "service_status"
    FAULTY_EQUIPMENTS = "faulty_equipments"
    FAILURE_TYPES = "failure_types"
    TECHNICAL_OBJECTS = "technical_objects"
    TIMETABLE = "timetable"
    DIRECTIONS = "directions"
    STATION_BETWEEN_TIME = "station_between_time"
    ANNOUNCEMENTS = "announcements"
    FAQ = "faq"
    TICKET_PRICES = "ticket_prices"
    MAPS = "maps"
    PROJECTS = "line_projects"
    RAILWAY_GROUPS = "railway_groups"


@dataclass
class QueryRequirement:
    """Sorgu için gerekli veri kaynakları"""
    required_sources: List[DataSource]
    optional_sources: List[DataSource]
    parameters: Dict[str, Any]
    priority: int  # 1-5, yüksek = öncelikli


class SmartAPIRouter:
    """
    Akıllı API Router

    Kullanıcı sorgusunu analiz eder ve hangi API'lere istek atılacağını belirler.
    Paralel isteklerle performansı optimize eder.
    """

    # API seçim promptu
    API_SELECTION_PROMPT = """Kullanıcı sorgusunu analiz et ve hangi Metro API'lerine istek atılması gerektiğini belirle.

Kullanıcı Sorgusu: "{query}"

Entity'ler: {entities}

Mevcut API'ler ve kullanım amaçları:
1. lines - Hat bilgileri (M1, M2, M3, M4, M5, M6, M7, M8, M9 hatları)
2. stations - İstasyon bilgileri (tüm istasyonlar, konum, özellikler)
3. service_status - Hizmet durumu (sefer iptal, arıza, gecikme)
4. faulty_equipments - Arızalı ekipmanlar (asansör, yürüyen merdiven, turnike)
5. failure_types - Arıza türleri ve kategorileri
6. technical_objects - Teknik nesne türleri
7. timetable - Sefer tarifeleri (ilk/son sefer, sefer aralıkları)
8. directions - Hat yön bilgileri
9. station_between_time - İstasyonlar arası süreler
10. announcements - Duyurular ve bildirimler
11. faq - Sıkça sorulan sorular
12. ticket_prices - Bilet ücretleri
13. maps - Ağ haritaları
14. line_projects - Devam eden projeler
15. railway_groups - Raylı sistem grupları

Aşağıdaki JSON formatında yanıt ver:
{{
    "required_sources": ["API1", "API2"],  // Mutlaka gerekli
    "optional_sources": ["API3"],  // İsteğe bağlı, zenginleştirme için
    "parameters": {{  // API çağrıları için parametreler
        "line_id": 4,
        "station_name": "Kadıköy",
        "equipment_type": "asansör"
    }},
    "priority": 3,  // 1-5 arası öncelik
    "reasoning": "Kısa açıklama"
}}

SADECE JSON döndür:"""

    def __init__(
        self,
        metro_client: MetroAPIClient,
        llm_client: Optional[OpenRouterClient] = None
    ):
        self.metro = metro_client
        self.llm = llm_client

        # Cache için (1 dakika TTL)
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 60  # saniye

    async def route_query(
        self,
        query: str,
        entities: Dict[str, Any],
        intent_type: str
    ) -> Dict[str, Any]:
        """
        Sorguyu analiz et ve gerekli API'lere istek at

        Args:
            query: Kullanıcı sorgusu
            entities: Çıkarılmış entity'ler
            intent_type: Intent tipi

        Returns:
            Tüm API yanıtlarını içeren dict
        """
        try:
            # 1. API seçimini belirle
            requirement = await self._determine_apis(query, entities, intent_type)

            logger.info(
                "API routing determined",
                required=requirement.required_sources,
                optional=requirement.optional_sources,
                parameters=requirement.parameters
            )

            # 2. Paralel API çağrıları
            results = await self._fetch_data(requirement)

            # 3. Sonuçları döndür
            return results

        except Exception as e:
            logger.error("API routing error", error=str(e))
            return {}

    async def _determine_apis(
        self,
        query: str,
        entities: Dict[str, Any],
        intent_type: str
    ) -> QueryRequirement:
        """Hangi API'lere istek atılacağını belirle"""

        # Intent bazlı hızlı yönlendirme (LLM'e ihtiyaç yok)
        quick_routing = self._quick_route(intent_type, entities)
        if quick_routing:
            return quick_routing

        # Karmaşık sorgular için LLM kullan
        if self.llm:
            return await self._llm_based_routing(query, entities)

        # Fallback: temel routing
        return self._fallback_routing(entities)

    def _quick_route(
        self,
        intent_type: str,
        entities: Dict[str, Any]
    ) -> Optional[QueryRequirement]:
        """Intent bazlı hızlı API yönlendirmesi"""

        # FAULT_REPORT - Arıza bildirimi
        if intent_type == "FAULT_REPORT":
            return QueryRequirement(
                required_sources=[
                    DataSource.FAULTY_EQUIPMENTS,
                    DataSource.STATIONS,
                    DataSource.LINES
                ],
                optional_sources=[
                    DataSource.FAILURE_TYPES,
                    DataSource.TECHNICAL_OBJECTS,
                    DataSource.SERVICE_STATUS,
                    DataSource.ANNOUNCEMENTS
                ],
                parameters=entities,
                priority=5  # En yüksek öncelik
            )

        # FAULT_INQUIRY - Arıza sorgulama
        if intent_type == "FAULT_INQUIRY":
            return QueryRequirement(
                required_sources=[
                    DataSource.FAULTY_EQUIPMENTS,
                    DataSource.STATIONS
                ],
                optional_sources=[
                    DataSource.SERVICE_STATUS
                ],
                parameters=entities,
                priority=4
            )

        # SERVICE_STATUS - Hizmet durumu
        if intent_type == "SERVICE_STATUS":
            return QueryRequirement(
                required_sources=[
                    DataSource.SERVICE_STATUS,
                    DataSource.LINES
                ],
                optional_sources=[
                    DataSource.ANNOUNCEMENTS,
                    DataSource.DIRECTIONS
                ],
                parameters=entities,
                priority=4
            )

        # TIMETABLE - Sefer saatleri
        if intent_type == "TIMETABLE":
            return QueryRequirement(
                required_sources=[
                    DataSource.STATIONS,
                    DataSource.DIRECTIONS
                ],
                optional_sources=[
                    DataSource.TIMETABLE,
                    DataSource.LINES
                ],
                parameters=entities,
                priority=3
            )

        # DIRECTION_HELP - Yön tarifi
        if intent_type == "DIRECTION_HELP":
            return QueryRequirement(
                required_sources=[
                    DataSource.STATIONS,
                    DataSource.LINES,
                    DataSource.DIRECTIONS
                ],
                optional_sources=[
                    DataSource.STATION_BETWEEN_TIME,
                    DataSource.SERVICE_STATUS
                ],
                parameters=entities,
                priority=3
            )

        # ACCESSIBILITY - Erişilebilirlik
        if intent_type == "ACCESSIBILITY":
            return QueryRequirement(
                required_sources=[
                    DataSource.STATIONS
                ],
                optional_sources=[
                    DataSource.FAULTY_EQUIPMENTS
                ],
                parameters=entities,
                priority=2
            )

        # FARE_INFO - Ücret bilgisi
        if intent_type == "FARE_INFO":
            return QueryRequirement(
                required_sources=[
                    DataSource.TICKET_PRICES
                ],
                optional_sources=[],
                parameters=entities,
                priority=1
            )

        # ANNOUNCEMENTS - Duyurular
        if intent_type == "ANNOUNCEMENTS":
            return QueryRequirement(
                required_sources=[
                    DataSource.ANNOUNCEMENTS
                ],
                optional_sources=[
                    DataSource.LINES
                ],
                parameters=entities,
                priority=2
            )

        # GENERAL_FAQ - Genel sorular
        if intent_type == "GENERAL_FAQ":
            return QueryRequirement(
                required_sources=[
                    DataSource.FAQ
                ],
                optional_sources=[],
                parameters=entities,
                priority=1
            )

        return None

    async def _llm_based_routing(
        self,
        query: str,
        entities: Dict[str, Any]
    ) -> QueryRequirement:
        """LLM bazlı akıllı routing"""

        try:
            import json

            prompt = self.API_SELECTION_PROMPT.format(
                query=query,
                entities=json.dumps(entities, ensure_ascii=False)
            )

            response = await self.llm.complete(prompt, temperature=0.1)
            data = await self.llm.parse_json_response(response)

            required = [DataSource(s) for s in data.get("required_sources", [])]
            optional = [DataSource(s) for s in data.get("optional_sources", [])]

            return QueryRequirement(
                required_sources=required,
                optional_sources=optional,
                parameters=data.get("parameters", {}),
                priority=int(data.get("priority", 3))
            )

        except Exception as e:
            logger.warning("LLM routing failed, using fallback", error=str(e))
            return self._fallback_routing(entities)

    def _fallback_routing(self, entities: Dict[str, Any]) -> QueryRequirement:
        """Fallback routing stratejisi"""

        # Her durumda temel veriler
        return QueryRequirement(
            required_sources=[
                DataSource.STATIONS,
                DataSource.LINES
            ],
            optional_sources=[
                DataSource.SERVICE_STATUS,
                DataSource.FAQ
            ],
            parameters=entities,
            priority=2
        )

    async def _fetch_data(
        self,
        requirement: QueryRequirement
    ) -> Dict[str, Any]:
        """API'lerden veri topla (paralel)"""

        results = {}

        # Tüm kaynakları birleştir
        all_sources = requirement.required_sources + requirement.optional_sources

        # Paralel çağrılar için task listesi
        tasks = []
        source_names = []

        for source in all_sources:
            task = self._fetch_single_source(source, requirement.parameters)
            tasks.append(task)
            source_names.append(source.value)

        # Paralel çalıştır
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for name, response in zip(source_names, responses):
                if isinstance(response, Exception):
                    logger.warning(f"API call failed: {name}", error=str(response))
                    results[name] = []
                else:
                    results[name] = response

        return results

    async def _fetch_single_source(
        self,
        source: DataSource,
        parameters: Dict[str, Any]
    ) -> Any:
        """Tek bir veri kaynağından fetch yap"""

        # Cache kontrolü
        cache_key = f"{source.value}:{str(parameters)}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            import time
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"Cache hit: {source.value}")
                return data

        # API çağrısı
        try:
            result = await self._call_api(source, parameters)

            # Cache'e ekle
            import time
            self._cache[cache_key] = (result, time.time())

            return result

        except Exception as e:
            logger.error(f"API call error: {source.value}", error=str(e))
            return []

    async def _call_api(
        self,
        source: DataSource,
        parameters: Dict[str, Any]
    ) -> Any:
        """Gerçek API çağrısı"""

        if source == DataSource.LINES:
            return await self.metro.get_lines()

        elif source == DataSource.STATIONS:
            # Eğer line_id varsa ona göre, yoksa tümünü al
            line_id = parameters.get("line_id")
            if line_id:
                return await self.metro.get_stations_by_line(int(line_id))
            return await self.metro.get_stations()

        elif source == DataSource.SERVICE_STATUS:
            return await self.metro.get_service_statuses()

        elif source == DataSource.FAULTY_EQUIPMENTS:
            return await self.metro.get_faulty_equipments()

        elif source == DataSource.FAILURE_TYPES:
            return await self.metro.get_failure_types()

        elif source == DataSource.TECHNICAL_OBJECTS:
            return await self.metro.get_technical_object_types()

        elif source == DataSource.TIMETABLE:
            station_id = parameters.get("station_id")
            direction_id = parameters.get("direction_id")
            if station_id and direction_id:
                return await self.metro.get_timetable(
                    int(station_id),
                    int(direction_id)
                )
            return []

        elif source == DataSource.DIRECTIONS:
            line_id = parameters.get("line_id")
            if line_id:
                return await self.metro.get_direction_by_line(int(line_id))
            return await self.metro.get_directions()

        elif source == DataSource.STATION_BETWEEN_TIME:
            station_id = parameters.get("station_id")
            direction_id = parameters.get("direction_id")
            if station_id and direction_id:
                return await self.metro.get_station_between_time(
                    int(station_id),
                    int(direction_id)
                )
            return []

        elif source == DataSource.ANNOUNCEMENTS:
            line_id = parameters.get("line_id")
            if line_id:
                return await self.metro.get_announcements_by_line(int(line_id), "tr")
            return await self.metro.get_announcements("tr")

        elif source == DataSource.FAQ:
            return await self.metro.get_faq()

        elif source == DataSource.TICKET_PRICES:
            return await self.metro.get_ticket_prices("tr")

        elif source == DataSource.MAPS:
            return await self.metro.get_maps()

        elif source == DataSource.PROJECTS:
            return await self.metro.get_line_projects()

        elif source == DataSource.RAILWAY_GROUPS:
            return await self.metro.get_railway_groups()

        else:
            logger.warning(f"Unknown data source: {source}")
            return []
