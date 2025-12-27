"""
İstanbul Otopark Bulucu - Core Module
ISpark API (gerçek zamanlı kapasite) + OpenStreetMap (yedek) kullanarak en yakın otoparkları bulur.
"""

import math
import json
import urllib.parse
from typing import List, Dict, Any, Tuple, Optional
import time

import requests
from geopy.geocoders import Nominatim


# =============================================================================
# API ENDPOINTS
# =============================================================================
# ISpark Real-time Parking API (Istanbul Municipality)
ISPARK_URL = "https://sehirharitasigateway.ibb.gov.tr/api/WmkA/api/Tkm/ispark"

# OpenStreetMap Overpass API (fallback if ISpark fails)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Geocoder instance (Nominatim - free service)
geocoder = Nominatim(user_agent="istanbul-parking-finder/1.0 (hackathon)")


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points in meters.
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def bbox_polygon_geojson(center_lat: float, center_lon: float, radius_km: float = 1.5) -> Dict[str, Any]:
    """
    Create bounding box polygon around center point.
    """
    # Approximate: 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 * cos(lat) km at given latitude
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))
    
    min_lat = center_lat - lat_delta
    max_lat = center_lat + lat_delta
    min_lon = center_lon - lon_delta
    max_lon = center_lon + lon_delta
    
    return {
        "type": "Polygon",
        "coordinates": [[
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ]]
    }


def geocode(query: str) -> Optional[Tuple[float, float]]:
    """
    Convert address/place name to coordinates using Nominatim.
    """
    try:
        search_query = query
        if "istanbul" not in query.lower() and "türkiye" not in query.lower():
            search_query = f"{query}, Istanbul, Turkey"
        
        print(f"\n🌍 GEOCODING:")
        print(f"   Sorgu: '{query}' → '{search_query}'")
        
        location = geocoder.geocode(search_query, timeout=10)
        
        if location:
            print(f"   ✅ Sonuç: ({location.latitude}, {location.longitude})")
            return (location.latitude, location.longitude)
        
        print(f"   ❌ Geocoding başarısız")
        return None
    
    except Exception as e:
        print(f"   ❌ Geocoding error: {e}")
        return None


