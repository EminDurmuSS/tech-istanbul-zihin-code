"""
============================================================================
DEMO: Metro İstanbul Arıza Rapor Sistemi (Mock Data)
============================================================================

Kullanıcı: "Kadıköy istasyonunda asansör çalışmıyor, engelli vatandaşlar mağdur"

Bu script mock verilerle:
1. Arızayı sınıflandırır
2. İBB için profesyonel rapor oluşturur
3. Kullanıcıya bilgilendirme mesajı hazırlar
"""

from datetime import datetime
import json


def get_mock_data():
    """Mock Metro API verileri"""
    return {
        "stations": [
            {
                "Id": 107,
                "Name": "Kadıköy",
                "LineId": 4,
                "LineName": "M4 (Kadıköy-Tavşantepe)",
                "DetailInfo": {
                    "Lift": 2,
                    "Escolator": 4,
                    "WC": True,
                    "BabyRoom": True,
                    "Latitude": "40.9907",
                    "Longitude": "29.0258"
                }
            }
        ],
        "lines": [
            {
                "Id": 4,
                "Name": "M4 (Kadıköy-Tavşantepe)",
                "ShortDescription": "Kadıköy-Tavşantepe Metro Hattı"
            }
        ],
        "service_statuses": [
            {
                "LineName": "M4",
                "Status": "Normal",
                "Message": "Seferler normal şekilde devam etmektedir"
            }
        ],
        "fault_types": [
            {
                "Id": "FT-ASANSOR-001",
                "Name": "Asansör Mekanik Arıza",
                "Category": "ELEVATOR"
            }
        ],
        "tech_objects": [
            {
                "Id": "TO-ASN-001",
                "Name": "Yolcu Asansörü",
                "Type": "ELEVATOR"
            }
        ],
        "faulty_equipments": []  # Yeni arıza
    }


def extract_entities(message):
    """Kullanıcı mesajından entity'leri çıkar"""
    return {
        "station": "Kadıköy",
        "line": "M4",
        "equipment": "Asansör",
        "location_detail": "Giriş katı",
        "problem_description": "Asansör çalışmıyor",
        "severity_hint": "Erişim engeli - engelli vatandaşlar mağdur",
        "accessibility_impact": True
    }


def check_existing_fault(entities, faulty_equipments):
    """Mevcut arızaları kontrol et"""
    # Bu senaryoda yeni arıza
    return None


def classify_fault(entities):
    """Arızayı sınıflandır"""
    return {
        "fault_type_id": "FT-ASANSOR-001",
        "fault_type_name": "Asansör Mekanik Arıza",
        "fault_category": "ELEVATOR",
        "technical_object_id": "TO-ASN-001",
        "technical_object_name": "Yolcu Asansörü",
        "priority": "HIGH",
        "priority_reason": "Engelli erişimini engelliyor - WCAG 2.1 uyumluluk ihlali",
        "target_department": "Elektro-Mekanik Sistemler Müdürlüğü",
        "sub_department": "Asansör ve Yürüyen Merdiven Bakım Birimi",
        "estimated_hours": 2,
        "sla_hours": 2
    }


def enrich_fault(entities, data):
    """Arıza verilerini zenginleştir"""

    station_info = data["stations"][0]
    line_info = data["lines"][0]
    line_status = data["service_statuses"][0]

    alternatives = [
        "Merdiven kullanılabilir (engelli erişimine uygun değil)",
        "Yürüyen merdiven kullanılabilir (tekerlekli sandalye için uygun değil)",
        "İstasyon görevlilerinden yardım istenebilir"
    ]

    passenger_impact = {
        "affected_groups": ["Engelli vatandaşlar", "Bebek arabalı aileler", "Yaşlı yolcular", "Bavullu yolcular"],
        "estimated_daily_affected": 150,
        "accessibility_compliance": "İHLAL - Asansör zorunlu erişim yolu",
        "legal_reference": "5378 Sayılı Engelliler Hakkında Kanun, Md. 7"
    }

    return {
        "station_info": station_info,
        "line_info": line_info,
        "line_status": line_status,
        "alternatives": alternatives,
        "accessibility_impact": "KRİTİK - Engelli erişimi tamamen engellenmiş",
        "passenger_impact": passenger_impact,
        "nearby_stations": ["Ayrılık Çeşmesi", "Acıbadem"],
        "alternative_routes": "Otobüs hatları: 4, 10S, 14, 16"
    }


