# Metro Agent API Kullanım Kılavuzu

## 🎯 Genel Bakış

Metro Agent, kullanıcı sorularını analiz edip en uygun Metro İstanbul API'lerini otomatik olarak çağırır ve zenginleştirilmiş yanıtlar üretir.

## 🔄 İstek Akışı

```
Frontend → POST /message → Metro Agent → Intent Classification
                                ↓
                        Uygun Modül Seçimi
                                ↓
                     Metro İstanbul API Çağrıları (Paralel)
                                ↓
                        Veri Zenginleştirme
                                ↓
                     Kullanıcıya Formatlı Yanıt
```

## 📡 API Endpoint

### POST /message

Kullanıcı mesajını işler ve yanıt döner.

**Request:**
```json
{
  "message": "Kadıköy istasyonunda asansör çalışmıyor",
  "channel": "web",
  "user_id": "user123",
  "session_id": "session456"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Arıza bildirimi kaydedildi!\n\nTakip Numaranız: MET-20251227-151011...",
  "intent": "fault_report",
  "confidence": 0.95,
  "entities": {
    "station": "Kadıköy",
    "line": "M4",
    "equipment": "Asansör"
  },
  "report_id": "MET-20251227-151011",
  "quick_replies": [],
  "actions": ["create_ticket", "notify_department"],
  "processing_time_ms": 1847,
  "timestamp": "2025-12-27T15:10:11.592038"
}
```

## 🎭 Intent Türleri

Sistem şu intent'leri otomatik tanır:

### 1. FAULT_REPORT (Arıza Bildirimi)
**Örnek Mesajlar:**
- "Kadıköy'de asansör bozuk"
- "Mecidiyeköy istasyonunda turnike çalışmıyor"
- "Şişli-Mecidiyeköy'de klima arızalı"

**Kullanılan API'ler:**
- `GET /GetFaultyEquipments` - Mevcut arıza kontrolü
- `GET /GetFailureTypes` - Arıza tipleri
- `GET /GetTechnicalObjectTypes` - Teknik nesneler
- `GET /GetStations` - İstasyon bilgisi
- `GET /GetLines` - Hat bilgisi
- `GET /GetServiceStatuses` - Hizmet durumu

**Çıktı:**
- Mevcut arıza varsa → Arıza durumu bilgisi
- Yeni arıza → Detaylı rapor + İBB için JSON

---

### 2. SERVICE_STATUS (Hat Durumu)
**Örnek Mesajlar:**
- "M4'te sefer var mı?"
- "M1 hattı çalışıyor mu?"
- "Şu an metro durumu ne?"

**Kullanılan API'ler:**
- `GET /GetServiceStatuses`
- `GET /GetLines`
- `GET /GetAnnouncements`

**Çıktı:**
```
M4 Hat Durumu

Durum: Normal
Seferler düzenli şekilde devam etmektedir.

İlk sefer: 06:00
Son sefer: 00:30
```

---

### 3. TIMETABLE (Sefer Saatleri)
**Örnek Mesajlar:**
- "Kadıköy'den ilk sefer saat kaçta?"
- "Mecidiyeköy'den son metro ne zaman?"
- "M2 sefer saatleri"

**Kullanılan API'ler:**
- `POST /GetTimeTable`
- `GET /GetStations`
- `GET /GetDirections`
- `POST /GetDirectionsByLineIdAndStationId`

**Çıktı:**
```
Kadıköy İstasyonu Sefer Saatleri

Yön: Tavşantepe
İlk Sefer: 06:00
Son Sefer: 00:30
Sefer Aralığı: 5-7 dakika
```

---

### 4. DIRECTION_HELP (Yön Tarifi)
**Örnek Mesajlar:**
- "Kadıköy'den Taksim'e nasıl giderim?"
- "Mecidiyeköy'e hangi hattan gidilir?"
- "4.Levent'e yol tarifi"

**Kullanılan API'ler:**
- `GET /GetLineAndStationSearch/{Text}`
- `GET /GetStations`
- `GET /GetLines`
- `POST /GetStationBetweenTime`
- `GET /GetDirections`

