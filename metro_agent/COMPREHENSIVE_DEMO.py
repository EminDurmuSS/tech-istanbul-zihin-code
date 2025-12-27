#!/usr/bin/env python3
# ============================================================================
# DOSYA: COMPREHENSIVE_DEMO.py
# AÇIKLAMA: Metro Agent kapsamlı demo ve test senaryoları
# ============================================================================

"""
Metro Agent - Kapsamlı Demo ve Test Senaryoları

Bu dosya, Metro Agent sisteminin tüm yeteneklerini gösterir:
1. Akıllı Intent Classification
2. Otomatik API Routing
3. Arıza Rapor Sistemi (Zenginleştirilmiş)
4. Çok Modüllü Entegrasyon
"""

import asyncio
import json
from datetime import datetime


# Test senaryoları
DEMO_SCENARIOS = [
    # ==========================================================================
    # SENARYO 1: ARIZA BİLDİRİMİ - Asansör Arızası
    # ==========================================================================
    {
        "id": "S1",
        "name": "Arıza Bildirimi - Asansör",
        "user_message": "Kadıköy istasyonunda asansör çalışmıyor",
        "expected_intent": "FAULT_REPORT",
        "expected_entities": {
            "station": "Kadıköy",
            "equipment": "asansör"
        },
        "expected_apis": [
            "GetFaultyEquipments",
            "GetStations",
            "GetLines",
            "GetFailureTypes",
            "GetServiceStatuses"
        ],
        "expected_response_contains": [
            "arıza",
            "takip numarası",
            "MET-",
            "departman"
        ]
    },

    # ==========================================================================
    # SENARYO 2: HİZMET DURUMU SORGULAMA
    # ==========================================================================
    {
        "id": "S2",
        "name": "Hizmet Durumu Sorgulama",
        "user_message": "M4'te sefer var mı? İstanbulkart ile ücret ne kadar?",
        "expected_intent": "SERVICE_STATUS",
        "expected_entities": {
            "line": "M4"
        },
        "expected_apis": [
            "GetServiceStatuses",
            "GetLines",
            "GetTicketPrice"
        ],
        "expected_response_contains": [
            "M4",
            "sefer",
            "durum"
        ]
    },

    # ==========================================================================
    # SENARYO 3: SEFER SAATLERİ
    # ==========================================================================
    {
        "id": "S3",
        "name": "Sefer Saatleri Sorgulama",
        "user_message": "Kadıköy'den ilk sefer saat kaçta?",
        "expected_intent": "TIMETABLE",
        "expected_entities": {
            "station": "Kadıköy",
            "time_context": "ilk sefer"
        },
        "expected_apis": [
            "GetStations",
            "GetDirections",
            "GetTimeTable"
        ],
        "expected_response_contains": [
            "sefer",
            "saat"
        ]
    },

    # ==========================================================================
    # SENARYO 4: YÖN TARİFİ
    # ==========================================================================
    {
        "id": "S4",
        "name": "Yön Tarifi",
        "user_message": "Kadıköy'den Taksim'e nasıl giderim?",
        "expected_intent": "DIRECTION_HELP",
        "expected_entities": {
            "station": "Kadıköy",
            "destination": "Taksim"
        },
        "expected_apis": [
            "GetStations",
            "GetLines",
            "GetDirections",
            "GetStationBetweenTime"
        ],
        "expected_response_contains": [
            "rota",
            "aktarma"
        ]
    },

    # ==========================================================================
    # SENARYO 5: ERİŞİLEBİLİRLİK SORGULAMA
    # ==========================================================================
    {
        "id": "S5",
        "name": "Erişilebilirlik Bilgisi",
        "user_message": "Mecidiyeköy istasyonunda engelli erişimi var mı?",
        "expected_intent": "ACCESSIBILITY",
        "expected_entities": {
            "station": "Mecidiyeköy"
        },
        "expected_apis": [
            "GetStations",
            "GetFaultyEquipments"
        ],
        "expected_response_contains": [
            "asansör",
            "engelli"
        ]
    },

    # ==========================================================================
    # SENARYO 6: ÜCRET BİLGİSİ
    # ==========================================================================
    {
        "id": "S6",
        "name": "Ücret Bilgisi",
        "user_message": "Metro ücreti ne kadar? İstanbulkart ile indirim var mı?",
        "expected_intent": "FARE_INFO",
        "expected_entities": {},
        "expected_apis": [
            "GetTicketPrice"
        ],
        "expected_response_contains": [
            "ücret",
            "TL",
            "İstanbulkart"
        ]
    },

    # ==========================================================================
    # SENARYO 7: ARIZA SORGULAMA
    # ==========================================================================
    {
        "id": "S7",
        "name": "Arıza Durumu Sorgulama",
        "user_message": "Şişli-Mecidiyeköy'de turnike arızası var mıydı?",
        "expected_intent": "FAULT_INQUIRY",
        "expected_entities": {
            "station": "Şişli-Mecidiyeköy",
            "equipment": "turnike"
        },
        "expected_apis": [
            "GetFaultyEquipments",
            "GetStations"
        ],
        "expected_response_contains": [
            "arıza",
            "durum"
        ]
    },

    # ==========================================================================
    # SENARYO 8: KOMPLEX SORU - Çoklu Intent
    # ==========================================================================
    {
        "id": "S8",
        "name": "Komplex Soru - Çoklu Bilgi",
        "user_message": "M7 hattı normal çalışıyor mu? Mahmutbey'den Mecidiyeköy'e kaç dakika?",
        "expected_intent": "SERVICE_STATUS",
        "expected_entities": {
            "line": "M7",
            "station": "Mahmutbey",
            "destination": "Mecidiyeköy"
        },
        "expected_apis": [
            "GetServiceStatuses",
            "GetLines",
            "GetStations",
            "GetStationBetweenTime"
        ],
        "expected_response_contains": [
            "M7",
            "durum",
            "süre"
        ]
    },

    # ==========================================================================
    # SENARYO 9: KRİTİK ARIZA - Acil Durum
    # ==========================================================================
    {
        "id": "S9",
        "name": "Kritik Arıza - Acil",
        "user_message": "ACİL! Taksim'de yangın alarmı çalıyor, duman var!",
        "expected_intent": "FAULT_REPORT",
        "expected_entities": {
            "station": "Taksim",
            "problem_description": "yangın alarmı",
            "severity_hint": "acil"
        },
        "expected_apis": [
            "GetFaultyEquipments",
            "GetStations",
            "GetLines",
            "GetServiceStatuses"
        ],
        "expected_priority": "CRITICAL",
        "expected_response_contains": [
            "ACİL",
            "takip numarası",
            "güvenlik"
        ]
    },

    # ==========================================================================
    # SENARYO 10: GENEL FAQ
    # ==========================================================================
    {
        "id": "S10",
        "name": "Genel Soru - FAQ",
        "user_message": "İstanbulkart nereden alınır?",
        "expected_intent": "GENERAL_FAQ",
        "expected_entities": {},
        "expected_apis": [
            "FrequentlyAskedQuestions"
        ],
        "expected_response_contains": [
            "İstanbulkart"
        ]
    }
]