def generate_ibb_report(entities, classification, enrichment):
    """İBB için profesyonel rapor oluştur"""

    report_id = f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    station_info = enrichment["station_info"]
    line_info = enrichment["line_info"]
    passenger_impact = enrichment["passenger_impact"]

    report = f"""
═══════════════════════════════════════════════════════════════════
                    ARIZA BİLDİRİM RAPORU
                  İSTANBUL BÜYÜKŞEHİR BELEDİYESİ
                    METRO İSTANBUL A.Ş.
═══════════════════════════════════════════════════════════════════

RAPOR NUMARASI    : {report_id}
TARİH/SAAT        : {timestamp}
KAYIT KANALI      : 153 Çağrı Merkezi (Otomatik AI Sistemi)
DURUM             : YENİ KAYIT - ACİL MÜDAHALE GEREKLİ

───────────────────────────────────────────────────────────────────
1. ÖNCELİK DEĞERLENDİRMESİ
───────────────────────────────────────────────────────────────────

ÖNCELİK SEVİYESİ  : ⚠️ YÜKSEK (HIGH)
ARIZA KATEGORİSİ  : {classification['fault_category']}
ARIZA TİPİ        : {classification['fault_type_name']}
SLA HEDEF SÜRESI  : {classification['sla_hours']} SAAT

ÖNCELİK GEREKÇESİ :
• {classification['priority_reason']}
• Erişilebilirlik mevzuatı uyumluluk ihlali
• Günlük ~{passenger_impact['estimated_daily_affected']} yolcu etkileniyor
• Alternatif erişim yolu engelli vatandaşlar için MEVCUT DEĞİL

HUKUKI BOYUT      :
• {passenger_impact['legal_reference']}
• Erişilebilirlik İzleme ve Denetleme Yönetmeliği
• WCAG 2.1 Level AA Erişilebilirlik Standartları

───────────────────────────────────────────────────────────────────
2. KONUM BİLGİLERİ
───────────────────────────────────────────────────────────────────

HAT               : {entities['line']} - {line_info['Name']}
İSTASYON          : {entities['station']}
İSTASYON ID       : {station_info['Id']}
KONUM DETAY       : {entities['location_detail']}
İLÇE              : Kadıköy
BÖLGE             : Anadolu Yakası

İSTASYON ÖZELLİKLERİ:
• Asansör Sayısı  : {station_info['DetailInfo']['Lift']}
• Yürüyen Merdiven: {station_info['DetailInfo']['Escolator']}
• Engelli WC      : {'Var' if station_info['DetailInfo']['WC'] else 'Yok'}
• Koordinatlar    : {station_info['DetailInfo']['Latitude']}, {station_info['DetailInfo']['Longitude']}

───────────────────────────────────────────────────────────────────
3. ARIZA DETAYLARI
───────────────────────────────────────────────────────────────────

EKİPMAN TÜRÜ      : {entities['equipment']}
TEKNİK NESNE      : {classification['technical_object_name']}
TEKNİK NESNE ID   : {classification['technical_object_id']}

SORUN TANIMI      :
"{entities['problem_description']}"

CİDDİYET İPUCU    :
"{entities['severity_hint']}"

ERİŞİLEBİLİRLİK   : {enrichment['accessibility_impact']}

MEVCUT DURUM      :
• Asansör tamamen devre dışı
• Engelli erişimi mümkün değil
• Alternatif erişim yolları yetersiz

───────────────────────────────────────────────────────────────────
4. ETKİ ANALİZİ
───────────────────────────────────────────────────────────────────

ETKİLENEN GRUPLAR :
"""

    for group in passenger_impact['affected_groups']:
        report += f"  • {group}\n"

    report += f"""
TAHMİNİ GÜNLÜK ETKİ:
• Etkilenen Yolcu : ~{passenger_impact['estimated_daily_affected']} kişi/gün
• Erişim Engeli   : %100 (Engelli vatandaşlar için)
• Hizmet Kalitesi : Kritik düşüş

HİZMET DURUMU     :
• Hat Durumu      : {enrichment['line_status']['Status']}
• Sefer Aralığı   : Normal
• Genel Etki      : Lokal (tek istasyon)

ALTERNATİF ÇÖZÜMLER:
"""

    for alt in enrichment['alternatives']:
        report += f"  • {alt}\n"

    report += f"""
YAKIN İSTASYONLAR :
"""
    for nearby in enrichment['nearby_stations']:
        report += f"  • {nearby}\n"

    report += f"""
ALTERNATİF ULAŞIM :
  • {enrichment['alternative_routes']}

───────────────────────────────────────────────────────────────────
5. YÖNLENDİRME BİLGİLERİ
───────────────────────────────────────────────────────────────────

HEDEF DEPARTMAN   : {classification['target_department']}
ALT BİRİM         : {classification['sub_department']}

SORUMLU EKİP      :
• Birincil        : Asansör Bakım Ekibi
• Destek          : Elektrik Arıza Ekibi
• Koordinasyon    : İstasyon Müdürlüğü - Kadıköy

DEVREYE ALINACAK SİSTEMLER:
• SAP PM (Bakım Yönetimi)
• SCADA (Asansör Monitoring)
• İş Emri Sistemi
• Çağrı Merkezi CRM

───────────────────────────────────────────────────────────────────
6. ÖNERİLEN MÜDAHALE PLANI
───────────────────────────────────────────────────────────────────

ACİL AKSIYONLAR (İLK 30 DAKİKA):
1. ✓ Teknik ekip sahaya sevk (ACIL)
2. ✓ İstasyon görevlisi bilgilendirme
3. ✓ Uyarı tabelası yerleştirme
4. ✓ Engelli yolculara alternatif erişim desteği

KISA VADE (1-2 SAAT):
5. ⏱ Asansör teknik kontrol ve teşhis
6. ⏱ Arıza kaynağı tespiti (mekanik/elektrik/yazılım)
7. ⏱ Yedek parça ihtiyacı kontrolü
8. ⏱ Tamir/değişim kararı

ORTA VADE (2-4 SAAT):
9. ⏱ Onarım işlemleri
10. ⏱ Sistem testleri
11. ⏱ Güvenlik kontrolleri
12. ⏱ Devreye alma

SON ADIMLAR:
13. ⏱ İstasyon görevlisi bilgilendirme
14. ⏱ Çağrı merkezi güncelleme
15. ⏱ Vatandaş bilgilendirme (varsa iletişim bilgisi)
16. ⏱ Rapor kapatma ve arşivleme

───────────────────────────────────────────────────────────────────
7. VATANDAŞ YÖNLENDİRME ÖNERİLERİ
───────────────────────────────────────────────────────────────────

Çağrı merkezi operatörü vatandaşa aşağıdaki bilgileri vermelidir:

1. ARIZA TAKİP NUMARASI:
   "Arıza kaydınız {report_id} numarası ile sisteme girildi."

2. TAHMİNİ ÇÖZÜM SÜRESİ:
   "Teknik ekibimiz en geç {classification['sla_hours']} saat içinde
   sorunu çözecektir."

3. MEVCUT DURUM:
   "Kadıköy istasyonu asansörü şu an hizmet dışıdır. Teknik ekip
   bilgilendirilmiş ve yola çıkmıştır."

4. ALTERNATİF ERİŞİM:
   - İstasyon görevlilerinden yardım talep edebilirsiniz
   - Komşu istasyonlar (Ayrılık Çeşmesi/Acıbadem) kullanılabilir
   - Alternatif ulaşım: {enrichment['alternative_routes']}

5. BİLGİLENDİRME:
   "Arıza çözüldüğünde iletişim bilgileriniz varsa size bilgi
   verilecektir."

───────────────────────────────────────────────────────────────────
8. TEKNİK VERİ PAKET (SAHA EKİBİ İÇİN)
───────────────────────────────────────────────────────────────────

ASANSÖR BİLGİLERİ:
• Marka/Model     : [SCADA sisteminden çekilecek]
• Seri No         : [SCADA sisteminden çekilecek]
• Kapasite        : [SCADA sisteminden çekilecek]
• Son Bakım       : [SAP PM'den çekilecek]
• Bakım Geçmişi   : [SAP PM'den çekilecek]

SCADA QUERY:
  SELECT * FROM elevator_status
  WHERE station_id = {station_info['Id']}
  AND equipment_type = 'ELEVATOR'
  AND location = 'ENTRANCE'

SAP PM İŞ EMRİ:
  • Notification Type: M1 (Breakdown)
  • Priority: 1 (Very High)
  • Functional Location: M4-KADIKOY-ELEVATOR-01
  • Equipment: [Equipment ID from SCADA]
  • Breakdown: Elevator not operational
  • Impact: Accessibility violation

───────────────────────────────────────────────────────────────────
9. KALİTE VE UYUMLULUK
───────────────────────────────────────────────────────────────────

KALİTE KONTROLÜ:
• Onarım sonrası fonksiyon testi
• Güvenlik sertifikası kontrolü
• Engelli erişim uyumluluk testi
• Ses ve görsel uyarı sistemleri testi

UYUMLULUK KONTROL:
• TSE EN 81-70 (Asansör Erişilebilirlik Standardı)
• 5378 Sayılı Engelliler Kanunu
• Erişilebilirlik İzleme Yönetmeliği
• Metro İstanbul Kalite Prosedürleri

───────────────────────────────────────────────────────────────────
10. RAPORLAMA VE TAKİP
───────────────────────────────────────────────────────────────────

DURUM GÜNCELLEMELERİ:
• 30 dk sonra : Ekip durumu
• 1 saat sonra: İlk teşhis
• 2 saat sonra: Tamir durumu
• Çözüm anında: Rapor kapatma

ESCALATION PROSEDÜRÜ:
• 2 saat içinde çözüm yoksa → Vardiya Amiri
• 4 saat içinde çözüm yoksa → Müdür Yardımcısı
• 8 saat içinde çözüm yoksa → Genel Müdür Raporu

BİLDİRİM LİSTESİ:
• İstasyon Müdürü - Kadıköy
• Elektro-Mekanik Sistemler Müdürü
• Çağrı Merkezi Koordinatörü
• Erişilebilirlik Sorumlusu
• (SLA aşımında) Genel Müdür Yardımcısı

───────────────────────────────────────────────────────────────────
11. SİSTEM ENTEGRASYONLARI
───────────────────────────────────────────────────────────────────

OTOMATIK VERİ AKIŞI:
✓ 153 Çağrı Merkezi → CRM Sistemi
✓ CRM Sistemi → SAP PM (İş Emri Oluşturma)
✓ SAP PM → SCADA (Ekipman Durumu Güncelleme)
✓ SCADA → BI Dashboard (Performans Metrikleri)
✓ BI Dashboard → Yönetim Raporlama

API ENTEGRASYONLARI:
• Metro İstanbul Mobile API (v2): İstasyon/Hat verileri
• SAP PM API: İş emri oluşturma
• SCADA REST API: Ekipman monitoring
• SMS Gateway API: Vatandaş bilgilendirme
• WhatsApp Business API: Otomatik yanıt

WEBHOOK NOTIFICATIONS:
• İş emri oluşturuldu → SAP PM
• Ekip yola çıktı → Mobile App
• İlk teşhis yapıldı → CRM Update
• Arıza çözüldü → Vatandaş bilgilendirme

───────────────────────────────────────────────────────────────────
12. RAPOR METRİKLERİ
───────────────────────────────────────────────────────────────────

SİSTEM PERFORMANSI:
• AI Entity Extraction : ✓ Başarılı (100%)
• API Veri Çekimi      : ✓ 5 endpoint başarılı
• Sınıflandırma        : ✓ Otomatik (AI-powered)
• Departman Routing    : ✓ Otomatik
• SLA Hesaplama        : ✓ Otomatik
• Zenginleştirme       : ✓ 5 veri kaynağı

RAPOR KALİTESİ:
• Veri Eksiksizliği    : 95%
• Doğruluk (estimated) : 92%
• İşlem Süresi         : <2 saniye
• Operatör Müdahalesi  : Minimal

VERİ ZENGİNLEŞTİRME:
• İstasyon metadata
• Hat durumu
• Erişilebilirlik bilgileri
• Alternatif rotalar
• Yolcu etki analizi
• Benzer arıza geçmişi

═══════════════════════════════════════════════════════════════════
                        RAPOR SONU

Oluşturulma: Otomatik (AI Agent)
Sistem: Metro İstanbul Akıllı Çağrı Merkezi v1.0
Onay: Sistem Otomatik - İnsan Onayı Bekleniyor

NOT: Bu rapor yapay zeka destekli sistemle otomatik oluşturulmuştur.
Kritik kararlar için insan onayı gereklidir.
═══════════════════════════════════════════════════════════════════
"""

    return report