**Çıktı:**
```
Kadıköy → Taksim Rotası

1. Kadıköy'den M4 ile binGeneral Pratik Kullanım:in
2. Ayrılık Çeşmesi'nde inin
3. M2'ye aktarma yapın (aynı istasyon)
4. Taksim'de inin

Tahmini Süre: ~35 dakika
Aktarma: 1 (Ayrılık Çeşmesi)
```

---

### 5. FARE_INFO (Ücret Bilgisi)
**Örnek Mesajlar:**
- "Metro ücreti ne kadar?"
- "İstanbulkart ile ne kadar?"
- "Bilet fiyatları"

**Kullanılan API'ler:**
- `GET /GetTicketPrice/tr`

**Çıktı:**
```
Metro Ücretlendirme

İstanbulkart: 12.80 TL
Tek Kullanımlık Jeton: 17.20 TL

Aktarmalı yolculuklarda indirim uygulanır.
```

---

### 6. ACCESSIBILITY (Erişilebilirlik)
**Örnek Mesajlar:**
- "Kadıköy'de asansör var mı?"
- "Mecidiyeköy engelli erişimi"
- "Bebek arabası ile girebilir miyim?"

**Kullanılan API'ler:**
- `GET /GetStations`
- `GET /GetStationById/{LineId}`

**Çıktı:**
```
Kadıköy İstasyonu Erişilebilirlik

Asansör: 2 adet
Yürüyen Merdiven: 4 adet
Engelli WC: Var
Bebek Bakım Odası: Var
```

---

### 7. ANNOUNCEMENTS (Duyurular)
**Örnek Mesajlar:**
- "Son duyurular neler?"
- "Metro duyuruları"
- "Güncel haberler"

**Kullanılan API'ler:**
- `GET /GetAnnouncements/tr`
- `GET /GetAnnouncementsByLine` (hat bazlı)

---

### 8. GENERAL_FAQ (Genel Sorular)
**Örnek Mesajlar:**
- "İstanbulkart nereden alınır?"
- "Kayıp eşya bürosu nerede?"
- "Müşteri hizmetleri telefon numarası"

**Kullanılan API'ler:**
- `GET /FrequentlyAskedQuestions`

---

## 🔧 Arıza Yönetimi Detayları

### Mevcut Arıza Kontrolü
```
1. Kullanıcı: "Kadıköy'de asansör bozuk"
   ↓
2. Entity Extraction:
   - station: "Kadıköy"
   - equipment: "Asansör"
   ↓
3. API Call: GET /GetFaultyEquipments
   ↓
4. Eşleştirme:
   - İstasyon adı eşleşmesi (fuzzy)
   - Ekipman tipi eşleşmesi (normalize)
   ↓
5a. Eşleşme Var:
    → "Bu arıza sistemimizde kayıtlı"
    → Arıza ID, durum, tahmini çözüm

5b. Eşleşme Yok:
    → Yeni arıza kaydı oluştur
    → Zenginleştirilmiş rapor
```

### Yeni Arıza Kaydı
```
1. Entity Extraction (AI)
2. Arıza Sınıflandırma:
   - Kategori belirleme (ELEVATOR, ESCALATOR, etc.)
   - Öncelik belirleme (CRITICAL, HIGH, MEDIUM, LOW)
   - Departman routing
   - SLA hesaplama
3. Veri Zenginleştirme:
   - İstasyon metadata
   - Hat durumu
   - Alternatif yollar
   - Erişilebilirlik etkisi
   - Yolcu etki tahmini
4. Rapor Oluşturma:
   - Kullanıcı yanıtı (kısa)
   - İBB raporu (detaylı)
   - JSON veri (entegrasyon)
```

## 📊 API Kullanım İstatistikleri

### Ortalama API Çağrı Sayıları (Intent Başına)

