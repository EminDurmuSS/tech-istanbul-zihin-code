# ============================================================================
# DOSYA: test_conversational_fault.py
# ============================================================================

import asyncio
import sys
import io

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.modules.conversational_fault_manager import ConversationalFaultManager
from src.api.metro_api_client import MetroAPIClient
from src.api.openrouter_client import OpenRouterClient


async def test_scenario():
    """
    Test senaryosu:
    Kullanıcı: "Bağcılar Meydan'dayım asansör çalışmıyor"
    Agent: Konum detayı sorar
    Kullanıcı: "Turnike katı ile cadde arasında"
    Agent: Rapor oluşturur
    """

    # İstemciler
    metro = MetroAPIClient()
    llm = OpenRouterClient()

    # Conversational Manager
    manager = ConversationalFaultManager(llm, metro)

    # User ID
    user_id = "test_user_001"

    print("=" * 70)
    print("     İBB METRO İSTANBUL - KONUŞMALI ARIZA BİLDİRİM TESTİ")
    print("=" * 70)
    print()

    # 1. İlk mesaj
    print("👤 KULLANICI:")
    print("Bağcılar Meydan'dayım asansör çalışmıyor")
    print()

    response, report, completed = await manager.handle_message(
        user_id,
        "Bağcılar Meydan'dayım asansör çalışmıyor"
    )

    print("🤖 AGENT:")
    print(response)
    print()
    print("-" * 70)
    print()

    if not completed:
        # 2. Konum detayı
        print("👤 KULLANICI:")
        print("Turnike katı ile cadde arasındaki asansör")
        print()

        response, report, completed = await manager.handle_message(
            user_id,
            "Turnike katı ile cadde arasındaki asansör"
        )

        print("🤖 AGENT:")
        print(response)
        print()
        print("-" * 70)
        print()

    if not completed:
        # 3. Problem detayı
        print("👤 KULLANICI:")
        print("Tamamen durmuş, çalışmıyor")
        print()

        response, report, completed = await manager.handle_message(
            user_id,
            "Tamamen durmuş, çalışmıyor"
        )

        print("🤖 AGENT:")
        print(response)
        print()
        print("-" * 70)
        print()

    # Rapor oluşturulduysa göster
    if report:
        print()
        print("=" * 70)
        print("                      RAPOR OLUŞTURULDU!")
        print("=" * 70)
        print()
        print(f"📋 Rapor ID: {report.report_id}")
        print(f"📍 İstasyon: {report.station}")
        print(f"🔧 Ekipman: {report.equipment_type}")
        print(f"📝 Konum: {report.location_detail}")
        print(f"⚡ Öncelik: {report.classification.priority.value}")
        print(f"👥 Departman: {report.target_department}")
        print(f"📅 Çözüm Tahmini: {report.estimated_resolution}")
        print()
        print(f"✅ Rapor dosyası: fault_reports/{report.report_id}.txt")
        print()

    print("=" * 70)
    print("                        TEST TAMAMLANDI")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_scenario())
