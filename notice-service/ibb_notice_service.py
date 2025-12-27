import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for the latest data
latest_data: Optional[List["Announcement"]] = None

# Constants
IBB_API_URL = "https://sehirharitasigateway.ibb.gov.tr/api/NAmC/api/Tkm/duyurular"
POLLING_INTERVAL = 60  # seconds

# Headers from the user request
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "content-type": "application/json; charset=utf-8",
    "origin": "https://harita.istanbul",
    "pragma": "no-cache",
    "referer": "https://harita.istanbul/",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "abc-3903258-571632": "ZXlKaGJHY2lPaUpvZEhSd09pOHZkM2QzTG5jekxtOXlaeTh5TURBeEx6QTBMM2h0YkdSemFXY3RiVzl5WlNOb2JXRmpMWE5vWVRJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5VG1GdFpTSTZJbUZ1YjIxcGJTSXNJbE5sYzNOcGIyNUpaQ0k2SWpBNU56UXlZbVEwTFRNMFpUZ3ROR1JqWlMwNVpXVTNMV1F4WkRVeE1qQmlOVFUxWXlJc0ltTnlaV0YwWVdSRVlYUmxJam9pTWpjdU1USXVNakF5TlNBeE1Ub3lPVG8xTXlJc0ltcDBhU0k2SWpRM05UWmlPRFF3TFdVelpqVXRORFV6TkMwNU9UYzBMVFl5T0dNeU9EY3dPVEpqTUNJc0luTnZkWEpqWlNJNklsc25NbVJyVWljc0p6QlVkbk1uTENkM1UyeHpKeXduVEhoc2R5Y3NKMWgyYzNvbkxDZE5lR1JrSnl3bmRuVkRUeWNzSjJFd1Ywd25MQ2MzV0V4NUp5d25OMUUzTUNjc0ozY3lhSGtuTENkbVZtUk5KeXduWm5GdWRpY3NKM2d5TWtNbkxDZENPRkEySnl3blVISjJVaWNzSjBSQlpYUW5MQ2RQTm1ORkp5d25RVGRpWlNjc0p6VnZNMHNuTENkUFZWaEtKeXduUVdaVWVpY3NKM1JrYm04bkxDZE5NVE5hSnl3blJEUmpPU2NzSjJSM1prY25MQ2N4ZVZkNUp5d25OMmQ0ZENjc0oyWlJVMUFuTENkMFdYTjZKeXduWm1jM015Y3NKMFJWYjNFbkxDZFJURlpvSnl3bk5rOW1XU2NzSjFkdGEwRW5MQ2RqZURCMkp5d25ZMDB6ZHljc0oxcEtiVUVuTENkdFpsRkhKeXduTkRsTVJTY3NKMGhCVWxnbkxDYzRkME0wSnl3bldWRlRPU2NzSjNkVWQyZ25MQ2M0U21wR0p5d25aMEU0TkNjc0p6UnNVbmtuTENkT1FXMURKeXduUzA1WU9TY3NKMjEwWTFvbkxDZFZjek01Snl3blFtTk5SeWNzSjNsSFdXSW5MQ2RQWlhodEp5d25OM2hRV0Njc0p6TnRkV3NuTENkSmJuRllKeXduZGxCTmFpY3NKMk5VTlZrbkxDYzJPRE14Snl3bmRUUkNZeWNzSjNOT1Uyc25MQ2Q1TWxSbEp5d25NRWt6Wnljc0oyOHdXVUluTENkU01uRkRKeXduVTBNemF5Y3NKMHRvTTFvbkxDY3laRWxsSnl3bmRtdGhkaWNzSjJKdk1tTW5MQ2RLWTBsTEp5d25ZbFpSY3ljc0owSXlWMDBuTENkWVdUVnJKeXduWVhObWRTY3NKMHRJWm5BbkxDYzVVVU5rSnl3blZrdFBlaWRkSWl3aWJtSm1Jam94TnpZMk9ETTBPVGt6TENKbGVIQWlPakUzTmpZNE5ESXhPVE1zSW1semN5STZJbWgwZEhCek9pOHZZMkp6YzJoMGIydGxibk5sY25acFkyVXVhV0ppTG1kdmRpNTBjaThpZlEuV0dmNERrbXpzLUVhZkhuZjhDemJKSDNtVmNVVzdLWVlGR2I3VGVJOUNITQ"
}


class Coordinates(BaseModel):
    """Coordinates model"""
    latitude: float
    longitude: float


class Announcement(BaseModel):
    """Structured announcement model"""
    id: int
    title: str
    title_en: str
    description: str
    description_en: str
    category: int
    priority: int
    start_date: str
    end_date: str
    camera_id: int
    link: str
    coordinates: Coordinates
    time_diff: int


def transform_data(raw_data: dict) -> List[Announcement]:
    """Transform GeoJSON data to structured list of announcements"""
    announcements = []
    
    if not raw_data or "features" not in raw_data:
        return announcements
    
    for feature in raw_data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [0, 0])
        
        announcement = Announcement(
            id=props.get("id", 0),
            title=props.get("baslik", ""),
            title_en=props.get("baslikIng", ""),
            description=props.get("metin", ""),
            description_en=props.get("metinIng", ""),
            category=props.get("tipi", 0),
            priority=props.get("oncelik", 0),
            start_date=props.get("girisTarihi", ""),
            end_date=props.get("bitisTarihi", ""),
            camera_id=props.get("kameraId", 0),
            link=props.get("link", ""),
            coordinates=Coordinates(
                longitude=coords[0] if len(coords) > 0 else 0,
                latitude=coords[1] if len(coords) > 1 else 0
            ),
            time_diff=props.get("timeDiff", 0)
        )
        announcements.append(announcement)
    
    return announcements


async def fetch_data():
    """Fetches data from the IBB API and updates the global storage."""
    global latest_data
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(IBB_API_URL, headers=HEADERS)
            response.raise_for_status()
            raw_data = response.json()
            latest_data = transform_data(raw_data)
            logger.info(f"Successfully fetched and transformed {len(latest_data)} announcements from IBB API")
    except Exception as e:
        logger.error(f"Error fetching data from IBB API: {e}")


async def polling_task():
    """Background task that runs periodically to fetch data."""
    while True:
        await fetch_data()
        await asyncio.sleep(POLLING_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background polling task
    task = asyncio.create_task(polling_task())
    yield
    # Shutdown: Cancel the task if needed (not strictly necessary as the loop dies with the app)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


@app.get("/duyurular")
async def get_duyurular():
    """Returns the latest cached data as structured announcements."""
    if latest_data is None:
         # Attempt to fetch immediately if we haven't yet, or return a loading/error state
        await fetch_data()
        if latest_data is None:
             raise HTTPException(status_code=503, detail="Data not available yet")
    
    # Convert to dict and return with proper UTF-8 encoding
    return JSONResponse(
        content=[announcement.model_dump() for announcement in latest_data],
        media_type="application/json; charset=utf-8"
    )


def get_announcements() -> Optional[List[Announcement]]:
    """
    Synchronous method to get the latest announcements.
    Can be imported and used by other modules.
    Returns None if data hasn't been fetched yet.
    """
    return latest_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
