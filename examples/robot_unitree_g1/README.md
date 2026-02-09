# Przykłady Zenoh dla Robota Unitree G1 EDU-U6

## Wprowadzenie

Ten katalog zawiera kompletny zestaw przykładów demonstrujących praktyczne zastosowanie protokołu Zenoh do budowy systemu komunikacyjnego dla robota humanoidalnego **Unitree G1 EDU-U6**.

Przykłady są zaprojektowane tak, aby można je było uruchomić niezależnie (symulacja) lub zintegrować z rzeczywistym robotem.

---

## Struktura przykładów

### 1. `robot_telemetry_publisher.py` 📡
**Publikator telemetrii robota**

- **Co robi:** Publikuje pozycję, orientację i stan baterii robota
- **Częstotliwość:** 10 Hz (konfigurowalna)
- **Klucze Zenoh:**
  - `robot/g1/state/pose` - pozycja (x, y, z, heading)
  - `robot/g1/state/battery` - poziom baterii
  - `robot/g1/sensors/imu/orientation` - orientacja (roll, pitch, yaw)

### 2. `robot_motion_controller.py` 🎮
**Kontroler ruchu robota**

- **Co robi:** Odbiera i wykonuje komendy ruchu
- **Subskrybuje:** `robot/g1/commands/motion/**`
- **Typy komend:**
  - `walk` - chód z zadaną prędkością (vx, vy, omega)
  - `stop` - zatrzymanie
  - `pose` - ruch do pozycji docelowej (x, y, heading)

### 3. `operator_station.py` 🖥️
**Stacja operatorska**

- **Co robi:** Interaktywny interfejs do wysyłania komend do robota
- **Menu:** Gotowe komendy (przód, tył, obrót, stop, cel)
- **Używa:** `z_put` do wysyłania komend

### 4. `robot_config_service.py` ⚙️
**Serwis konfiguracji (Queryable)**

- **Co robi:** Odpowiada na zapytania o konfigurację robota
- **Klucze Zenoh:**
  - `robot/g1/config/pid_gains` - wzmocnienia PID
  - `robot/g1/config/joint_limits` - limity stawów
  - `robot/g1/config/max_velocity` - maksymalne prędkości
  - `robot/g1/config/safety` - parametry bezpieczeństwa

### 5. `health_monitor.py` 🏥
**Monitor zdrowia systemu**

- **Co robi:** Monitoruje które moduły są aktywne
- **Używa:** Liveness tokens do wykrywania awarii
- **Wyświetla:** Status, uptime, alarmy dla modułów krytycznych

---

## Szybki start

### Scenariusz 1: Podstawowa symulacja

**Terminal 1 - Monitor zdrowia:**
```bash
python3 health_monitor.py
```

**Terminal 2 - Kontroler ruchu:**
```bash
python3 robot_motion_controller.py
```

**Terminal 3 - Telemetria:**
```bash
python3 robot_telemetry_publisher.py
```

**Terminal 4 - Stacja operatorska:**
```bash
python3 operator_station.py
```

**Obserwuj:**
- Monitor wyświetli status wszystkich modułów
- Stacja pozwoli wysyłać komendy
- Kontroler wykona komendy
- Telemetria publikuje pozycję robota

### Scenariusz 2: Konfiguracja

**Terminal 1 - Serwis konfiguracji:**
```bash
python3 robot_config_service.py
```

**Terminal 2 - Zapytania:**
```bash
# Cała konfiguracja
python3 ../z_get.py -s 'robot/g1/config/**'

# Tylko PID gains
python3 ../z_get.py -s 'robot/g1/config/pid_gains'

# Tylko limity
python3 ../z_get.py -s 'robot/g1/config/joint_limits'
```

### Scenariusz 3: Monitoring telemetrii

**Terminal 1 - Telemetria:**
```bash
python3 robot_telemetry_publisher.py --interval 0.1
```

**Terminal 2 - Wszystkie dane:**
```bash
python3 ../z_sub.py -k 'robot/g1/**'
```

**Terminal 3 - Tylko pozycja:**
```bash
python3 ../z_sub.py -k 'robot/g1/state/pose'
```

**Terminal 4 - Tylko bateria:**
```bash
python3 ../z_sub.py -k 'robot/g1/state/battery'
```

---

## Architektura systemu

```
┌─────────────────────────────────────────────────────────┐
│                    Zenoh Network                        │
│              (automatyczne peer discovery)              │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │Telemetry│   │ Motion  │   │ Config  │   │ Health  │
    │Publisher│   │Controller   │ Service │   │ Monitor │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
         ↓              ↑              ↑              ↑
         │              │              │              │
    ┌────┴──────────────┴──────────────┴──────────────┴───┐
    │            Operator Station / Other Apps             │
    └──────────────────────────────────────────────────────┘
```

