# Przewodnik Zenoh dla Robota Unitree G1 EDU-U6

## Wprowadzenie

Ten przewodnik wyjaśnia, jak wykorzystać protokół Zenoh do budowy systemów komunikacyjnych dla robota humanoidalnego **Unitree G1 EDU-U6**. 

### O robocie Unitree G1 EDU-U6

**Unitree G1 EDU-U6** to zaawansowany robot humanoidalny charakteryzujący się:
- **23 stopnie swobody (DOF)** - realistyczne ruchy przypominające ludzkie
- **Wzrost:** około 127 cm
- **Waga:** około 35 kg
- **Zaawansowane czujniki:**
  - Kamery stereo (depth sensing)
  - IMU (Inertial Measurement Unit) - jednostka pomiarów bezwładnościowych
  - Enkodery w stawach (joint encoders)
  - Czujniki siły/momentu (force/torque sensors)
- **Możliwości:**
  - Chodzenie dwunożne
  - Manipulacja obiektami
  - Interakcja z otoczeniem
  - AI-driven behaviors

---

## Dlaczego Zenoh dla robota humanoidalnego?

### Wyzwania w robotyce humanoidalnej

Robot humanoidalny to złożony system wymagający:

1. **Komunikacji w czasie rzeczywistym**
   - Kontrola 23 stawów z częstotliwością >100Hz
   - Latencja <10ms dla stabilności chodu
   - Synchronizacja wielu kontrolerów

2. **Dużej przepustowości danych**
   - Obrazy z kamer: ~180 MB/s (1080p @ 30fps × 2 kamery)
   - Point clouds z depth sensor: dziesiątki MB/s
   - Telemetria z wszystkich czujników

3. **Skalowalności**
   - Wiele modułów oprogramowania (perception, planning, control)
   - Komunikacja między robotem a stacją bazową
   - Możliwość dodawania nowych komponentów

4. **Niezawodności**
   - Failure detection i recovery
   - Graceful degradation (degradacja zamiast awarii)
   - Monitoring systemu

### Rozwiązania Zenoh

| Wymaganie | Rozwiązanie Zenoh |
|-----------|-------------------|
| Niska latencja | Zero-copy w SHM, efektywny routing |
| Wysoka przepustowość | Shared memory, batching, compression |
| Skalowalność | Dinamiczne discovery, geo-distributed |
| Elastyczność | Pub/Sub + Query/Queryable w jednym |
| Monitoring | Liveness tokens, built-in monitoring |

---

## Architektura systemu dla Unitree G1

### Przykładowa architektura oparta na Zenoh

```
┌─────────────────────────────────────────────────────────┐
│                    Zenoh Router                         │
│            (opcjonalnie - dla WAN/routing)              │
└─────────────────────────────────────────────────────────┘
           │                  │                  │
    ┌──────┴──────┐    ┌──────┴──────┐   ┌──────┴──────┐
    │   Robot     │    │   Operator  │   │   Monitor   │
    │  Unitree G1 │    │   Station   │   │   Station   │
    └─────────────┘    └─────────────┘   └─────────────┘
```

### Komponenty na robocie

1. **Low-Level Control** (niska warstwa sterowania)
   - Bezpośrednie sterowanie silnikami
   - Odczyt enkoderów i czujników
   - Częstotliwość: 200-1000 Hz

2. **Sensor Processing** (przetwarzanie czujników)
   - Fusion danych z IMU
   - Przetwarzanie obrazu z kamer
   - Częstotliwość: 30-60 Hz

3. **High-Level Control** (wysoka warstwa sterowania)
   - Planowanie ruchu
   - Balance control (kontrola balansu)
   - Gait generation (generowanie chodu)
   - Częstotliwość: 10-50 Hz

4. **State Publisher** (publikator stanu)
   - Aktualna pozycja/orientacja
   - Stan stawów
   - Stan baterii/temperatury
   - Częstotliwość: 10-30 Hz

---

## Hierarchia kluczy (Key Expressions) dla Unitree G1

Zenoh używa hierarchicznych kluczy podobnych do ścieżek plików. Dobrze zaprojektowana hierarchia jest kluczowa dla efektywnej komunikacji.

### Proponowana struktura

