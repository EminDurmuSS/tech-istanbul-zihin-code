# 🅿️ İstanbul Otopark Bulucu API

İBB Şehir Haritası Gateway API kullanarak İstanbul'da **en yakın otoparkları bulan** REST API.

## 🚀 Özellikler

- ✅ **Adres veya koordinat** ile arama
- ✅ **İSPARK, Açık ve Kapalı otoparklar** (İBB kategorileri: 215, 366, 367)
- ✅ **Haversine mesafe hesaplama** (metre cinsinden)
- ✅ **Progresif arama** (1.5km → 8km yarıçap genişletme)
- ✅ **Ücretsiz geocoding** (Nominatim)
- ✅ **Google Maps linkleri** (hedef ve otopark lokasyonları)
- ✅ **FastAPI + Swagger UI** (otomatik API dokümantasyonu)

---

## 📦 Kurulum

### 1. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### 2. API'yi başlat

```bash
uvicorn main:app --reload
```

Varsayılan adres: **http://localhost:8000**

---

## 🔌 API Kullanımı

### **Ana Endpoint: `/nearest-parking`**

İki kullanım şekli:

#### 1️⃣ Adres/Mekan Adı ile Arama

```bash
curl "http://localhost:8000/nearest-parking?query=Kadıköy%20İskele"
```

**Örnek yanıt:**

```json
{
  "ok": true,
  "query": "Kadıköy İskele",
  "target": {
    "lat": 40.9999,
    "lon": 29.0275,
    "google_maps_link": "https://www.google.com/maps/search/?api=1&query=40.9999,29.0275"
  },
  "search_radius_km": 1.5,
  "best": {
    "name": "Kadıköy İskele Otoparkı",
    "address": "Caferağa Mah. Moda Cad. No:12",
    "category": "İSPARK",
    "distance_m": 150.3,
    "lat": 40.9985,
    "lon": 29.0288,
    "google_maps_link": "https://www.google.com/maps/search/?api=1&query=40.9985,29.0288"
  },
  "alternatives": [
    {
      "name": "Kadıköy İskele Otoparkı",
      "distance_m": 150.3,
      ...
    },
    ...
  ],
  "total_found": 8
}
```

#### 2️⃣ Koordinat ile Arama

```bash
curl "http://localhost:8000/nearest-parking?lat=40.8790&lon=29.2354"
```

---

## 🛠️ Alternatif Endpoint'ler

### `/parking/search` - Sadece adres

```bash
curl "http://localhost:8000/parking/search?address=Taksim%20Meydanı"
```

### `/parking/by-coords` - Sadece koordinat

```bash
curl "http://localhost:8000/parking/by-coords?lat=41.0082&lon=28.9784"
```

### `/health` - Health check

```bash
curl http://localhost:8000/health
```

**Yanıt:**

```json
{
  "status": "healthy",
  "service": "istanbul-parking-finder"
}
```

---

## 📖 API Dokümantasyonu

API başlatıldıktan sonra:

- **Swagger UI**: http://localhost:8000/
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Test (Python modülü olarak)

```bash
python parking_finder.py
```

Test çıktısı:

```json
{
  "ok": true,
  "query": "Pendik Sahil",
  "target": { "lat": 40.8790, "lon": 29.2354 },
  "best": {
    "name": "Pendik Sahil Otoparkı",
    "address": "...",
    "category": "İSPARK",
    "distance_m": 120.5,
    ...
  },
  ...
}
```

---

## 📐 Sistem Mimarisi

```
1. Kullanıcı → Hedef (adres/koordinat)
2. Geocoding (Nominatim) → Koordinat
3. Bounding Box (Polygon) → Arama alanı
4. İBB API → Otoparkları çek (alt_kategori__in=215,366,367)
5. Haversine → Mesafe hesapla
6. Sıralama → En yakından uzağa
7. Yanıt → JSON (best + alternatives + Google Maps linkleri)
```

---

## 🔍 Progresif Arama Mantığı

