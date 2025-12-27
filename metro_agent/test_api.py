"""
Metro Agent API Test Script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_message(message: str):
    """Test message endpoint"""
    print(f"\n{'='*60}")
    print(f"TEST: {message}")
    print(f"{'='*60}")

    response = requests.post(
        f"{BASE_URL}/message",
        json={"message": message}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\nBasarili!")
        print(f"\nIntent: {data['intent']} (Confidence: {data['confidence']:.2f})")
        print(f"Entities: {json.dumps(data['entities'], ensure_ascii=False, indent=2)}")
        print(f"\nYanit:\n{data['response']}")

        if data.get('report_id'):
            print(f"\nRapor ID: {data['report_id']}")

        print(f"\nIslem suresi: {data['processing_time_ms']}ms")
    else:
        print(f"Hata: {response.status_code}")
        print(response.text)


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(f"\nSistem Saglik Durumu:")
    print(f"   Status: {data['status']}")
    print(f"   Version: {data['version']}")


def main():
    print("\nMetro Agent API Test")
    print("="*60)

    # Health check
    test_health()

    # Test mesajları
    test_cases = [
        "Mecidiyeköy istasyonunda asansör bozuk",
        "M2 hattı çalışıyor mu?",
        "Taksim'den Kadıköy'e nasıl giderim?",
        "İstanbulkart fiyatları nedir?",
        "İlk sefer saat kaçta?",
    ]

    for message in test_cases:
        try:
            test_message(message)
        except Exception as e:
            print(f"Test hatasi: {e}")

    print("\n" + "="*60)
    print("Testler tamamlandi!")


if __name__ == "__main__":
    main()
