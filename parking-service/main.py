"""
İstanbul Otopark Bulucu API
FastAPI backend for finding nearest parking spots in Istanbul using IBB API.
"""

from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from parking_finder import find_nearest_parking


app = FastAPI(
    title="İstanbul Otopark Bulucu API",
    description="""
    İBB ISpark API ve OpenStreetMap kullanarak İstanbul'da en yakın otoparkları bulan API.
    
    **Özellikler:**
    - 🅿️ ISpark gerçek zamanlı kapasite verisi (capacity, emptyCapacity, occupancy_rate)
    - 🗺️ OpenStreetMap yedek veri kaynağı
    - 📍 Otomatik geocoding (adres → koordinat)
    - 📊 Mesafe hesaplama ve sıralama
    - 🔗 Google Maps entegrasyonu
    """,
    version="2.0.0",
    docs_url="/",
    redoc_url="/redoc"
)

# CORS ayarları (frontend için gerekirse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "istanbul-parking-finder"}


@app.get("/nearest-parking")
async def get_nearest_parking(
    query: Optional[str] = Query(
        None,
        description="Hedef adres veya mekan adı (örn: 'Kadıköy İskele', 'Taksim Meydanı')",
        example="Kadıköy İskele"
    ),
    lat: Optional[float] = Query(
        None,
        description="Hedef enlem (latitude)",
        ge=-90,
        le=90,
        example=40.8790
    ),
    lon: Optional[float] = Query(
        None,
        description="Hedef boylam (longitude)",
        ge=-180,
        le=180,
        example=29.2354
    )
):
    """
    En yakın otoparkları bul.
    
    İki kullanım şekli:
    1. **Adres/mekan adı ile**: `?query=Kadıköy İskele`
    2. **Koordinat ile**: `?lat=40.8790&lon=29.2354`
    
    **Dönen veri:**
    - `best`: En yakın otopark
      - ISpark verisi: capacity, emptyCapacity, occupancy_rate, workHours, district
      - OpenStreetMap verisi: capacity (varsa), type
    - `alternatives`: Sonraki en yakın 5 otopark
    - `target`: Hedef koordinat ve Google Maps linki
    - `search_radius_km`: Kullanılan arama yarıçapı
    - `total_found`: Toplam bulunan otopark sayısı
    
    **Örnek ISpark yanıtı:**
    ```json
    {
      "ok": true,
      "best": {
        "name": "Kadıköy Açık Otoparkı",
        "type": "AÇIK OTOPARK",
        "distance_m": 234.5,
        "capacity": 1004,
        "emptyCapacity": 762,
        "occupancy_rate": 24.1,
        "workHours": "24 Saat",
        "district": "KADIKÖY",
        "isOpen": true,
        "source": "ISpark",
        "google_maps_link": "https://..."
      }
    }
    ```
    """
    
    # Validation: Either query OR (lat+lon) must be provided
    if not query and (lat is None or lon is None):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_PARAMETERS",
                "message": "Lütfen 'query' parametresi veya 'lat' + 'lon' parametrelerini girin.",
                "examples": [
                    "/nearest-parking?query=Kadıköy İskele",
                    "/nearest-parking?lat=40.8790&lon=29.2354"
                ]
            }
        )
    
    # Priority: coordinates > query
    if lat is not None and lon is not None:
        destination = query or f"Koordinat: {lat}, {lon}"
        result = find_nearest_parking(destination, lat=lat, lon=lon)
    else:
        result = find_nearest_parking(query)
    
    # Return error response if search failed
    if not result["ok"]:
        return JSONResponse(
            status_code=404 if result.get("error") == "NO_PARKING_FOUND" else 400,
            content=result
        )
    
    return result


@app.get("/parking/search")
async def search_parking_by_address(
    address: str = Query(
        ...,
        description="Aranacak adres veya mekan adı",
        example="Pendik Sahil"
    )
):
    """
    Adres ile otopark ara (alternatif endpoint).
    
    Kullanım: /parking/search?address=Kadıköy İskele
    """
    result = find_nearest_parking(address)
    
    if not result["ok"]:
        return JSONResponse(
            status_code=404 if result.get("error") == "NO_PARKING_FOUND" else 400,
            content=result
        )
    
    return result


@app.get("/parking/by-coords")
async def search_parking_by_coordinates(
    lat: float = Query(
        ...,
        description="Enlem (latitude)",
        ge=-90,
        le=90,
        example=40.8790
    ),
    lon: float = Query(
        ...,
        description="Boylam (longitude)",
        ge=-180,
        le=180,
        example=29.2354
    )
):
    """
    Koordinat ile otopark ara (alternatif endpoint).
    
    Kullanım: /parking/by-coords?lat=40.8790&lon=29.2354
    """
    result = find_nearest_parking(f"Koordinat: {lat}, {lon}", lat=lat, lon=lon)
    
    if not result["ok"]:
        return JSONResponse(
            status_code=404 if result.get("error") == "NO_PARKING_FOUND" else 400,
            content=result
        )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