API, otobark bulunamazsa otomatik olarak arama yarıçapını genişletir:

- **1. Aşama**: 1.5 km
- **2. Aşama**: 3.0 km
- **3. Aşama**: 5.0 km
- **4. Aşama**: 8.0 km

8 km içinde otopark bulunamazsa `NO_PARKING_FOUND` hatası döner.

---

## 🚦 Hata Kodları

| Hata Kodu          | Açıklama                                                        |
| ------------------ | --------------------------------------------------------------- |
| `GEOCODE_FAILED`   | Adres koordinata çevrilemedi (daha detaylı adres gerekli)      |
| `NO_PARKING_FOUND` | 8 km yarıçap içinde otopark bulunamadı                         |
| `INVALID_PARAMETERS` | Ne `query` ne de `lat`+`lon` parametreleri verilmedi         |

---

## 🗺️ Google Maps Entegrasyonu

Her yanıt şunları içerir:

- **Hedef lokasyon linki**: `target.google_maps_link`
- **Otopark lokasyon linki**: `best.google_maps_link`

Linkler Google Maps'te tek tıkla açılır: `https://www.google.com/maps/search/?api=1&query=LAT,LON`

---

## 📊 Kullanılan Teknolojiler

- **FastAPI**: Hızlı REST API framework
- **Geopy**: Geocoding (Nominatim)
- **Requests**: HTTP istekleri (İBB API)
- **Haversine**: Koordinat mesafe hesaplama
- **Uvicorn**: ASGI server

---

## 🎯 Örnek Kullanım Senaryoları

### 1. Web/Mobile Uygulama Entegrasyonu

```javascript
// Frontend (React/Vue/Angular)
fetch('http://localhost:8000/nearest-parking?query=Kadıköy')
  .then(res => res.json())
  .then(data => {
    console.log(`En yakın: ${data.best.name} - ${data.best.distance_m}m`);
    window.open(data.best.google_maps_link); // Navigasyon
  });
```

### 2. GPS Koordinatı ile Anlık Sorgu

```python
import requests

# Kullanıcının mevcut GPS lokasyonu
my_lat, my_lon = 41.0082, 28.9784

response = requests.get(
    "http://localhost:8000/nearest-parking",
    params={"lat": my_lat, "lon": my_lon}
)

data = response.json()
if data["ok"]:
    print(f"En yakın otopark: {data['best']['name']}")
    print(f"Mesafe: {data['best']['distance_m']} metre")
```

---

## 🔐 Güvenlik Notları

- ✅ Sadece **otopark kategorileri** (215, 366, 367) sorgulanır
- ✅ Koordinat validasyonu (lat: -90/+90, lon: -180/+180)
- ✅ CORS tüm origin'lere açık (üretimde kısıtlanmalı)
- ⚠️ **Rate limiting yok** (Nominatim 1 req/sec limiti var, production'da dikkat!)

---

## 🚀 Production Deployment Önerileri

### 1. Geocoding Cache

Nominatim'in rate limit'ini aşmamak için sık sorgulanan adresleri cache'le:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def geocode_cached(query: str):
    return geocode(query)
```

### 2. Environment Variables

API anahtarları için:

```bash
export IBB_API_KEY="your-key-here"
export GEOCODING_PROVIDER="google"  # veya "nominatim"
```

### 3. Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t istanbul-parking-finder .
docker run -p 8000:8000 istanbul-parking-finder
```

---

## 📝 Lisans

MIT License - Hackathon projesi

---

## 🤝 Katkıda Bulunma

1. Fork'la
2. Feature branch oluştur (`git checkout -b feature/amazing`)
3. Commit'le (`git commit -m 'Harika özellik ekledim'`)
4. Push'la (`git push origin feature/amazing`)
5. Pull Request aç

---

## 📧 İletişim

Sorular için: [GitHub Issues](https://github.com/your-repo/issues)

**Geliştirici**: İBB Hackathon 2025 Ekibi 🚀
