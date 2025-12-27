# Metro Agent - Data Integration Dokümantasyonu

## Özet

Projedeki tüm data dosyaları artık **düzgün bir şekilde entegre edilmiş durumda**. Daha önce kullanılmayan JSON dosyaları şimdi aktif olarak yükleniyor ve sistemde kullanılıyor.

## Yapılan Değişiklikler

### 1. Data Dosyaları Düzenlendi ✅

Tüm data dosyaları Python string değişkenlerinden **gerçek JSON dosyalarına** dönüştürüldü:

- `data/station_mappings.json` - 20 alias, 10 istasyon
- `data/department_routing.json` - 12 departman, 8 priority kuralı
- `data/intent_examples.json` - 10 intent tipi, 52 örnek

### 2. Data Loader Modülü Oluşturuldu ✅

**Dosya:** [src/utils/data_loader.py](f:\tech-istanbul-zihin-code\metro_agent\src\utils\data_loader.py)

**Fonksiyonlar:**
```python
# Ana yükleme fonksiyonları
load_station_mappings()      # İstasyon alias ve hatları
load_department_routing()    # Department ve SLA bilgileri
load_intent_examples()       # Intent örnekleri

# Yardımcı fonksiyonlar
get_station_aliases()                      # Alias dictionary
get_station_lines()                        # İstasyon -> hat mapping
get_department_info(equipment_category)    # Department bilgisi
get_sla_hours(equipment, priority)         # SLA süresi
get_priority_from_description(text)        # Açıklamadan priority çıkar
get_intent_examples_for_prompt()           # LLM için örnekler

# Validation
validate_data_files()        # Tüm dosyaları doğrula
preload_data()              # Başlangıçta cache'e yükle
```

**Özellikler:**
- `@lru_cache` ile performans optimizasyonu
- Hata durumunda fallback değerler
- Detaylı logging

### 3. Validators Güncellendi ✅

**Dosya:** [src/utils/validators.py](f:\tech-istanbul-zihin-code\metro_agent\src\utils\validators.py)

**Değişiklik:**
- Hardcoded `STATION_ALIASES` dictionary kaldırıldı
- `normalize_station_name()` artık `get_station_aliases()` kullanıyor
- Data dosyasındaki 20 alias otomatik yükleniyor

**Önce:**
```python
STATION_ALIASES = {
    "mecidiyekoy": "mecidiyeköy",
    # ... hardcoded
}
```

**Sonra:**
```python
from src.utils.data_loader import get_station_aliases

def normalize_station_name(name: str) -> str:
    station_aliases = get_station_aliases()
    if normalized in station_aliases:
        return station_aliases[normalized]
```

### 4. Fault Manager Güncellendi ✅

**Dosya:** [src/modules/fault_manager.py](f:\tech-istanbul-zihin-code\metro_agent\src\modules\fault_manager.py)

**Değişiklikler:**
- `_default_classification()` artık data dosyasından SLA bilgisi alıyor
- Department routing otomatik yapılıyor
- Priority kuralları data'dan okunuyor

**Önce:**
```python
def _default_classification(fault_entity):
    return FaultClassification(
        target_department="Teknik Bakım Müdürlüğü",  # Hardcoded
        estimated_hours=4  # Hardcoded
    )
```

**Sonra:**
```python
def _default_classification(fault_entity):
    # Priority'yi açıklamadan çıkar
    priority = get_priority_from_description(description)

    # Department bilgisini data'dan al
    dept_info = get_department_info(category.value)
    target_department = dept_info.get("name")

    # SLA saatini data'dan al
    sla_hours = get_sla_hours(category.value, priority)

    return FaultClassification(
        target_department=target_department,
        estimated_hours=int(sla_hours),
        sla_hours=int(sla_hours)
    )
```

### 5. Intent Classifier Güncellendi ✅

**Dosya:** [src/agent/intent_classifier.py](f:\tech-istanbul-zihin-code\metro_agent\src\agent\intent_classifier.py)

**Değişiklikler:**
- Sistem promptu artık dinamik olarak oluşturuluyor
- Intent örnekleri LLM context'ine ekleniyor
- Her intent için 3 örnek gösteriliyor

**Önce:**
```python
class IntentClassifier:
    SYSTEM_PROMPT = """..."""  # Statik prompt
```

**Sonra:**
```python
class IntentClassifier:
    @staticmethod
    def _build_system_prompt() -> str:
        examples = get_intent_examples_for_prompt()
        # Intent örneklerini prompt'a ekle
        return base_prompt + examples + ...

    def __init__(self, llm_client):
        self.system_prompt = self._build_system_prompt()
```