def fetch_parkings_in_geom(polygon_geojson: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch parking POIs from ISpark API (primary) or OpenStreetMap (fallback).
    
    Args:
        polygon_geojson: GeoJSON polygon for filtering results
        limit: Maximum number of results
    
    Returns:
        List of parking POIs in standard format
    """
    # Extract bbox from polygon
    coords = polygon_geojson["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    print(f"\n🌐 FETCHING PARKINGS:")
    print(f"   Bbox: {min_lat:.6f},{min_lon:.6f},{max_lat:.6f},{max_lon:.6f}")
    
    # ==========================================================================
    # TRY 1: ISpark API (Real-time data with capacity info)
    # ==========================================================================
    try:
        print(f"   🅿️ Trying ISpark API...")
        
        # IMPORTANT: This header is required for authentication
        # The token appears to be dynamic/session-based from harita.istanbul
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://harita.istanbul/",
            "Origin": "https://harita.istanbul",
            "abc-3903258-571632": "ZXlKaGJHY2lPaUpvZEhSd09pOHZkM2QzTG5jekxtOXlaeTh5TURBeEx6QTBMM2h0YkdSemFXY3RiVzl5WlNOb2JXRmpMWE5vWVRJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SjFjMlZ5VG1GdFpTSTZJbUZ1YjIxcGJTSXNJbE5sYzNOcGIyNUpaQ0k2SWpZMFptSmpPRE13TFdWa1pXWXROREUwTWkwNFlXTXlMVGhsTVRFNFlqZ3pZMlkwTUNJc0ltTnlaV0YwWVdSRVlYUmxJam9pTWpjdU1USXVNakF5TlNBd09Ub3hPRG94TUNJc0ltcDBhU0k2SW1SaE4ySTJPR0poTFRneFlUY3ROR1ZoWVMwNE16VXhMVEptTXpWak1UVXdOekkzWXlJc0luTnZkWEpqWlNJNklsc25NbVJyVWljc0p6QlVkbk1uTENkM1UyeHpKeXduVEhoc2R5Y3NKMWgyYzNvbkxDZE5lR1JrSnl3bmRuVkRUeWNzSjJFd1Ywd25MQ2MzV0V4NUp5d25OMUUzTUNjc0ozY3lhSGtuTENkbVZtUk5KeXduWm5GdWRpY3NKM2d5TWtNbkxDZENPRkEySnl3blVISjJVaWNzSjBSQlpYUW5MQ2RQTm1ORkp5d25RVGRpWlNjc0p6VnZNMHNuTENkUFZWaEtKeXduUVdaVWVpY3NKM1JrYm04bkxDZE5NVE5hSnl3blJEUmpPU2NzSjJSM1prY25MQ2N4ZVZkNUp5d25OMmQ0ZENjc0ptWlJVMUFuTENkMFdYTjZKeXduWm1jM015Y3NKMFJWYjNFbkxDZFJURlpvSnl3bk5rOW1XU2NzSjFkdGEwRW5MQ2RqZURCMkp5d25ZMDB6ZHljc0oxcEtiVUVuTENkdFpsRkhKeXduTkRsTVJTY3NKMGhCVWxnbkxDYzRkME0wSnl3bldWRlRPU2NzSjNkVWQyZ25MQ2M0U21wR0p5d25aMEU0TkNjc0p6UnNVbmtuTENkT1FXMURKeXduUzA1WU9TY3NKMjEwWTFvbkxDZFZjek01Snl3blFtTk5SeWNzSjNsSFdXSW5MQ2RQWlhodEp5d25OM2hRV0Njc0p6TnRkV3NuTENkSmJuRllKeXduZGxCTmFpY3NKMk5VTlZrbkxDYzJPRE14Snl3bmRUUkNZeWNzSjNOT1Uyc25MQ2Q1TWxSbEp5d25NRWt6Wnljc0oyOHdXVUluTENkU01uRkRKeXduVTBNemF5Y3NKMHRvTTFvbkxDY3laRWxsSnl3bmRtdGhkaWNzSjJKdk1tTW5MQ2RLWTBsTEp5d25ZbFpSY3ljc0owSXlWMDBuTENkWVdUVnJKeXduWVhObWRTY3NKMHRJWm5BbkxDYzVVVU5rSnl3blZrdFBlaWRkSWl3aWJtSm1Jam94TnpZMk9ESTNNRGt3TENKbGVIQWlPakUzTmpZNE16UXlPVEFzSW1semN5STZJbWgwZEhCek9pOHZZMkp6YzJoMGIydGxibk5sY25acFkyVXVhV0ppTG1kdmRpNTBjaThpZlEuUGJVZThZOWdRRkxvR2RrT21qNWdCLVhVdUl5SzY3M250Y3NoUFR3ZFBFaw=="
        }
        
        resp = requests.get(ISPARK_URL, headers=headers, timeout=20)
        
        print(f"   📡 ISpark Response Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            
            if "features" in data and isinstance(data["features"], list):
                print(f"   ✅ ISpark returned {len(data['features'])} total parkings")
                
                # Filter by bounding box
                filtered_parkings = []
                for feature in data["features"]:
                    if "geometry" in feature and "coordinates" in feature["geometry"]:
                        lon, lat = feature["geometry"]["coordinates"]
                        
                        # Check if within bbox
                        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                            props = feature.get("properties", {})
                            
                            # Convert to standard format
                            parking = {
                                "name": props.get("parkName", "ISpark Otopark"),
                                "lat": lat,
                                "lon": lon,
                                "type": props.get("parkType", "OTOPARK"),
                                "capacity": props.get("capacity", 0),
                                "emptyCapacity": props.get("emptyCapacity", 0),
                                "workHours": props.get("workHours", "24 Saat"),
                                "district": props.get("district", ""),
                                "isOpen": props.get("isOpen", True),
                                "source": "ISpark"
                            }
                            filtered_parkings.append(parking)
                            
                            if len(filtered_parkings) >= limit:
                                break
                
                if filtered_parkings:
                    print(f"   ✅ Found {len(filtered_parkings)} ISpark parkings in bbox")
                    return filtered_parkings
                else:
                    print(f"   ⚠️ No ISpark parkings found in bbox, falling back to OSM")
    
    except Exception as e:
        print(f"   ❌ ISpark API error: {e}")
        print(f"   ⚠️ Falling back to OpenStreetMap...")
    
    # ==========================================================================
    # TRY 2: OpenStreetMap Overpass API (Fallback)
    # ==========================================================================
    try:
        bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"  # south,west,north,east
        
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="parking"]({bbox});
          way["amenity"="parking"]({bbox});
          relation["amenity"="parking"]({bbox});
        );
        out center {limit};
        """
        
        print(f"   🗺️ Trying OpenStreetMap Overpass API...")
        print(f"   Query Bbox: {bbox}")
        
        resp = requests.post(
            OVERPASS_URL,
            data=overpass_query,
            timeout=30,
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
        
        print(f"   📡 Overpass Response Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"   ❌ Overpass returned non-200 status")
            return []
        
        data = resp.json()
        
        if "elements" not in data:
            print(f"   ❌ No 'elements' in Overpass response")
            return []
        
        elements = data["elements"]
        print(f"   ✅ Found {len(elements)} OSM parking elements")
        
        # Convert OSM elements to standard format
        parkings = []
        for elem in elements:
            lat = elem.get("lat")
            lon = elem.get("lon")
            
            # For ways/relations, use center coordinates
            if lat is None and "center" in elem:
                lat = elem["center"]["lat"]
                lon = elem["center"]["lon"]
            
            if lat is None or lon is None:
                continue
            
            tags = elem.get("tags", {})
            name = tags.get("name", tags.get("operator", "Otopark"))
            
            # Determine parking type
            parking_type = "AÇIK OTOPARK"
            if tags.get("parking") == "underground" or tags.get("parking") == "multi-storey":
                parking_type = "KAPALI OTOPARK"
            elif tags.get("parking") == "surface":
                parking_type = "AÇIK OTOPARK"
            
            parking = {
                "name": name,
                "lat": lat,
                "lon": lon,
                "type": parking_type,
                "capacity": int(tags.get("capacity", 0)),
                "emptyCapacity": 0,  # OSM doesn't have real-time data
                "workHours": "24 Saat",
                "district": "",
                "isOpen": True,
                "source": "OpenStreetMap"
            }
            parkings.append(parking)
        
        print(f"   ✅ Converted to {len(parkings)} parkings")
        return parkings
    
    except Exception as e:
        print(f"   ❌ OpenStreetMap error: {e}")
        return []


def rank_by_distance(target_lat: float, target_lon: float, pois: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate distances to all POIs and rank by proximity.
    
    Returns list with additional fields:
    - distance_m: Distance in meters
    - google_maps_link: Google Maps link to parking
    - occupancy_rate: Percentage of occupied spots (if ISpark data available)
    """
    print(f"\n📏 MESAFE HESAPLAMA:")
    print(f"   Hedef: ({target_lat}, {target_lon})")
    print(f"   İşlenecek POI sayısı: {len(pois)}")
    
    ranked = []
    
    for p in pois:
        poi_lat = p.get("lat")
        poi_lon = p.get("lon")
        
        if not poi_lat or not poi_lon:
            continue
        
        d = haversine_m(target_lat, target_lon, poi_lat, poi_lon)
        
        # Calculate occupancy rate if capacity data available
        occupancy_rate = None
        if p.get("capacity", 0) > 0:
            occupied = p["capacity"] - p.get("emptyCapacity", 0)
            occupancy_rate = round((occupied / p["capacity"]) * 100, 1)
        
        result = {
            "name": p.get("name"),
            "type": p.get("type"),
            "lat": poi_lat,
            "lon": poi_lon,
            "distance_m": round(d, 1),
            "capacity": p.get("capacity"),
            "emptyCapacity": p.get("emptyCapacity"),
            "workHours": p.get("workHours"),
            "district": p.get("district"),
            "isOpen": p.get("isOpen"),
            "source": p.get("source"),
            "google_maps_link": f"https://www.google.com/maps/search/?api=1&query={poi_lat},{poi_lon}",
        }
        
        if occupancy_rate is not None:
            result["occupancy_rate"] = occupancy_rate
        
        ranked.append(result)
    
    ranked.sort(key=lambda x: x["distance_m"])
    
    if ranked:
        print(f"   ✅ Sıralandı: En yakın {ranked[0]['name']} ({ranked[0]['distance_m']}m)")
    else:
        print(f"   ⚠️ Hiç geçerli POI bulunamadı")
    
    return ranked


def find_nearest_parking(destination: str, lat: float = None, lon: float = None) -> Dict[str, Any]:
    """
    Main function to find nearest parking to a destination.
    Uses progressive radius search (1.5km → 8km).
    
    Returns:
        Dictionary with search results:
        - ok: Success flag
        - query: Original query
        - target: Resolved coordinates
        - best: Nearest parking
        - alternatives: Top 5 nearest parkings
        - error: Error code if failed
    """
    print(f"\n{'='*60}")
    print(f"🅿️  OTOPARK ARAMA BAŞLADI")
    print(f"{'='*60}")
    print(f"Hedef: {destination}")
    print(f"Koordinat: lat={lat}, lon={lon}")
    
    # 1) Resolve target coordinate
    if lat is None or lon is None:
        geo = geocode(destination)
        if not geo:
            return {
                "ok": False,
                "error": "GEOCODE_FAILED",
                "message": "Hedefi koordinata çeviremedim. Lütfen daha detaylı adres ver.",
                "query": destination,
            }
        lat, lon = geo
    
    # 2) Progressive radius search
    for radius_km in (1.5, 3.0, 5.0, 8.0):
        print(f"\n🔍 ARAMA TURU: {radius_km} km yarıçap")
        print(f"{'-'*60}")
        
        poly = bbox_polygon_geojson(lat, lon, radius_km=radius_km)
        pois = fetch_parkings_in_geom(poly, limit=50)
        ranked = rank_by_distance(lat, lon, pois)
        
        if ranked:
            print(f"\n✅ BAŞARILI! {len(ranked)} otopark bulundu.")
            best = ranked[0]
            return {
                "ok": True,
                "query": destination,
                "target": {
                    "lat": lat,
                    "lon": lon,
                    "google_maps_link": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                },
                "search_radius_km": radius_km,
                "best": best,
                "alternatives": ranked[1:6],  # Next 5 closest
                "total_found": len(ranked)
            }
    
    # 3) No parking found within max radius
    print(f"\n❌ OTOPARK BULUNAMADI!")
    print(f"   8 km yarıçap içinde arama yapıldı.")
    print(f"{'='*60}\n")
    
    return {
        "ok": False,
        "error": "NO_PARKING_FOUND",
        "message": "Bu hedefin yakınında otopark bulunamadı (8 km içinde arama yapıldı).",
        "query": destination,
        "target": {
            "lat": lat,
            "lon": lon,
            "google_maps_link": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        },
    }


if __name__ == "__main__":
    # Test: Koordinat ile direkt
    print("=== Test 1: Koordinat ile (Pendik Sahil) ===")
    result = find_nearest_parking("Pendik Sahil", lat=40.877, lon=29.236)
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
