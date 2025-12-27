# Metro İstanbul Arıza Servisi

Metro İstanbul'un arıza sayfasından canlı veri çeken ve REST API olarak sunan FastAPI servisi.

## 🚀 Özellikler

- ✅ Canlı arıza verisi çekme
- ✅ HTML parsing ve JSON dönüşümü
- ✅ RESTful API endpoints
- ✅ Hat, istasyon ve ekipman bazında filtreleme
- ✅ Otomatik API dokümantasyonu (Swagger/ReDoc)
- ✅ CORS desteği

## 📋 Gereksinimler

- Python 3.8+
- pip

## 🔧 Kurulum

1. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## 🏃 Çalıştırma

### Geliştirme Modu
```bash
python main.py
```

veya

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Modu
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Servis `http://localhost:8000` adresinde çalışacaktır.

## 📚 API Endpoints

### Genel

- `GET /` - API bilgileri
- `GET /health` - Sağlık kontrolü
- `GET /docs` - Swagger UI dokümantasyonu
- `GET /redoc` - ReDoc dokümantasyonu

### Arıza Verileri

#### Tüm Arızalar
```bash
GET /api/arizalar
```

**Query Parametreleri:**
- `hat` - Hat kodu filtresi (örn: M1A, M2)
- `istasyon` - İstasyon adı filtresi
- `ekipman` - Ekipman türü filtresi
- `durum` - Durum filtresi

**Örnek:**
```bash
curl "http://localhost:8000/api/arizalar?hat=M2"
curl "http://localhost:8000/api/arizalar?istasyon=Taksim"
curl "http://localhost:8000/api/arizalar?ekipman=Asansör"
```

#### Özet Bilgiler
```bash
GET /api/ozet
```

**Örnek:**
```bash
curl http://localhost:8000/api/ozet
```

#### Hat Bazında Arızalar
```bash
GET /api/hat/{hat_kodu}
```

**Örnek:**
```bash
curl http://localhost:8000/api/hat/M2
curl http://localhost:8000/api/hat/T1
```

#### İstasyon Bazında Arızalar
```bash
GET /api/istasyon/{istasyon_adi}
```

**Örnek:**
```bash
curl http://localhost:8000/api/istasyon/Taksim
curl http://localhost:8000/api/istasyon/Kadıköy
```

#### Tüm Hatları Listele
```bash
GET /api/hatlar
```

**Örnek:**
```bash
curl http://localhost:8000/api/hatlar
```

## 📊 Response Formatı

### Başarılı Response
```json
{
  "success": true,
  "error": null,
  "data": {
    "ozet": {
      "toplam_ariza_sayisi": 126,
      "cekme_tarihi": "2025-12-27T15:45:00.000000",
      "hat_bazinda_dagilim": {
        "M2": 42,
        "M9": 18,
        "M3": 15
      },
      "ekipman_bazinda_dagilim": {
        "Yürüyen Merdiven": 99,
        "Asansör": 13
      },
      "durum_bazinda_dagilim": {
        "Arıza": 42,
        "Tasarruf-Güvenlik": 73
      }
    },
    "arizalar": [
      {
        "ariza_id": "203001",
        "ariza_takip_no": "001003308746",
        "hat_kodu": "M7",
        "istasyon_id": "150",
        "istasyon_adi": "Alibeyköy",
        "ekipman_turu": "YURMERDVEN",
        "ekipman_turu_aciklama": "Yürüyen Merdiven",
        "ekipman_aciklama": "Peron 2 ' den batı biletholüne inen yürüyen merdiven",
        "durum": "Arıza",
        "ariza_nedeni": "Ariza",
        "tarih": "01.01.2026",
        "ref_char": "A"
      }
    ]
  }
}
```

### Hata Response
```json
{
  "success": false,
  "error": "Hata mesajı",
  "data": null
}
```

## 🧪 Test

### Scraper'ı Test Et
```bash
python scraper.py
```

### API'yi Test Et
```bash
# Tüm arızalar
curl http://localhost:8000/api/arizalar

# Özet
curl http://localhost:8000/api/ozet

# M2 hattı arızaları
curl http://localhost:8000/api/hat/M2

# Taksim istasyonu arızaları
curl http://localhost:8000/api/istasyon/Taksim
```

## 📁 Dosya Yapısı

```
ariza-service/
├── main.py              # FastAPI uygulaması
├── scraper.py           # HTML scraper
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

## 🔍 Veri Kaynağı

Veriler Metro İstanbul'un resmi web sitesinden çekilmektedir:
- URL: https://www.metro.istanbul/SeferDurumlari/Ariza/2

## ⚠️ Önemli Notlar

- Bu servis eğitim amaçlıdır
- Metro İstanbul'un resmi bir servisi değildir
- Veriler gerçek zamanlı olarak web sitesinden çekilir
- Rate limiting uygulanması önerilir

## 📝 Lisans

MIT License

## 👨‍💻 Geliştirici

Tech Istanbul - Zihin Code