### 6. Startup Validation Eklendi ✅

**Dosya:** [main.py](f:\tech-istanbul-zihin-code\metro_agent\main.py)

**Değişiklikler:**
- Uygulama başlarken tüm data dosyaları doğrulanıyor
- Hata varsa uygulama başlamıyor
- Data dosyaları önceden cache'e yükleniyor

```python
def startup():
    """Uygulama başlangıç kontrolleri"""
    logger.info("Validating data files...")
    if not validate_data_files():
        logger.error("Data validation failed!")
        sys.exit(1)

    preload_data()
    logger.info("Startup complete")
```

### 7. Eksik __init__.py Dosyaları Oluşturuldu ✅

- `src/__init__.py` ✅
- `src/utils/__init__.py` ✅ (güncellendi)
- `src/models/__init__.py` ✅

### 8. Birleştirilmiş Dosyalar Düzeltildi ✅

Daha önce yanlışlıkla birden fazla dosyanın içeriği birleştirilmişti:

- [config.py](f:\tech-istanbul-zihin-code\metro_agent\src\config.py) - `src/models/__init__.py` içeriği kaldırıldı ✅
- [report.py](f:\tech-istanbul-zihin-code\metro_agent\src\models\report.py) - `src/utils/__init__.py` içeriği kaldırıldı ✅
- [fault.py](f:\tech-istanbul-zihin-code\metro_agent\src\models\fault.py) - `station.py` içeriği kaldırıldı ✅
- [service_status.py](f:\tech-istanbul-zihin-code\metro_agent\src\modules\service_status.py) - `direction_helper.py` içeriği kaldırıldı ✅

Yeni dosya oluşturuldu:
- [station.py](f:\tech-istanbul-zihin-code\metro_agent\src\models\station.py) ✅

## Kullanım Örnekleri

### İstasyon Alias Kullanımı

```python
from src.utils.validators import normalize_station_name

# "mecidiyekoy" -> "Mecidiyeköy" (data dosyasından)
normalized = normalize_station_name("mecidiyekoy")
```

### SLA Hesaplama

```python
from src.utils.data_loader import get_sla_hours
from src.models.fault import FaultCategory, Priority

# ESCALATOR + CRITICAL -> 1 saat (data dosyasından)
hours = get_sla_hours(FaultCategory.ESCALATOR.value, Priority.CRITICAL.value)
```

### Priority Detection

```python
from src.utils.data_loader import get_priority_from_description

# "Tren durdu" içeren metin -> CRITICAL
priority = get_priority_from_description("Tren durdu, yardım edin!")
```

### Department Routing

```python
from src.utils.data_loader import get_department_info

# ELEVATOR -> "Elektromekanik Bakım Müdürlüğü"
dept = get_department_info("ELEVATOR")
print(dept["name"])  # Elektromekanik Bakım Müdürlüğü
print(dept["sub_unit"])  # Asansör Ekibi
```

## Test Sonuçları

Test scripti çalıştırıldı: [test_data_simple.py](f:\tech-istanbul-zihin-code\metro_agent\test_data_simple.py)

```
✅ station_mappings.json - 20 aliases, 10 stations
✅ department_routing.json - 12 departments, 8 priority rules
✅ intent_examples.json - 10 intents, 52 examples
🎉 All data files are valid!
```

## Faydalar

1. **Merkezi Veri Yönetimi**
   - Tüm data tek yerden yönetiliyor
   - Güncellemeler kod değişikliği gerektirmiyor

2. **Bakım Kolaylığı**
   - JSON dosyalarını düzenlemek Python kodu düzenlemekten kolay
   - Teknik olmayan kişiler de güncelleyebilir

3. **Performans**
   - `@lru_cache` ile datalar bir kez yükleniyor
   - Tekrar tekrar dosya okuma yok

4. **Güvenilirlik**
   - Başlangıçta validation yapılıyor
   - Hatalı data ile uygulama başlamıyor

5. **Genişletilebilirlik**
   - Yeni data dosyaları kolayca eklenebilir
   - Yeni fonksiyonlar kolayca yazılabilir

## Önemli Notlar

⚠️ **Data Dosyalarını Düzenlerken:**
- JSON syntax'ına dikkat edin
- Mevcut key'leri silmeyin
- Encoding UTF-8 olmalı

⚠️ **Production'da:**
- Data dosyalarını backup alın
- Değişikliklerden sonra `python test_data_simple.py` çalıştırın
- Uygulama restart edin (cache temizlenir)

## İletişim & Destek

Herhangi bir sorunuz veya öneriniz varsa lütfen bildirin!
