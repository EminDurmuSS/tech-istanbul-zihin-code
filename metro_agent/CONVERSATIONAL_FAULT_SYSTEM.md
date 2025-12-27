# Konuşmaya Dayalı Profesyonel Arıza Bildirimi Sistemi

## Genel Bakış

Bu sistem, kullanıcılardan arıza bildirimi alırken eksik bilgileri akıllıca sorgulayan, Metro İstanbul API'lerinden detaylı bilgi çekerek zenginleştiren ve profesyonel raporlar oluşturan bir konuşma yönetim sistemidir.

## Özellikler

### 1. **Multi-Turn Konuşma Yönetimi**
- Kullanıcıyla doğal dilde konuşarak eksik bilgileri toplar
- Her aşamada yalnızca gerekli bilgiyi sorar
- Kullanıcı deneyimini optimize eder

### 2. **Akıllı Bilgi Toplama**
Sistem şu bilgileri akıllıca toplar:
- ✅ **İstasyon**: İstasyon adını doğrular, API'den detaylı bilgi alır
- ✅ **Konum Detayı**: "Turnike katı ile cadde arası" gibi spesifik konum
- ✅ **Ekipman**: Arızalı ekipman türü (asansör, yürüyen merdiven, vb.)
- ✅ **Problem Açıklaması**: Sorunun ne olduğu

### 3. **API Entegrasyonu**
Sistem Metro İstanbul API'lerinden şu bilgileri çeker:

#### Kullanılan API'ler:
1. **GetStations** - Tüm istasyon bilgileri
2. **GetLineAndStationSearch** - İstasyon arama ve doğrulama
3. **GetLines** - Hat bilgileri
4. **GetFaultyEquipments** - Mevcut arıza kontrolü
5. **GetFaultDetails** - Arıza detayları
6. **GetFailureTypes** - Arıza tipleri sınıflandırması
7. **GetTechnicalObjectTypes** - Teknik nesne türleri
8. **GetServiceStatuses** - Hat servis durumları
9. **GetEquipments** - İstasyon ekipman listesi
10. **GetAnnouncementsByLine** - Hata ilgili duyurular

### 4. **Mevcut Arıza Kontrolü**
Yeni rapor oluşturmadan önce:
- Aynı istasyon, ekipman ve konumda mevcut arıza var mı kontrol eder
- Varsa mevcut arıza bilgilerini gösterir
- **Planlanan Servise Dönüş Tarihi** bilgisini sunar

### 5. **Profesyonel Rapor Oluşturma**
Rapor şunları içerir:

#### Rapor İçeriği:
```
═══════════════════════════════════════════════════════════════
1. ÖZET BİLGİLER
   - İstasyon, Hat, Konum Detayı, Ekipman, Açıklama

2. SINIFLANDIRMA
   - Arıza Tipi, Kategori, Teknik Nesne
   - Öncelik Seviyesi (CRITICAL/HIGH/MEDIUM/LOW)
   - Öncelik Gerekçesi

3. YÖNLENDİRME
   - Sorumlu Departman
   - Alt Birim

4. ZAMAN PLANLAMA
   - SLA Süresi
   - Tahmini Çözüm Tarihi

5. DETAYLI BİLGİLER
   - İstasyon Tesisleri (asansör sayısı, yürüyen merdiven, vb.)
   - Alternatif Çözümler
   - Erişilebilirlik Etkisi

6. KONUŞMA GEÇMİŞİ
   - Tüm kullanıcı mesajları
═══════════════════════════════════════════════════════════════
```

### 6. **Rapor Kaydetme**
- Her rapor `fault_reports/` klasörüne `.txt` dosyası olarak kaydedilir
- Dosya adı: `MET-YYYYMMDD-HHMMSS.txt`
- UTF-8 encoding ile Türkçe karakter desteği

## Kullanım Senaryosu

### Örnek Konuşma Akışı:

```
👤 KULLANICI:
"Bağcılar Meydan'dayım asansör çalışmıyor"

🤖 AGENT:
"📌 İstasyonun neresinde bir sorun var?
Lütfen daha detaylı konum belirtin:
• Giriş/Çıkış katı
• Turnike katı
• Peron katı..."

👤 KULLANICI:
"Turnike katı ile cadde arasındaki asansör"

🤖 AGENT:
[Sistem mevcut arızaları kontrol eder]
[Mevcut arıza yoksa yeni rapor oluşturur]

"✅ Arıza Bildirimi Başarıyla Kaydedildi!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TAKİP NUMARASI: MET-20251227-161217
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Konum: BAGCILAR MEYDAN - M1B
🔧 Arıza: asansör
📝 Detay: Turnike katı ile cadde arasındaki asansör

⚡ Öncelik: HIGH
👥 Departman: Asansör Bakım Birimi
📅 Tahmini Çözüm: 27.12.2025 (Tahmini 4 saat içinde)

⚠️ Engelli vatandaşların erişimi etkileniyor

🔄 Alternatif Çözümler:
  • İstasyonda 29 adet asansör kullanılabilir
  • Normal merdivenler kullanılabilir"
```