```
robot/g1/
├── state/                    # Stan robota
│   ├── pose                  # Pozycja i orientacja (x,y,z, roll,pitch,yaw)
│   ├── velocity              # Prędkość liniowa i kątowa
│   ├── battery               # Poziom baterii (%)
│   └── temperature           # Temperatura komponentów
│
├── joints/                   # Stawy
│   ├── left_arm/
│   │   ├── shoulder/pitch    # Konkretny staw
│   │   ├── shoulder/roll
│   │   ├── shoulder/yaw
│   │   ├── elbow
│   │   └── wrist
│   ├── right_arm/
│   │   └── ...
│   ├── left_leg/
│   │   ├── hip/pitch
│   │   ├── hip/roll
│   │   ├── hip/yaw
│   │   ├── knee
│   │   └── ankle
│   ├── right_leg/
│   │   └── ...
│   └── torso/
│       └── ...
│
├── sensors/                  # Czujniki
│   ├── imu/
│   │   ├── acceleration      # Przyspieszenie (ax,ay,az)
│   │   ├── gyroscope         # Prędkość kątowa (gx,gy,gz)
│   │   └── orientation       # Orientacja (quaternion lub euler)
│   ├── cameras/
│   │   ├── left/image        # Obraz z lewej kamery
│   │   ├── right/image       # Obraz z prawej kamery
│   │   └── depth/pointcloud  # Chmura punktów
│   └── force/
│       ├── left_foot         # Siła w lewej stopie
│       └── right_foot        # Siła w prawej stopie
│
├── commands/                 # Komendy sterujące
│   ├── motion/
│   │   ├── walk              # Komenda chodu (vx,vy,omega)
│   │   ├── stop              # Zatrzymanie
│   │   └── pose              # Pozycja docelowa
│   ├── joints/target         # Docelowe pozycje stawów
│   └── mode                  # Tryb pracy (stand, walk, sit)
│
├── config/                   # Konfiguracja (Query/Queryable)
│   ├── gains                 # Wzmocnienia PID
│   ├── limits                # Limity stawów
│   └── calibration           # Kalibracja
│
└── health/                   # Health monitoring
    ├── status                # OPERATIONAL/ERROR/WARNING
    ├── errors                # Lista błędów
    └── liveness/module_name  # Liveness tokens dla modułów
```

### Przykłady subskrypcji

```python
# Wszystkie dane robota
'robot/g1/**'

# Tylko stan
'robot/g1/state/**'

# Wszystkie stawy
'robot/g1/joints/**'

# Tylko lewa ręka
'robot/g1/joints/left_arm/**'

# Wszystkie kamery
'robot/g1/sensors/cameras/**'

# Konkretny czujnik
'robot/g1/sensors/imu/acceleration'
```

---

## Przykład 1: Publikowanie telemetrii robota

### Scenariusz
Robot publikuje swoją pozycję, orientację i stan baterii w czasie rzeczywistym.

### Kod: `robot_telemetry_publisher.py`

