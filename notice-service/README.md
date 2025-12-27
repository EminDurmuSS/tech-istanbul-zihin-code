# İBB Trafik Duyuruları API Servisi

İstanbul Büyükşehir Belediyesi'nin trafik duyurularını otomatik olarak çeken ve yapılandırılmış JSON formatında sunan FastAPI tabanlı servis.

## 🚀 Özellikler

- **Otomatik Veri Çekme**: Her 60 saniyede bir İBB API'sinden güncel trafik duyurularını çeker
- **Yapılandırılmış Veri**: GeoJSON formatındaki karmaşık veriyi temiz, düz JSON formatına dönüştürür
- **Türkçe Karakter Desteği**: UTF-8 encoding ile Türkçe karakterleri doğru şekilde işler
- **RESTful API**: Standart HTTP GET endpoint ile kolay entegrasyon
- **Modüler Yapı**: Diğer Python projelerine import edilebilir

## 📋 Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)

## 🔧 Kurulum

1. **Sanal ortam oluştur ve aktifleştir:**
```bash
cd ibb_bot
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows
```

2. **Bağımlılıkları yükle:**
```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

### API Sunucusu Olarak

**Sunucuyu başlat:**
```bash
python -m uvicorn ibb_notice_service:app --host 0.0.0.0 --port 8001
```

**Arka planda çalıştırma:**
```bash
nohup python -m uvicorn ibb_notice_service:app --host 0.0.0.0 --port 8001 > server.log 2>&1 &
```

**API'ye istek at:**
```bash
curl http://localhost:8001/duyurular
```

### Python Modülü Olarak

```python
from ibb_notice_service import get_announcements

# Güncel duyuruları al
announcements = get_announcements()

if announcements:
    for announcement in announcements:
        print(f"{announcement.title} - {announcement.description}")
```

## 📊 API Endpoint

### GET `/duyurular`

İBB'den çekilen güncel trafik duyurularını döndürür.

**Response Format:**
```json
[
  {
    "id": 1395752,
    "title": "D100 Haramidere-Ambarlı Yönü...",
    "title_en": "D100 Haramidere-Ambarlı direction...",
    "description": "D100 Haramidere-Ambarlı Yönü, orta şerit...",
    "description_en": "D100 Haramidere-Ambarlı Yönü right lane...",
    "category": 16,
    "priority": 1,
    "start_date": "2025-12-27T12:07:36",
    "end_date": "2025-12-27T13:37:00",
    "camera_id": 155,
    "link": "",
    "coordinates": {
      "latitude": 40.99989204,
      "longitude": 28.69090282
    },
    "time_diff": 35
  }
]
```

**Response Fields:**
- `id`: Duyuru benzersiz kimliği
- `title`: Türkçe başlık
- `title_en`: İngilizce başlık
- `description`: Türkçe açıklama
- `description_en`: İngilizce açıklama
- `category`: Duyuru kategorisi (16: Kaza, 17: Bakım-Onarım, 32: Arıza)
- `priority`: Öncelik seviyesi
- `start_date`: Başlangıç tarihi
- `end_date`: Bitiş tarihi
- `camera_id`: İlgili kamera ID'si
- `link`: Detay linki (varsa)
- `coordinates`: Lokasyon bilgisi (enlem/boylam)
- `time_diff`: Dakika cinsinden geçen süre

## ⚙️ Yapılandırma

`ibb_notice_service.py` dosyasında aşağıdaki sabitler değiştirilebilir:

```python
POLLING_INTERVAL = 60  # Veri çekme aralığı (saniye)
IBB_API_URL = "..."    # İBB API URL'i
```

## 📁 Proje Yapısı

```
ibb_bot/
├── ibb_notice_service.py      # Ana servis dosyası
├── requirements.txt    # Python bağımlılıkları
├── README.md          # Bu dosya
├── venv/              # Sanal ortam (oluşturulacak)
└── server.log         # Sunucu logları (oluşturulacak)
```

## 🔍 Veri Modeli

```python
class Coordinates:
    latitude: float
    longitude: float

class Announcement:
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
```

## 🐛 Hata Ayıklama

**Sunucu loglarını kontrol et:**
```bash
tail -f server.log
```

**Sunucu çalışıyor mu kontrol et:**
```bash
ps aux | grep uvicorn
```

**Sunucuyu durdur:**
```bash
pkill -f "uvicorn ibb_notice_service:app"
```

## 📝 Notlar

- Servis başlatıldığında ilk veri çekme işlemi hemen başlar
- Veri her 60 saniyede bir otomatik güncellenir
- İlk istek sırasında veri henüz çekilmemişse, servis hemen çekmeye çalışır
- Türkçe karakterler UTF-8 encoding ile korunur
- API yanıtları `application/json; charset=utf-8` formatındadır

## 🔐 Güvenlik

- API şu anda kimlik doğrulama gerektirmez
- Production ortamında reverse proxy (nginx) kullanılması önerilir
- Rate limiting eklenebilir

## 📞 Destek

Sorularınız için proje sahibi ile iletişime geçin.

## 📄 Lisans

Bu proje İBB'nin açık API'sini kullanmaktadır. Ticari kullanım öncesinde İBB ile iletişime geçilmesi önerilir.
