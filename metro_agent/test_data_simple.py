#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit data loader test - bağımlılık gerektirmez
"""

import json
import sys
from pathlib import Path

# UTF-8 encoding için
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"


def test_json_files():
    """JSON dosyalarının geçerliliğini test et"""
    print("Metro Agent - Data Files Test\n")

    files = [
        "station_mappings.json",
        "department_routing.json",
        "intent_examples.json"
    ]

    for filename in files:
        filepath = DATA_DIR / filename
        print(f"Testing {filename}...")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Dosya türüne göre kontrol
            if "station_mappings" in filename:
                assert "aliases" in data, "Missing 'aliases' key"
                assert "lines" in data, "Missing 'lines' key"
                print(f"  ✓ {len(data['aliases'])} aliases found")
                print(f"  ✓ {len(data['lines'])} stations with line info")

            elif "department_routing" in filename:
                assert "departments" in data, "Missing 'departments' key"
                assert "priority_rules" in data, "Missing 'priority_rules' key"
                print(f"  ✓ {len(data['departments'])} departments found")
                print(f"  ✓ {len(data['priority_rules'])} priority rules found")

                # Test bir department
                escalator = data['departments'].get('ESCALATOR')
                if escalator:
                    print(f"  ✓ ESCALATOR -> {escalator['name']}")
                    print(f"  ✓ CRITICAL SLA: {escalator['sla_hours']['CRITICAL']} hours")

            elif "intent_examples" in filename:
                total_examples = sum(len(examples) for examples in data.values())
                print(f"  ✓ {len(data)} intent types found")
                print(f"  ✓ {total_examples} total examples")

                # İlk örnek
                for intent, examples in data.items():
                    print(f"  ✓ {intent}: {len(examples)} examples")
                    if examples:
                        print(f"     Example: '{examples[0]}'")
                    break

            print(f"  ✅ {filename} is valid!\n")

        except FileNotFoundError:
            print(f"  ❌ File not found: {filepath}\n")
            return False

        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}\n")
            return False

        except AssertionError as e:
            print(f"  ❌ Validation error: {e}\n")
            return False

    return True


if __name__ == "__main__":
    try:
        if test_json_files():
            print("🎉 All data files are valid and properly formatted!")
        else:
            print("❌ Some data files have issues!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