```python
#!/usr/bin/env python3
"""
Przykład: Publikowanie telemetrii robota Unitree G1
Symuluje publikowanie pozycji, orientacji i stanu baterii.
"""

import time
import json
import math
import zenoh

def main():
    # Inicjalizacja logowania
    # 'error' - tylko błędy, można zmienić na 'debug' dla szczegółów
    zenoh.init_log_from_env_or("error")
    
    print("🤖 Uruchamianie modułu telemetrii robota Unitree G1...")
    
    # Konfiguracja Zenoh
    # Config() używa domyślnych ustawień (peer mode, auto-discovery)
    conf = zenoh.Config()
    
    # Otwieranie sesji Zenoh
    # Sesja to główny punkt interakcji z Zenoh
    print("📡 Otwieranie sesji Zenoh...")
    with zenoh.open(conf) as session:
        
        # Deklarowanie publisher'ów dla różnych typów danych
        # Publisher to zadeklarowany "nadajnik" dla konkretnego klucza
        # Deklaracja zwiększa wydajność (vs. pojedyncze put)
        
        print("📢 Deklarowanie publisher'ów...")
        pub_pose = session.declare_publisher("robot/g1/state/pose")
        pub_battery = session.declare_publisher("robot/g1/state/battery")
        pub_imu = session.declare_publisher("robot/g1/sensors/imu/orientation")
        
        print("✅ Robot gotowy do publikowania danych!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # Symulowane dane początkowe
        x, y, z = 0.0, 0.0, 0.0  # Pozycja w metrach
        heading = 0.0             # Kierunek w radianach
        battery_level = 100.0     # Procent baterii
        
        try:
            # Główna pętla publikowania
            idx = 0
            while True:
                # ============================================
                # KROK 1: Symulacja ruchu robota
                # ============================================
                # Robot porusza się w okręgu
                # W prawdziwej aplikacji: odczyt z rzeczywistych czujników
                
                idx += 1
                t = idx * 0.1  # Czas symulacji
                
                # Ruch po okręgu o promieniu 2m
                radius = 2.0
                angular_speed = 0.2  # rad/s
                x = radius * math.cos(angular_speed * t)
                y = radius * math.sin(angular_speed * t)
                z = 0.0  # Robot na ziemi
                heading = angular_speed * t + math.pi/2  # Kierunek jazdy
                
                # Normalizacja kierunku do zakresu [0, 2π]
                heading = heading % (2 * math.pi)
                
                # Symulacja rozładowania baterii
                battery_level = max(0, 100 - t * 0.1)
                
                # ============================================
                # KROK 2: Przygotowanie danych do wysłania
                # ============================================
                # Zenoh przesyła surowe bajty
                # Możemy użyć JSON dla czytelności (lub binary dla wydajności)
                
                # Dane pozycji (pose)
                pose_data = {
                    "x": round(x, 3),
                    "y": round(y, 3), 
                    "z": round(z, 3),
                    "heading": round(heading, 3),
                    "timestamp": time.time()
                }
                
                # Dane IMU (orientacja jako kąty Eulera)
                imu_data = {
                    "roll": 0.0,   # Przechył na boki
                    "pitch": 0.0,  # Przechył przód-tył
                    "yaw": round(heading, 3),  # Obrót wokół osi Z
                    "timestamp": time.time()
                }
                
                # ============================================
                # KROK 3: Publikowanie danych
                # ============================================
                
                # Publikuj pozycję
                # JSON → string → bytes (UTF-8)
                pub_pose.put(json.dumps(pose_data))
                
                # Publikuj stan baterii
                # Prosty format: tylko wartość
                pub_battery.put(str(battery_level))
                
                # Publikuj orientację IMU
                pub_imu.put(json.dumps(imu_data))
                
                # ============================================
                # KROK 4: Wyświetl info (co 10 iteracji)
                # ============================================
                if idx % 10 == 0:
                    print(f"[{idx:4d}] 📍 Pozycja: ({x:6.2f}, {y:6.2f})  "
                          f"🧭 Kierunek: {math.degrees(heading):6.1f}°  "
                          f"🔋 Bateria: {battery_level:5.1f}%")
                
                # Czekaj 100ms przed następną iteracją
                # W rzeczywistym systemie: synchronizacja z częstotliwością czujników
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie publikatora telemetrii...")
    
    print("✅ Moduł telemetrii zakończony.")

if __name__ == "__main__":
    main()
```

### Uruchomienie

Terminal 1 - Robot (publikuje dane):
```bash
python3 robot_telemetry_publisher.py
```

Terminal 2 - Monitor (subskrybuje dane):
```bash
# Wszystkie dane robota
python3 z_sub.py -k 'robot/g1/**'

# Tylko pozycja
python3 z_sub.py -k 'robot/g1/state/pose'

# Tylko bateria
python3 z_sub.py -k 'robot/g1/state/battery'
```

---

## Przykład 2: Kontrola ruchu robota

### Scenariusz
Stacja operatorska wysyła komendy ruchu do robota.

### Kod: `robot_motion_controller.py`