### Mevcut Arıza Durumu:

```
👤 KULLANICI:
"Bağcılar Meydan'dayım asansör çalışmıyor"

🤖 AGENT:
[Konum detayı sorar]

👤 KULLANICI:
"Turnike katı ile cadde arası"

🤖 AGENT:
[Sistemde aynı arıza bulunur]

"🔍 Sistem Kontrolü Tamamlandı

Bu konuda sistemimizde mevcut bir arıza kaydı bulunmaktadır:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Arıza Takip No: ARZ-2024-12345
📍 İstasyon: BAGCILAR MEYDAN
🔧 Ekipman: Asansör
📊 Durum: İşlemde
📅 Planlanan Servise Dönüş: 26.12.2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Teknik ekibimiz konuyla ilgilenmektedir."
```

## Teknik Detaylar

### Konuşma Durumu Yönetimi
```python
class FaultReportState:
    phase: ConversationPhase  # Hangi aşamadayız
    station: str              # Toplanan istasyon
    station_id: int           # İstasyon ID (API'den)
    line: str                 # Hat bilgisi
    location_detail: str      # Konum detayı
    equipment: str            # Ekipman
    problem_description: str  # Problem açıklaması

    # Zenginleştirilmiş data
    station_info: Dict        # API'den gelen istasyon detayları
    line_info: Dict
    equipment_info: Dict
```

### Konuşma Aşamaları
```python
class ConversationPhase(Enum):
    INITIAL_REPORT              # İlk mesaj
    COLLECTING_STATION          # İstasyon soruluyor
    COLLECTING_LOCATION_DETAIL  # Konum detayı soruluyor
    COLLECTING_EQUIPMENT        # Ekipman soruluyor
    COLLECTING_PROBLEM_DETAIL   # Problem detayı soruluyor
    CONFIRMING                  # Onay bekleniyor
    COMPLETED                   # Tamamlandı
```

### Öncelik Belirleme
```python
Priority Levels:
- CRITICAL: Can güvenliği, tren durması, yangın/duman
- HIGH: Ana erişim kapalı, kritik ekipman arızası
- MEDIUM: Alternatif var, tek ekipman arızası
- LOW: Konfor sorunu, minör arıza
```

### SLA Süreleri
Öncelik ve ekipman türüne göre otomatik SLA hesaplanır:
- CRITICAL: 1-2 saat
- HIGH: 4 saat
- MEDIUM: 8 saat
- LOW: 24 saat

## Test Etme

```bash
# Test senaryosunu çalıştır
python test_conversational_fault.py
```

Bu test:
1. Kullanıcının "Bağcılar Meydan'dayım asansör çalışmıyor" demesiyle başlar
2. Agent konum detayı sorar
3. Kullanıcı "Turnike katı ile cadde arası" cevabını verir
4. Sistem mevcut arızaları kontrol eder
5. Rapor oluşturur ve `fault_reports/` klasörüne kaydeder

## Entegrasyon

### MetroAgent'a Entegrasyon
```python
# src/agent/metro_agent.py

class MetroAgent:
    def __init__(self):
        # ...
        self.conversational_fault_manager = ConversationalFaultManager(
            self.llm,
            self.metro
        )

    async def _route_intent(self, message, intent, user_id):
        if intent.type == IntentType.FAULT_REPORT:
            response, report, completed = await self.conversational_fault_manager.handle_message(
                user_id, message
            )
            # ...
```

### API Endpoint Kullanımı
```bash
POST /message
{
    "message": "Bağcılar Meydan'dayım asansör çalışmıyor",
    "user_id": "user_123",
    "channel": "phone"
}
```

## Önemli Notlar

### Production için Öneriler:

1. **State Storage**:
   - Şu an in-memory dict kullanılıyor
   - Production'da Redis veya database kullanılmalı
   - Session timeout mekanizması eklenmeli

2. **Rapor Saklama**:
   - Dosya sistemi yerine S3/Azure Blob kullanılmalı
   - Database'e de rapor metadata'sı kaydedilmeli

3. **Bildirim Sistemi**:
   - Rapor oluşturulunca ilgili departmana email/SMS
   - Webhook entegrasyonu
   - CRM sistemi entegrasyonu

4. **Monitoring**:
   - Konuşma süresi tracking
   - Başarı oranı metrikleri
   - API çağrı metrikleri

## Gelecek Geliştirmeler

- [ ] Resim/fotoğraf upload desteği
- [ ] Ses kaydı desteği (telefon kanalı için)
- [ ] Çoklu dil desteği
- [ ] Real-time arıza durum güncellemesi
- [ ] Kullanıcıya SMS/Email bildirimi
- [ ] Dashboard arayüzü
- [ ] Analytics ve raporlama

## Lisans

İBB Metro İstanbul A.Ş. - 2024