| Intent | API Çağrı | Paralel | Süre |
|--------|-----------|---------|------|
| FAULT_REPORT | 5-6 | ✓ | ~2s |
| SERVICE_STATUS | 2-3 | ✓ | ~1s |
| TIMETABLE | 3-4 | ✓ | ~1.5s |
| DIRECTION_HELP | 4-5 | ✓ | ~2s |
| FARE_INFO | 1 | - | ~0.5s |
| ACCESSIBILITY | 1-2 | - | ~0.8s |
| ANNOUNCEMENTS | 1 | - | ~0.6s |
| GENERAL_FAQ | 1 | - | ~0.5s |

## 🚀 Performans Optimizasyonları

### 1. Paralel API Çağrıları
```python
# Kötü ❌
stations = await metro.get_stations()
lines = await metro.get_lines()
statuses = await metro.get_service_statuses()

# İyi ✓
stations, lines, statuses = await asyncio.gather(
    metro.get_stations(),
    metro.get_lines(),
    metro.get_service_statuses()
)
```

### 2. Response Caching
```python
# İstasyon ve hat verileri 1 saat cache
# Arıza verileri cache yok (real-time)
```

### 3. Graceful Degradation
```python
# API hata verirse boş liste dön, crash etme
try:
    faults = await metro.get_faulty_equipments()
except:
    faults = []  # Devam et
```

## 🎨 Frontend Entegrasyonu

### Örnek Frontend Kodu (React)
```typescript
const sendMessage = async (message: string) => {
  const response = await fetch('/api/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      channel: 'web',
      user_id: getUserId(),
      session_id: getSessionId()
    })
  });

  const data = await response.json();

  // Yanıtı göster
  displayMessage(data.response);

  // Quick replies varsa göster
  if (data.quick_replies?.length > 0) {
    displayQuickReplies(data.quick_replies);
  }

  // Rapor ID varsa sakla
  if (data.report_id) {
    localStorage.setItem('last_report_id', data.report_id);
  }
};
```

### WebSocket Alternatifi (Real-time)
```typescript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'fault_update') {
    // Arıza durumu güncellendi
    updateFaultStatus(data.report_id, data.status);
  }
};
```

## 🔐 Güvenlik

### Rate Limiting
```python
# Her kullanıcı için 10 req/dakika
# Aşarsa 429 Too Many Requests
```

### Input Validation
```python
# Max message length: 500 karakter
# Zararlı karakterler filtrele
# SQL injection koruması
```

## 📈 Monitoring

### Loglar
```python
# Her istek loglanır:
- Intent tipi
- Confidence score
- İşlem süresi
- Kullanılan API'ler
- Hata durumları
```

### Metrikler
```python
# Prometheus metrikleri:
- request_total
- request_duration_seconds
- intent_distribution
- api_call_duration
- error_rate
```

## 🐛 Hata Yönetimi

### Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| 400 | Geçersiz istek | Mesaj formatını kontrol et |
| 429 | Çok fazla istek | Rate limit aşıldı, bekle |
| 500 | Sunucu hatası | Retry veya destek |
| 503 | Servis kullanılamaz | Metro API down |

### Retry Stratejisi
```python
# Exponential backoff
# 1. deneme: hemen
# 2. deneme: 1s sonra
# 3. deneme: 2s sonra
# 4. deneme: 4s sonra
# Vazgeç
```

## 📝 Geliştirme Notları

### Yeni Intent Ekleme
1. `IntentType` enum'a ekle
2. Intent classifier'a örnek ekle
3. Yeni modül oluştur
4. `MetroAgent._route_intent`'e ekle
5. Test yaz

### Yeni API Endpoint Ekleme
1. `MetroAPIClient`'a method ekle
2. Dokümantasyonu güncelle
3. İlgili modülde kullan
4. Test yaz

## 🎯 Best Practices

1. **Her zaman mevcut arıza kontrolü yap**
2. **API çağrılarını paralel yap**
3. **Hataları gracefully handle et**
4. **Kullanıcıya her zaman yanıt ver**
5. **Logla her şeyi**
6. **Cache akıllıca kullan**
7. **Rate limit'i aşma**
8. **Güvenliği unutma**

## 📞 Destek

Sorularınız için:
- **E-posta:** support@metro.istanbul
- **Telefon:** 153
- **Döküman:** https://api.metro.istanbul/docs