```python
#!/usr/bin/env python3
"""
Przykład: Kontroler ruchu robota Unitree G1
Subskrybuje komendy ruchu i symuluje wykonanie.
"""

import time
import json
import zenoh

def main():
    zenoh.init_log_from_env_or("error")
    
    print("🎮 Uruchamianie kontrolera ruchu robota...")
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("📡 Połączono z Zenoh")
        
        # ============================================
        # Callback wywoływany przy otrzymaniu komendy
        # ============================================
        def motion_callback(sample: zenoh.Sample):
            """
            Funkcja wywoływana automatycznie gdy przyjdzie nowa komenda ruchu.
            
            Args:
                sample: Otrzymany sample z Zenoh
                    - sample.key_expr: klucz (np. 'robot/g1/commands/motion/walk')
                    - sample.payload: dane (bytes)
                    - sample.kind: typ (PUT, DELETE)
            """
            
            # Konwersja payload (bytes) na string
            command = sample.payload.to_string()
            
            print(f"\n📨 Otrzymano komendę: {sample.key_expr}")
            print(f"   Payload: {command}")
            
            try:
                # Parsowanie JSON
                data = json.loads(command)
                
                # Sprawdzenie typu komendy na podstawie klucza
                if "walk" in sample.key_expr:
                    # Komenda chodu
                    vx = data.get("vx", 0.0)  # Prędkość do przodu [m/s]
                    vy = data.get("vy", 0.0)  # Prędkość w bok [m/s]
                    omega = data.get("omega", 0.0)  # Prędkość kątowa [rad/s]
                    
                    print(f"   🚶 Wykonuję chód: vx={vx}, vy={vy}, omega={omega}")
                    
                    # TU: Wysłanie do low-level controller
                    # send_to_robot_controller(vx, vy, omega)
                    
                elif "stop" in sample.key_expr:
                    print(f"   🛑 Zatrzymuję robota!")
                    # send_to_robot_controller(0, 0, 0)
                    
                elif "pose" in sample.key_expr:
                    # Docelowa pozycja
                    x = data.get("x", 0.0)
                    y = data.get("y", 0.0)
                    heading = data.get("heading", 0.0)
                    
                    print(f"   🎯 Cel: x={x}, y={y}, heading={heading}")
                    # plan_motion_to_goal(x, y, heading)
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Błąd parsowania JSON: {e}")
            except Exception as e:
                print(f"   ❌ Błąd wykonania: {e}")
        
        # ============================================
        # Subskrypcja komend ruchu
        # ============================================
        # Dopasowanie wszystkich komend pod robot/g1/commands/motion/
        print("🎧 Subskrybowanie komend ruchu...")
        subscriber = session.declare_subscriber(
            "robot/g1/commands/motion/**",
            motion_callback
        )
        
        print("✅ Kontroler gotowy do przyjmowania komend!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # Liveness token - sygnalizacja że moduł działa
        # Jeśli proces umrze, token zniknie
        liveness_token = session.liveliness().declare_token(
            "robot/g1/health/liveness/motion_controller"
        )
        print("💚 Liveness token aktywny")
        
        # Pętla główna - czeka na komendy
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie kontrolera...")
    
    print("✅ Kontroler zakończony.")

if __name__ == "__main__":
    main()
```

### Kod: `operator_station.py`

```python
#!/usr/bin/env python3
"""
Przykład: Stacja operatorska - wysyłanie komend do robota
"""

import json
import zenoh

def main():
    zenoh.init_log_from_env_or("error")
    
    print("🖥️  Stacja operatorska robota Unitree G1")
    print("=" * 50)
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("✅ Połączono z Zenoh\n")
        
        # Menu komend
        while True:
            print("\nDostępne komendy:")
            print("  1 - Chód do przodu (0.5 m/s)")
            print("  2 - Chód do tyłu (0.5 m/s)")
            print("  3 - Obrót w lewo (0.3 rad/s)")
            print("  4 - Obrót w prawo (0.3 rad/s)")
            print("  5 - Stop")
            print("  6 - Idź do pozycji (2, 3)")
            print("  q - Quit")
            
            choice = input("\nWybierz komendę: ").strip()
            
            if choice == 'q':
                break
            
            # Przygotowanie komendy
            key = None
            payload = None
            
            if choice == '1':
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({"vx": 0.5, "vy": 0.0, "omega": 0.0})
            elif choice == '2':
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({"vx": -0.5, "vy": 0.0, "omega": 0.0})
            elif choice == '3':
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({"vx": 0.0, "vy": 0.0, "omega": 0.3})
            elif choice == '4':
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({"vx": 0.0, "vy": 0.0, "omega": -0.3})
            elif choice == '5':
                key = "robot/g1/commands/motion/stop"
                payload = json.dumps({})
            elif choice == '6':
                key = "robot/g1/commands/motion/pose"
                payload = json.dumps({"x": 2.0, "y": 3.0, "heading": 0.0})
            else:
                print("❌ Nieprawidłowy wybór")
                continue
            
            # Wysłanie komendy
            print(f"📤 Wysyłanie: {key}")
            print(f"   Dane: {payload}")
            session.put(key, payload)
            print("✅ Komenda wysłana!")
    
    print("\n👋 Do widzenia!")

if __name__ == "__main__":
    main()
```