---

## Hierarchia kluczy (Key Structure)

```
robot/g1/
├── state/                    # Stan robota (Publisher)
│   ├── pose                  # Pozycja i orientacja
│   └── battery               # Poziom baterii
│
├── sensors/                  # Dane czujników (Publisher)
│   └── imu/
│       └── orientation       # Orientacja IMU
│
├── commands/                 # Komendy sterujące (Subscriber)
│   └── motion/
│       ├── walk              # Komenda chodu
│       ├── stop              # Zatrzymanie
│       └── pose              # Ruch do pozycji
│
├── config/                   # Konfiguracja (Queryable)
│   ├── pid_gains             # Wzmocnienia PID
│   ├── joint_limits          # Limity stawów
│   ├── max_velocity          # Maksymalne prędkości
│   └── safety                # Parametry bezpieczeństwa
│
└── health/                   # Monitoring (Liveness)
    └── liveness/
        ├── motion_controller
        ├── config_service
        └── telemetry
```

---

## Zadania dla studentów

### Poziom 1 - Podstawy

1. **Uruchom wszystkie moduły** i obserwuj ich interakcje
2. **Wyślij różne komendy** przez stację operatorską
3. **Zatrzymaj moduł** i obserwuj reakcję health monitora
4. **Zmień częstotliwość telemetrii** i zaobserwuj wpływ

### Poziom 2 - Modyfikacje

5. **Dodaj nowy typ komendy** (np. sit, stand, jump)
6. **Rozszerz telemetrię** o nowe dane (temperatura, siły kontaktu)
7. **Dodaj nowy parametr konfiguracji** (np. walk parameters)
8. **Zaimplementuj zapis danych** telemetrii do pliku CSV

### Poziom 3 - Zaawansowane

9. **Stwórz wizualizację** pozycji robota (matplotlib, pygame)
10. **Dodaj kontroler z joysticka** zamiast menu
11. **Zaimplementuj planowanie trajektorii** (path planning)
12. **Dodaj persystencję konfiguracji** (zapis/odczyt z pliku)
13. **Stwórz webowy dashboard** (Flask + JavaScript)
14. **Integruj z prawdziwym robotem** (jeśli dostępny)

---

## Rozszerzenia

### Integracja z prawdziwym robotem

Aby zintegrować z prawdziwym robotem Unitree G1:

1. **W `robot_telemetry_publisher.py`:**
   - Zastąp symulację odczytem z SDK robota
   - Odczytuj rzeczywiste dane z enkoderów, IMU, etc.

2. **W `robot_motion_controller.py`:**
   - Dodaj wysyłanie komend do SDK robota
   - Implementuj bezpieczne sprawdzanie limitów

3. **Dodaj moduł bezpieczeństwa:**
   - Emergency stop przy krytycznych błędach
   - Monitoring granic przestrzeni roboczej
   - Zabezpieczenie przed kolizjami

### Dodatkowe moduły do zaimplementowania

- **Perception:** Przetwarzanie obrazu z kamer
- **Localization:** Estymacja pozycji (SLAM)
- **Navigation:** Planowanie ścieżek i unikanie przeszkód
- **Manipulation:** Sterowanie chwytakiem
- **Logging:** Zapis wszystkich danych do bazy

---

## Najczęstsze problemy

### Problem: Moduły się nie widzą

**Rozwiązanie:**
- Sprawdź firewall (port 7447 UDP)
- Uruchom `z_scout.py` aby zobaczyć wykryte węzły
- Użyj `-e tcp/localhost:7447` jeśli multicast nie działa

### Problem: Wysokie opóźnienia

**Rozwiązanie:**
- Zmniejsz częstotliwość publikacji
- Użyj shared memory dla dużych danych
- Sprawdź obciążenie sieci/CPU

### Problem: Moduły nie zatrzymują się poprawnie

**Rozwiązanie:**
- Używaj CTRL-C (KeyboardInterrupt)
- Upewnij się, że sesje są w `with` block
- Dodaj proper cleanup w finally block

---

## Dalsze kroki

1. 📖 **Przeczytaj:** [UNITREE_G1_GUIDE.pl.md](../../UNITREE_G1_GUIDE.pl.md)
2. 📚 **Dokumentacja:** [README.pl.md](../../README.pl.md)
3. 🎓 **Przykłady Zenoh:** [examples/README.pl.md](../README.pl.md)
4. 🌐 **Zenoh docs:** https://zenoh.io/docs/

---

## Kontakt i pomoc

- **Issues:** Zgłaszaj problemy przez GitHub Issues
- **Discord:** Dołącz do społeczności Zenoh
- **Dokumentacja:** https://zenoh-python.readthedocs.io/

---

**Powodzenia w pracy z robotem Unitree G1! 🤖🚀**
