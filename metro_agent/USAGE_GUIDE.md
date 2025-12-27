# Metro Agent - Kullanım Kılavuzu

## 📖 İçindekiler

1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Sistem Özellikleri](#sistem-özellikleri)
3. [Kullanım Senaryoları](#kullanım-senaryoları)
4. [API Entegrasyonu](#api-entegrasyonu)
5. [Arıza Rapor Sistemi](#arıza-rapor-sistemi)
6. [Demo & Test](#demo--test)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
# 1. Repository'yi klonlayın
cd metro_agent

# 2. Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyin
```

### .env Dosyası

```bash
# OpenRouter (LLM)
OPENROUTER_API_KEY=your_api_key_here
LLM_MODEL=anthropic/claude-3-haiku
LLM_TEMPERATURE=0.2

# Metro İstanbul API
METRO_API_BASE_URL=https://api.ibb.gov.tr/MetroIstanbul/api/MetroMobile/V2
METRO_API_KEY=  # Opsiyonel

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### İlk Çalıştırma

```bash
# API Server'ı başlatın
python -m src.api.endpoints

# Veya uvicorn ile
uvicorn src.api.endpoints:app --reload --port 8000
```

### İlk Test

```bash
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "M4 hattı çalışıyor mu?",
    "channel": "web"
  }'
```

---

## 🎯 Sistem Özellikleri

### 1. Akıllı Intent Tanıma

Sistem, kullanıcı mesajını analiz ederek niyeti otomatik belirler:

```
✅ Arıza Bildirimi
✅ Arıza Sorgulama
✅ Hizmet Durumu
✅ Sefer Saatleri
✅ Yön Tarifi
✅ Ücret Bilgisi
✅ Erişilebilirlik
✅ Duyurular
✅ Genel Sorular
```

### 2. Otomatik API Yönlendirme

Her sorgu için en uygun API'leri otomatik seçer ve paralel çağırır.

### 3. Zenginleştirilmiş Arıza Raporları

İBB için kapsamlı, detaylı arıza raporları oluşturur:
- Öncelik değerlendirmesi
- Risk analizi
- Yolcu etki tahmini
- Aksiyon planı
- Narrative rapor (LLM-generated)

### 4. Performans Optimizasyonu

- Paralel API çağrıları
- 60 saniye cache
- Graceful degradation
- Fallback mekanizmaları

---

## 💼 Kullanım Senaryoları

### Senaryo 1: Arıza Bildirimi

**Kullanıcı:**
```
"Kadıköy istasyonunda asansör çalışmıyor"
```

**Sistem:**
1. Intent tespit: `FAULT_REPORT`
2. Entity extraction: `{station: "Kadıköy", equipment: "asansör"}`
3. Mevcut arıza kontrolü (`GetFaultyEquipments`)
4. Yeni arıza ise:
   - Sınıflandırma (kategori, öncelik, departman)
   - API'lerden veri toplama (istasyon bilgisi, hat durumu, vb.)
   - Zenginleştirilmiş rapor oluşturma
   - İBB için JSON çıktı

**Agent Yanıtı:**
```
Arıza bildirimi alındı! 🚇

📋 Takip Numaranız: MET-20251227-153042

📍 Konum: Kadıköy
🔧 Arıza: Asansör
⏱️ Tahmini Çözüm: 4 saat
📌 Departman: Asansör Bakım Müdürlüğü
⚠️ Engelli erişimi etkileniyor

🔄 Alternatifler:
• Yürüyen merdiven kullanılabilir
• Merdiven kullanılabilir

Teknik ekibimiz bilgilendirildi.

Başka yardımcı olabilir miyim?
```

**İBB İçin Rapor:**
```json
{
  "report_id": "MET-20251227-153042",
  "timestamp": "2025-12-27T15:30:42",
  "status": "NEW",
  "location": {
    "line": "M4",
    "station": "Kadıköy",
    "station_details": {
      "Lift": 2,
      "Escolator": 4,
      "WC": true,
      "BabyRoom": true
    }
  },
  "fault": {
    "equipment_type": "Asansör",
    "category": "ELEVATOR",
    "problem_description": "Çalışmıyor"
  },
  "priority": {
    "level": "MEDIUM",
    "reason": "Erişilebilirlik etkileniyor, alternatif mevcut",
    "sla_hours": 4,
    "safety_risk": "DÜŞÜK",
    "service_interruption": "PERFORMANS DÜŞÜKLÜĞÜ"
  },
  "impact": {
    "passenger_impact": "ORTA - Erişilebilirlik etkileniyor",
    "accessibility_impact": "YÜKSEK - Engelli erişimi kesintiye uğramış",
    "alternatives": ["Yürüyen merdiven", "Merdiven"],
    "estimated_affected_passengers": "50,000+"
  },
  "routing": {
    "target_department": "Asansör Bakım Müdürlüğü",
    "notifications": [
      "Asansör Bakım Müdürlüğü",
      "Operasyon Merkezi"
    ]
  },
  "actions": [
    "Teknik ekip 1 saat içinde müdahale etmeli",
    "Alternatif yollar için yönlendirme yapılmalı",
    "Asansör Bakım Müdürlüğü bilgilendirildi",
    "Durum takip sistemine kaydedildi",
    "Mobil uygulama ve web sitesinde duyuru yapılmalı"
  ],
  "context": {
    "line_status": {"Status": "Normal"},
    "similar_fault_count": 0
  },
  "narrative_report": "...detaylı rapor metni..."
}
```

### Senaryo 2: Hizmet Durumu

**Kullanıcı:**
```
"M4'te sefer var mı?"
```

**Sistem:**
1. Intent: `SERVICE_STATUS`
2. Entity: `{line: "M4"}`
3. API çağrıları: `GetServiceStatuses`, `GetLines`
4. Yanıt formatla

**Agent Yanıtı:**
```
🚇 M4 Hat Durumu

✅ Durum: Normal
Seferler düzenli şekilde devam etmektedir.

🕐 İlk Sefer: 06:00
🕛 Son Sefer: 00:30
⏱️ Sefer Aralığı: 5-7 dakika

Başka yardımcı olabilir miyim?
```

### Senaryo 3: Yön Tarifi

**Kullanıcı:**
```
"Kadıköy'den Taksim'e nasıl giderim?"
```

**Sistem:**
1. Intent: `DIRECTION_HELP`
2. Entity: `{station: "Kadıköy", destination: "Taksim"}`
3. API'ler: `GetStations`, `GetLines`, `GetDirections`, `GetStationBetweenTime`
4. Rota hesapla

**Agent Yanıtı:**
```
📍 Kadıköy → Taksim Rotası

1️⃣ Kadıköy'den M4 (Tavşantepe yönü) ile binin
2️⃣ Ayrılık Çeşmesi'nde inin (8 durak, ~12 dk)
3️⃣ M2 hattına aktarma yapın (aynı istasyon)
4️⃣ M2 (Hacıosman yönü) ile Taksim'e gidin (4 durak, ~7 dk)

⏱️ Toplam Süre: ~25 dakika
🔄 Aktarma: 1 (Ayrılık Çeşmesi)
💳 Ücret: 12.80 TL (İstanbulkart, aktarma indirimi ile)

Başka yardımcı olabilir miyim?
```

### Senaryo 4: Erişilebilirlik

**Kullanıcı:**
```
"Mecidiyeköy istasyonunda asansör var mı?"
```

**Sistem:**
1. Intent: `ACCESSIBILITY`
2. Entity: `{station: "Mecidiyeköy"}`
3. API: `GetStations`

**Agent Yanıtı:**
```
♿ Mecidiyeköy İstasyonu Erişilebilirlik

✅ Asansör: 3 adet
✅ Yürüyen Merdiven: 6 adet
✅ Engelli WC: Var
✅ Bebek Bakım Odası: Var
✅ Mescit: Var

📍 Tüm giriş/çıkışlar engelli erişimine uygundur.

Başka yardımcı olabilir miyim?
```

### Senaryo 5: Acil Durum (Kritik Arıza)

**Kullanıcı:**
```
"ACİL! Taksim'de yangın alarmı çalıyor!"
```

**Sistem:**
1. Intent: `FAULT_REPORT`
2. Öncelik tespiti: **CRITICAL**
3. Acil protokol devreye girer

**Agent Yanıtı:**
```
⚠️ ACİL DURUM - Bildiriminiz kaydedildi!

📋 Takip No: MET-20251227-154500
🚨 ÖNCELİK: KRİTİK

📍 Konum: Taksim İstasyonu
⚡ Durum: Yangın alarmı aktif

✅ Yapılanlar:
• Güvenlik ekibi anında bilgilendirildi
• Teknik ekip yola çıkarıldı
• Operasyon merkezi devrede
• İstasyon yönetimi uyarıldı

⏱️ Müdahale Süresi: < 15 dakika

Güvenliğiniz için lütfen istasyon personelinin yönlendirmelerine uyun.

ACİL DURUM: 155
```

---

## 🔌 API Entegrasyonu

### REST API

#### Endpoint: POST /message

**Request:**
```json
{
  "message": "string",
  "channel": "web|phone|app",
  "user_id": "string (optional)",
  "session_id": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Agent yanıtı...",
  "intent": "fault_report",
  "confidence": 0.95,
  "entities": {
    "station": "Kadıköy",
    "equipment": "Asansör"
  },
  "report_id": "MET-20251227-153042",
  "actions": ["create_ticket", "notify_department"],
  "processing_time_ms": 1847,
  "timestamp": "2025-12-27T15:30:42"
}
```

### Python SDK

```python
from src.agent.metro_agent import MetroAgent

# Agent'ı başlat
agent = MetroAgent()

# Mesaj gönder
response = await agent.process_message(
    message="Kadıköy'de asansör bozuk",
    user_id="user_123",
    channel="web"
)

# Yanıt
print(response.response.text)
print(f"Intent: {response.intent.type.value}")
print(f"Report ID: {response.internal_report.report_id}")
```

### JavaScript/TypeScript

```typescript
const sendMessage = async (message: string) => {
  const response = await fetch('http://localhost:8000/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      channel: 'web',
      user_id: getUserId()
    })
  });

  const data = await response.json();
  return data;
};

// Kullanım
const result = await sendMessage("M4 hattı çalışıyor mu?");
console.log(result.response);
```

---

## 📊 Arıza Rapor Sistemi

### Rapor Yapısı

Metro Agent, her arıza bildirimi için **iki çıktı** üretir:

1. **Kullanıcı Yanıtı**: Kısa, anlaşılır, takip numaralı
2. **İBB Raporu**: Detaylı, zenginleştirilmiş, JSON formatında

### Rapor Bölümleri

#### 1. Özet Bilgiler
```
- Rapor ID
- Durum (NEW, IN_PROGRESS, RESOLVED)
- Öncelik (CRITICAL, HIGH, MEDIUM, LOW)
- Tahmini Çözüm Süresi
- Hedef Departman
```

#### 2. Konum Detayları
```
- Hat
- İstasyon
- Konum Detayı (giriş, peron, vb.)
- İstasyon Özellikleri (asansör sayısı, vb.)
```

#### 3. Arıza Bilgileri
```
- Ekipman Türü
- Arıza Kategorisi
- Arıza Tipi
- Teknik Nesne
- Sorun Açıklaması
```

#### 4. Öncelik Değerlendirmesi
```
- Öncelik Seviyesi
- Gerekçe
- SLA (Hizmet Seviyesi Anlaşması)
- Can Güvenliği Riski
- Hizmet Kesintisi Durumu
```

#### 5. Etki Analizi
```
- Yolcu Etkisi
- Erişilebilirlik Etkisi
- Alternatif Erişim Yolları
- Tahmini Etkilenen Yolcu Sayısı
```

#### 6. Bağlam
```
- Hat Durumu
- Benzer Arızalar (varsa)
- İlgili Duyurular
```

#### 7. Aksiyon Planı
```
1. Acil Müdahale
2. Teknik Değerlendirme
3. Yolcu Yönlendirme
4. İletişim
5. Takip
```

#### 8. Narrative Rapor
LLM tarafından oluşturulan profesyonel rapor metni

### Rapor Erişimi

```python
# Agent yanıtından rapor al
response = await agent.process_message("Kadıköy'de asansör bozuk")

# Kullanıcı yanıtı
user_response = response.response.text

# İBB raporu (internal)
if response.internal_report:
    report_data = response.internal_report.data
    report_id = response.internal_report.report_id

    # JSON olarak kaydet
    import json
    with open(f"reports/{report_id}.json", "w") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
```

---

## 🧪 Demo & Test

### Kapsamlı Demo

```bash
# Tüm senaryoları çalıştır
python COMPREHENSIVE_DEMO.py all

# İnteraktif mod
python COMPREHENSIVE_DEMO.py interactive

# Tek senaryo
python COMPREHENSIVE_DEMO.py S1
```

### Demo Senaryoları

```
S1  - Arıza Bildirimi (Asansör)
S2  - Hizmet Durumu
S3  - Sefer Saatleri
S4  - Yön Tarifi
S5  - Erişilebilirlik
S6  - Ücret Bilgisi
S7  - Arıza Sorgulama
S8  - Komplex Soru
S9  - Kritik Arıza (Acil)
S10 - Genel FAQ
```

### Manuel Test

```python
import asyncio
from src.agent.metro_agent import MetroAgent

async def test():
    agent = MetroAgent()

    # Test mesajları
    messages = [
        "M4'te sefer var mı?",
        "Kadıköy'de asansör bozuk",
        "Taksim'e nasıl giderim?"
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        response = await agent.process_message(msg)
        print(f"Agent: {response.response.text}")

asyncio.run(test())
```

---

## 🔧 Troubleshooting

### Problem: LLM API Hatası

**Belirti:** `OpenRouter API error` veya `LLM classification failed`

**Çözüm:**
1. `.env` dosyasında `OPENROUTER_API_KEY` kontrol edin
2. API key geçerli mi kontrol edin
3. Fallback keyword-based classification devreye girer (sistem çalışır)

### Problem: Metro API Zaman Aşımı

**Belirti:** `Metro API timeout`

**Çözüm:**
1. İnternet bağlantısını kontrol edin
2. `.env`'de `METRO_API_TIMEOUT` değerini artırın (örn. 60)
3. Sistem gracefully degrade olur (boş liste döner)

### Problem: Yavaş Yanıt

**Belirti:** 5+ saniye işlem süresi

**Çözüm:**
1. LLM modelini haiku olarak ayarlayın: `LLM_MODEL=anthropic/claude-3-haiku`
2. Cache'in çalıştığından emin olun
3. Log'larda hangi API'lerin yavaş olduğunu kontrol edin

### Problem: Intent Yanlış Tespit Ediliyor

**Belirti:** Yanlış intent sınıflandırması

**Çözüm:**
1. `LLM_TEMPERATURE` değerini düşürün (örn. 0.1)
2. Daha iyi bir LLM modeli kullanın (claude-3.5-sonnet)
3. Intent examples'ı güncelleyin

### Problem: Arıza Raporu Oluşturulmuyor

**Belirti:** `Enhanced report creation failed`

**Çözüm:**
1. Log'ları kontrol edin
2. Fallback minimal report kullanılır
3. LLM ve API bağlantılarını kontrol edin

---

## 📞 Destek

### Dokümantasyon
- [Sistem Mimarisi](SYSTEM_ARCHITECTURE.md)
- [API Kullanım Kılavuzu](API_USAGE_GUIDE.md)
- [Kod Dokümantasyonu](src/)

### İletişim
- **E-posta:** support@metro.istanbul
- **Telefon:** 153 (İBB Çözüm Merkezi)
- **Web:** metro.istanbul

### Issue Reporting
GitHub Issues üzerinden rapor edin:
- Bug reports
- Feature requests
- Documentation improvements

---

**Versiyon:** 1.0.0
**Son Güncelleme:** 2025-12-27