### Uruchomienie

Terminal 1 - Robot (odbiera komendy):
```bash
python3 robot_motion_controller.py
```

Terminal 2 - Operator (wysyła komendy):
```bash
python3 operator_station.py
```

Terminal 3 - Monitor (opcjonalnie):
```bash
python3 z_sub.py -k 'robot/g1/commands/**'
```

---

## Przykład 3: Query/Queryable - Konfiguracja robota

### Scenariusz
Odpytywanie i modyfikacja konfiguracji robota (PID gains, limity).

### Kod: `robot_config_service.py`

```python
#!/usr/bin/env python3
"""
Przykład: Serwis konfiguracji robota (Queryable)
Odpowiada na zapytania o konfigurację.
"""

import json
import zenoh

# Symulowana konfiguracja robota
CONFIG = {
    "pid_gains": {
        "left_arm": {"p": 10.0, "i": 0.5, "d": 2.0},
        "right_arm": {"p": 10.0, "i": 0.5, "d": 2.0},
        "left_leg": {"p": 15.0, "i": 1.0, "d": 3.0},
        "right_leg": {"p": 15.0, "i": 1.0, "d": 3.0},
    },
    "joint_limits": {
        "shoulder_pitch": {"min": -90, "max": 180},
        "elbow": {"min": 0, "max": 150},
        "knee": {"min": 0, "max": 150},
    },
    "max_velocity": {
        "linear": 1.5,  # m/s
        "angular": 1.0,  # rad/s
    }
}

def main():
    zenoh.init_log_from_env_or("error")
    
    print("⚙️  Uruchamianie serwisu konfiguracji robota...")
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        
        # ============================================
        # Queryable callback
        # ============================================
        def config_queryable(query: zenoh.Query):
            """
            Funkcja wywoływana gdy ktoś wysyła zapytanie.
            
            Args:
                query: Obiekt zapytania
                    - query.selector: klucz zapytania
                    - query.payload: opcjonalne dane zapytania
            """
            
            selector = query.selector
            print(f"\n📨 Otrzymano zapytanie: {selector}")
            
            # Parsowanie selektora
            # Przykład: robot/g1/config/pid_gains
            parts = str(selector).split('/')
            
            try:
                if "pid_gains" in str(selector):
                    # Zwróć PID gains
                    response = CONFIG["pid_gains"]
                    print(f"   📤 Odpowiadam: PID gains")
                    
                elif "joint_limits" in str(selector):
                    # Zwróć limity stawów
                    response = CONFIG["joint_limits"]
                    print(f"   📤 Odpowiadam: Joint limits")
                    
                elif "max_velocity" in str(selector):
                    # Zwróć max prędkości
                    response = CONFIG["max_velocity"]
                    print(f"   📤 Odpowiadam: Max velocity")
                    
                else:
                    # Zwróć całą konfigurację
                    response = CONFIG
                    print(f"   📤 Odpowiadam: Pełna konfiguracja")
                
                # Wysłanie odpowiedzi
                # reply() wysyła Sample z danymi
                query.reply(
                    zenoh.Sample(
                        selector,
                        json.dumps(response, indent=2)
                    )
                )
                
            except Exception as e:
                print(f"   ❌ Błąd: {e}")
                # Możemy wysłać błąd jako odpowiedź
                error_payload = json.dumps({"error": str(e)})
                query.reply_err(zenoh.Sample(selector, error_payload))
        
        # ============================================
        # Deklaracja Queryable
        # ============================================
        print("🎧 Deklarowanie queryable dla konfiguracji...")
        queryable = session.declare_queryable(
            "robot/g1/config/**",
            config_queryable
        )
        
        print("✅ Serwis konfiguracji gotowy!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # Czekaj na zapytania
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie serwisu...")
    
    print("✅ Serwis zakończony.")

if __name__ == "__main__":
    main()
```