def generate_user_response(entities, classification, enrichment):
    """Kullanıcıya dönecek yanıt"""

    report_id = f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    return f"""
Metro İstanbul Çağrı Merkezi

Arıza bildirimi kaydedildi!

═══════════════════════════════════
TAKİP NUMARANIZ
═══════════════════════════════════
{report_id}

═══════════════════════════════════
KONUM BİLGİLERİ
═══════════════════════════════════
• İstasyon: {entities['station']}
• Hat: {entities['line']}
• Ekipman: {entities['equipment']}

═══════════════════════════════════
TAHMİNİ ÇÖZÜM SÜRESİ
═══════════════════════════════════
{classification['sla_hours']} saat içinde

═══════════════════════════════════
DURUM
═══════════════════════════════════
Teknik ekibimiz bilgilendirildi ve
en kısa sürede müdahale edecektir.

Departman: {classification['target_department']}

═══════════════════════════════════
ÖNEMLİ BİLGİ
═══════════════════════════════════
{enrichment['accessibility_impact']}

═══════════════════════════════════
ALTERNATİF ERİŞİM
═══════════════════════════════════
• İstasyon görevlilerinden yardım
  talep edebilirsiniz
• Komşu istasyonlar: {', '.join(enrichment['nearby_stations'])}
• Alternatif ulaşım: {enrichment['alternative_routes']}

═══════════════════════════════════
İLETİŞİM
═══════════════════════════════════
Gelişmelerden haberdar olmak için
takip numaranızı saklayın.

Sorularınız için: 153

Anlayışınız için teşekkür ederiz.

İstanbul Büyükşehir Belediyesi
Metro İstanbul A.Ş.
"""


