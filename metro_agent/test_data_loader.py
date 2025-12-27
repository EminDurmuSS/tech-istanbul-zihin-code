#!/usr/bin/env python3
"""
Data loader test scripti
"""

from src.utils.data_loader import (
    load_station_mappings,
    load_department_routing,
    load_intent_examples,
    get_station_aliases,
    get_sla_hours,
    get_priority_from_description,
    validate_data_files
)
from src.models.fault import FaultCategory, Priority


def test_station_mappings():
    """İstasyon mapping testi"""
    print("\n=== İstasyon Mappings Test ===")

    data = load_station_mappings()
    print(f"✓ Aliases yüklendi: {len(data['aliases'])} adet")
    print(f"✓ İstasyon hatları: {len(data['lines'])} adet")

    aliases = get_station_aliases()
    test_alias = aliases.get("mecidiyekoy")
    print(f"✓ Test alias: 'mecidiyekoy' -> '{test_alias}'")


def test_department_routing():
    """Department routing testi"""
    print("\n=== Department Routing Test ===")

    data = load_department_routing()
    print(f"✓ Departmanlar: {len(data['departments'])} adet")
    print(f"✓ Priority kuralları: {len(data['priority_rules'])} adet")

    # SLA test
    sla = get_sla_hours(FaultCategory.ESCALATOR.value, Priority.CRITICAL.value)
    print(f"✓ ESCALATOR + CRITICAL SLA: {sla} saat")

    # Priority test
    priority = get_priority_from_description("Tren durdu, can güvenliği var!")
    print(f"✓ Priority detection: 'can güvenliği' -> {priority}")


def test_intent_examples():
    """Intent examples testi"""
    print("\n=== Intent Examples Test ===")

    data = load_intent_examples()
    print(f"✓ Intent türleri: {len(data)} adet")

    total = sum(len(examples) for examples in data.values())
    print(f"✓ Toplam örnek: {total} adet")

    if "fault_report" in data:
        print(f"✓ fault_report örnekleri: {len(data['fault_report'])} adet")
        print(f"  İlk örnek: '{data['fault_report'][0]}'")


def test_validation():
    """Data validation testi"""
    print("\n=== Data Validation Test ===")

    result = validate_data_files()
    if result:
        print("✓ Tüm data dosyaları geçerli!")
    else:
        print("✗ Validation başarısız!")

    return result


if __name__ == "__main__":
    print("Metro Agent - Data Loader Test\n")

    try:
        test_station_mappings()
        test_department_routing()
        test_intent_examples()

        if test_validation():
            print("\n🎉 Tüm testler başarılı!")
        else:
            print("\n❌ Bazı testler başarısız!")

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