### Odpytywanie konfiguracji

```bash
# Terminal 1 - Serwis
python3 robot_config_service.py

# Terminal 2 - Zapytania
# Cała konfiguracja
python3 z_get.py -s 'robot/g1/config/**'

# Tylko PID gains
python3 z_get.py -s 'robot/g1/config/pid_gains'

# Tylko limity stawów
python3 z_get.py -s 'robot/g1/config/joint_limits'
```

---

## Przykład 4: Health Monitoring z Liveness

### Kod: `health_monitor.py`

```python
#!/usr/bin/env python3
"""
Przykład: Monitoring zdrowia modułów robota
Monitoruje liveness tokens wszystkich modułów.
"""

import time
import zenoh

def main():
    zenoh.init_log_from_env_or("error")
    
    print("🏥 Uruchamianie monitora zdrowia robota...")
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        
        # Przechowywanie stanu modułów
        active_modules = set()
        
        # ============================================
        # Subscriber liveness
        # ============================================
        def liveness_callback(sample: zenoh.Sample):
            """Wywoływane gdy moduł się uruchomi lub zatrzyma"""
            
            module_name = str(sample.key_expr).split('/')[-1]
            
            if sample.kind == zenoh.SampleKind.PUT:
                # Moduł się uruchomił
                active_modules.add(module_name)
                print(f"✅ Moduł ONLINE: {module_name}")
            else:  # DELETE
                # Moduł się zatrzymał
                if module_name in active_modules:
                    active_modules.remove(module_name)
                print(f"❌ Moduł OFFLINE: {module_name}")
            
            # Wyświetl aktualny stan
            print(f"   📊 Aktywne moduły ({len(active_modules)}): {', '.join(active_modules)}")
        
        print("🎧 Subskrybowanie liveness tokens...")
        session.liveliness().declare_subscriber(
            "robot/g1/health/liveness/**",
            liveness_callback
        )
        
        print("✅ Monitor gotowy!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # Okresowe sprawdzanie
        try:
            while True:
                time.sleep(5)
                if len(active_modules) == 0:
                    print("⚠️  UWAGA: Brak aktywnych modułów!")
                else:
                    print(f"💚 OK: {len(active_modules)} modułów aktywnych")
                    
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie monitora...")
    
    print("✅ Monitor zakończony.")

if __name__ == "__main__":
    main()
```

---

## Optymalizacje dla robota

### 1. Shared Memory dla obrazów z kamer

Obrazy z kamer to duże dane (MB). Użyj SHM dla zero-copy:

```python
# Wymaga: pip install eclipse-zenoh --config-settings build-args="--features=zenoh/shared-memory"

import zenoh

conf = zenoh.Config()

# Włącz SHM
# Dokumentacja: https://zenoh.io/docs/manual/abstractions/#shared-memory

with zenoh.open(conf) as session:
    # Publisher z SHM
    pub = session.declare_publisher("robot/g1/sensors/cameras/left/image")
    
    # Przykład: wysłanie obrazu (numpy array)
    import numpy as np
    image = np.zeros((1080, 1920, 3), dtype=np.uint8)  # Dummy image
    
    # Konwersja do bytes i wysłanie
    pub.put(image.tobytes())
```

### 2. Batching dla telemetrii

Grupowanie wielu pomiarów w jeden sample:

```python
# Zamiast wysyłać każdy staw osobno (23 wiadomości):
# pub_joint_1.put(angle_1)
# pub_joint_2.put(angle_2)
# ...

# Wyślij wszystkie w jednej wiadomości (1 wiadomość):
all_joints = {
    "left_arm": [angle1, angle2, angle3, ...],
    "right_arm": [angle1, angle2, angle3, ...],
    # ...
    "timestamp": time.time()
}
pub_all_joints.put(json.dumps(all_joints))
```

**Zalety:**
- Mniej overhead'u sieciowego
- Lepsza synchronizacja (wszystkie pomiary z tego samego momentu)
- Wyższa przepustowość

**Wady:**
- Większa latencja dla pojedynczego pomiaru
- Trudniejsze filtrowanie (subskrybent dostaje wszystko)

**Rekomendacja:** Używaj batching dla danych o wysokiej częstotliwości (>100Hz).