def main():
    """Ana demo fonksiyonu"""

    print("=" * 70)
    print("Metro Istanbul Ariza Rapor Sistemi - DEMO")
    print("=" * 70)
    print()

    print("KULLANICI BILDIRIMI:")
    print("'Kadikoy istasyonunda asansor calismiyor,")
    print(" engelli vatandaslar magdur'")
    print()

    # 1. Mock veri
    print("Mock veri yukleniyor...")
    data = get_mock_data()
    print(f"* {len(data['stations'])} istasyon")
    print(f"* {len(data['lines'])} hat")
    print(f"* {len(data['fault_types'])} ariza tipi")
    print(f"* {len(data['tech_objects'])} teknik nesne")
    print()

    # 2. Entity extraction
    print("Entity extraction...")
    entities = extract_entities("Kadıköy istasyonunda asansör çalışmıyor")
    print(f"* Istasyon: {entities['station']}")
    print(f"* Hat: {entities['line']}")
    print(f"* Ekipman: {entities['equipment']}")
    print()

    # 3. Mevcut arıza kontrolü
    print("Mevcut ariza kontrolu...")
    existing = check_existing_fault(entities, data['faulty_equipments'])
    if existing:
        print(f"! Bu ariza sistemde kayitli")
    else:
        print("* Yeni ariza - kayit olusturuluyor")
    print()

    # 4. Sınıflandırma
    print("Ariza siniflandiriliyor...")
    classification = classify_fault(entities)
    print(f"* Kategori: {classification['fault_category']}")
    print(f"* Oncelik: {classification['priority']}")
    print(f"* Departman: {classification['target_department']}")
    print(f"* SLA: {classification['sla_hours']} saat")
    print()

    # 5. Zenginleştirme
    print("Veri zenginlestiriliyor...")
    enrichment = enrich_fault(entities, data)
    print(f"* Istasyon detaylari eklendi")
    print(f"* Hat durumu eklendi")
    print(f"* Alternatifler belirlendi")
    print(f"* Etki analizi yapildi")
    print()

    # 6. Rapor oluştur
    print("IBB raporu olusturuluyor...")
    ibb_report = generate_ibb_report(entities, classification, enrichment)

    # 7. Kullanıcı yanıtı
    user_response = generate_user_response(entities, classification, enrichment)

    # Dosyalara kaydet
    with open("ibb_fault_report.txt", "w", encoding="utf-8") as f:
        f.write(ibb_report)

    with open("user_response.txt", "w", encoding="utf-8") as f:
        f.write(user_response)

    # JSON formatında da kaydet
    json_data = {
        "report_id": f"MET-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "entities": entities,
        "classification": classification,
        "enrichment": {
            "station_info": enrichment["station_info"],
            "line_info": enrichment["line_info"],
            "alternatives": enrichment["alternatives"],
            "passenger_impact": enrichment["passenger_impact"]
        }
    }

    with open("fault_data.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print("* Rapor olusturuldu")
    print()

    print("=" * 70)
    print("KULLANICIYA GONDERILECEK MESAJ:")
    print("=" * 70)
    print(user_response)

    print()
    print("=" * 70)
    print("DOSYALAR:")
    print("=" * 70)
    print("* ibb_fault_report.txt  - IBB icin detayli rapor")
    print("* user_response.txt     - Kullanici yaniti")
    print("* fault_data.json       - JSON veri")
    print()


if __name__ == "__main__":
    main()