def print_header(text: str):
    """Başlık yazdır"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str):
    """Bölüm başlığı"""
    print(f"\n--- {text} ---")


def print_success(text: str):
    """Başarı mesajı"""
    print(f"✓ {text}")


def print_error(text: str):
    """Hata mesajı"""
    print(f"✗ {text}")


def print_info(text: str):
    """Bilgi mesajı"""
    print(f"ℹ {text}")


async def run_demo_scenario(scenario: dict, agent):
    """Tek bir demo senaryosu çalıştır"""

    print_header(f"SENARYO {scenario['id']}: {scenario['name']}")

    print_section("Kullanıcı Mesajı")
    print(f"  '{scenario['user_message']}'")

    # Agent'a gönder
    try:
        response = await agent.process_message(
            message=scenario['user_message'],
            user_id=f"demo_user_{scenario['id']}",
            channel="demo"
        )

        # Intent kontrolü
        print_section("Intent Sınıflandırma")
        print(f"  Beklenen: {scenario['expected_intent']}")
        print(f"  Bulunan: {response.intent.type.value}")

        if response.intent.type.value.upper() == scenario['expected_intent']:
            print_success("Intent doğru tespit edildi!")
        else:
            print_error(f"Intent hatalı! Beklenen: {scenario['expected_intent']}, Bulunan: {response.intent.type.value}")

        print(f"  Güven Skoru: {response.intent.confidence:.2f}")

        # Entity kontrolü
        print_section("Entity Extraction")
        print(f"  Bulunan Entity'ler: {json.dumps(response.intent.entities, ensure_ascii=False, indent=2)}")

        for expected_key, expected_value in scenario.get('expected_entities', {}).items():
            found_value = response.intent.entities.get(expected_key)
            if found_value and expected_value.lower() in str(found_value).lower():
                print_success(f"{expected_key}: '{found_value}' ✓")
            else:
                print_error(f"{expected_key} beklenen değerde değil")

        # API Kullanımı (log'lardan görülebilir)
        print_section("API Çağrıları")
        print(f"  Beklenen API'ler: {', '.join(scenario.get('expected_apis', []))}")
        print_info("Gerçek API çağrıları log'larda görülebilir")

        # Yanıt kontrolü
        print_section("Agent Yanıtı")
        print(f"\n{response.response.text}\n")

        # Yanıt içerik kontrolü
        response_text_lower = response.response.text.lower()
        all_found = True

        for expected_text in scenario.get('expected_response_contains', []):
            if expected_text.lower() in response_text_lower:
                print_success(f"Yanıt içeriyor: '{expected_text}'")
            else:
                print_error(f"Yanıt içermiyor: '{expected_text}'")
                all_found = False

        # Öncelik kontrolü (arıza raporlarında)
        if scenario.get('expected_priority') and response.internal_report:
            print_section("Öncelik Değerlendirmesi")
            # Priority bilgisi internal_report'ta olabilir
            print_info(f"Beklenen: {scenario['expected_priority']}")

        # İşlem süresi
        print_section("Performans")
        print(f"  İşlem Süresi: {response.processing_time_ms} ms")

        if response.processing_time_ms < 3000:
            print_success("İşlem süresi kabul edilebilir (< 3s)")
        else:
            print_error("İşlem süresi yüksek (> 3s)")

        # Rapor ID (arıza için)
        if response.internal_report:
            print_section("Arıza Raporu")
            print(f"  Rapor ID: {response.internal_report.report_id}")
            print(f"  Aksiyonlar: {', '.join(response.actions)}")

        print_section("Sonuç")
        if all_found:
            print_success(f"✓✓✓ Senaryo {scenario['id']} BAŞARILI ✓✓✓")
        else:
            print_error(f"✗✗✗ Senaryo {scenario['id']} KISMEN BAŞARILI ✗✗✗")

    except Exception as e:
        print_error(f"Senaryo çalıştırma hatası: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_all_scenarios():
    """Tüm senaryoları sırayla çalıştır"""

    print_header("METRO AGENT - KAPSAMLI DEMO VE TEST")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Toplam Senaryo: {len(DEMO_SCENARIOS)}")

    # Agent'ı başlat
    print_info("Metro Agent başlatılıyor...")

    try:
        from src.agent.metro_agent import MetroAgent

        agent = MetroAgent()
        print_success("Metro Agent başlatıldı!")

    except Exception as e:
        print_error(f"Agent başlatılamadı: {str(e)}")
        return

    # Senaryoları çalıştır
    success_count = 0

    for i, scenario in enumerate(DEMO_SCENARIOS, 1):
        print_info(f"\nSenaryo {i}/{len(DEMO_SCENARIOS)} çalıştırılıyor...")
        await run_demo_scenario(scenario, agent)

        # Kısa bekleme (API rate limit için)
        await asyncio.sleep(1)

    # Özet
    print_header("DEMO TAMAMLANDI")
    print(f"Tüm {len(DEMO_SCENARIOS)} senaryo çalıştırıldı.")
    print("\nDetaylı loglar için loglara bakınız.")


async def run_single_scenario(scenario_id: str):
    """Tek bir senaryoyu çalıştır"""

    scenario = next((s for s in DEMO_SCENARIOS if s['id'] == scenario_id), None)

    if not scenario:
        print_error(f"Senaryo {scenario_id} bulunamadı!")
        print(f"Mevcut senaryolar: {', '.join([s['id'] for s in DEMO_SCENARIOS])}")
        return

    from src.agent.metro_agent import MetroAgent
    agent = MetroAgent()

    await run_demo_scenario(scenario, agent)


async def interactive_demo():
    """İnteraktif demo modu"""

    print_header("METRO AGENT - İNTERAKTİF DEMO")
    print("Çıkmak için 'exit' yazın.")

    from src.agent.metro_agent import MetroAgent
    agent = MetroAgent()

    while True:
        print("\n" + "-" * 80)
        user_input = input("\nVatandaş: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'çıkış']:
            print("Demo sonlandırılıyor...")
            break

        try:
            response = await agent.process_message(
                message=user_input,
                user_id="interactive_user",
                channel="interactive"
            )

            print(f"\nAgent: {response.response.text}")
            print(f"\n[Intent: {response.intent.type.value}, Güven: {response.intent.confidence:.2f}, Süre: {response.processing_time_ms}ms]")

        except Exception as e:
            print_error(f"Hata: {str(e)}")


def main():
    """Ana fonksiyon"""
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "all":
            # Tüm senaryolar
            asyncio.run(run_all_scenarios())

        elif mode == "interactive":
            # İnteraktif mod
            asyncio.run(interactive_demo())

        elif mode.startswith("S"):
            # Tek senaryo
            asyncio.run(run_single_scenario(mode))

        else:
            print("Kullanım:")
            print("  python COMPREHENSIVE_DEMO.py all          - Tüm senaryoları çalıştır")
            print("  python COMPREHENSIVE_DEMO.py interactive  - İnteraktif demo")
            print("  python COMPREHENSIVE_DEMO.py S1           - Tek senaryo çalıştır")
    else:
        # Default: tüm senaryolar
        asyncio.run(run_all_scenarios())


if __name__ == "__main__":
    main()