### 3. Priority dla krytycznych komend

```python
# Zenoh pozwala ustawić priority dla wiadomości
# Wyższy priorytet = szybsze dostarczenie w przypadku przeciążenia

# Komendy STOP mają najwyższy priorytet
from zenoh import Priority

pub_stop = session.declare_publisher(
    "robot/g1/commands/emergency_stop",
    priority=Priority.REAL_TIME  # Najwyższy priorytet
)

pub_telemetry = session.declare_publisher(
    "robot/g1/state/pose",
    priority=Priority.DATA  # Normalny priorytet
)
```

---

## Dobre praktyki

### 1. Hierarchia kluczy

✅ **Dobrze:**
```python
"robot/g1/sensors/imu/acceleration"
"robot/g1/joints/left_arm/shoulder/pitch"
```

❌ **Źle:**
```python
"imu_accel"  # Za krótko, niespecyficzne
"robot_g1_sensors_imu_acceleration"  # Nie używaj underscores zamiast /
```

### 2. Serializacja danych

**Dla małych danych (<1KB):** JSON
- Czytelny
- Łatwy do debugowania
- Elastyczny

**Dla średnich danych (1-100KB):** MessagePack lub Protocol Buffers
- Szybszy niż JSON
- Mniejszy rozmiar
- Type safety

**Dla dużych danych (>100KB):** Raw binary lub HDF5
- Minimalne overhead
- Maksymalna wydajność

### 3. Error handling

Zawsze obs obsługuj błędy w callback'ach:

```python
def callback(sample: zenoh.Sample):
    try:
        data = json.loads(sample.payload.to_string())
        # Przetwarzanie...
    except json.JSONDecodeError:
        print(f"❌ Błąd parsowania: {sample.key_expr}")
    except Exception as e:
        print(f"❌ Błąd: {e}")
        # Nie pozwól, aby błąd w jednym sample zatrzymał cały subscriber
```

### 4. Graceful shutdown

```python
def main():
    session = None
    try:
        conf = zenoh.Config()
        session = zenoh.open(conf)
        
        # Główna logika...
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Graceful shutdown...")
    finally:
        if session:
            session.close()
        print("✅ Zakończono poprawnie")
```

---

## Debugging i diagnostyka

### 1. Włącz szczegółowe logi

```bash
RUST_LOG=debug python3 robot_telemetry_publisher.py
```

Poziomy: `error` < `warn` < `info` < `debug` < `trace`

### 2. Monitoruj ruch w sieci

```bash
# Terminal 1 - Nasłuchuj wszystko
python3 z_sub.py -k '**'

# Terminal 2 - Twoja aplikacja
python3 robot_telemetry_publisher.py
```

### 3. Sprawdź dostępne węzły

```bash
python3 z_scout.py
```

### 4. Użyj Zenoh Router do logowania

Router może logować cały ruch - przydatne do analiz offline.

---

## Podsumowanie

### Nauczyłeś się:

✅ Dlaczego Zenoh jest idealny dla robotyki humanoidalnej  
✅ Jak zaprojektować hierarchię kluczy dla Unitree G1  
✅ Jak publikować telemetrię robota (Pub/Sub)  
✅ Jak wysyłać komendy sterujące  
✅ Jak używać Query/Queryable dla konfiguracji  
✅ Jak monitorować zdrowie systemu (Liveness)  
✅ Optymalizacje (SHM, batching, priority)  
✅ Dobre praktyki i debugging  

### Następne kroki:

1. 🧪 **Eksperymentuj** - uruchom przykłady, modyfikuj parametry
2. 📊 **Zmierz** - throughput, latencję dla swojego przypadku
3. 🏗️ **Zbuduj** - własną aplikację dla rzeczywistego robota
4. 📚 **Pogłębiaj** - czytaj dokumentację Zenoh i Unitree G1

---

## Zasoby dodatkowe

- **Zenoh documentation:** https://zenoh.io/docs/
- **Zenoh Python API:** https://zenoh-python.readthedocs.io/
- **Unitree G1 documentation:** (dokumentacja producenta)
- **ROS 2 Zenoh bridge:** https://github.com/ros2/zenoh_bridge_ros2 (jeśli używasz ROS 2)

---

**Powodzenia w pracy z robotem Unitree G1! 🤖🚀**
