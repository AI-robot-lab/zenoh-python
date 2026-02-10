#!/usr/bin/env python3
"""
================================================================================
PRZYKŁAD: PUBLIKOWANIE TELEMETRII ROBOTA UNITREE G1
================================================================================

CEL:
    Symuluje publikowanie telemetrii robota Unitree G1 w czasie rzeczywistym.
    W prawdziwej aplikacji dane pochodziłyby z rzeczywistych czujników robota.

PUBLIKOWANE DANE:
    - robot/g1/state/pose         : Pozycja i orientacja (x, y, z, heading)
    - robot/g1/state/battery      : Poziom baterii (%)
    - robot/g1/sensors/imu/orientation : Orientacja z IMU (roll, pitch, yaw)

CZĘSTOTLIWOŚĆ:
    10 Hz (co 100ms) - typowa dla telemetrii robota mobilnego

JAK URUCHOMIĆ:
    Terminal 1 (ten program - robot):
        python3 robot_telemetry_publisher.py
    
    Terminal 2 (monitoring - stacja operatorska):
        python3 ../z_sub.py -k 'robot/g1/**'
    
    Terminal 3 (tylko pozycja):
        python3 ../z_sub.py -k 'robot/g1/state/pose'

ZADANIA DLA STUDENTÓW:
    1. Uruchom program i obserwuj publikowane dane
    2. Zmień częstotliwość publikacji (--interval)
    3. Dodaj publikowanie nowych danych (np. temperatura)
    4. Zintegruj z rzeczywistymi czujnikami (jeśli dostępne)

================================================================================
"""

import time
import json
import math
import argparse
import zenoh


def main(interval: float):
    """
    Główna funkcja publikatora telemetrii.
    
    Args:
        interval: Odstęp między publikacjami w sekundach (domyślnie 0.1 = 10 Hz)
    """
    
    # ============================================================================
    # KROK 1: INICJALIZACJA ZENOH
    # ============================================================================
    print("🤖 Uruchamianie modułu telemetrii robota Unitree G1...")
    zenoh.init_log_from_env_or("error")
    
    # Konfiguracja Zenoh - używamy domyślnych ustawień (peer mode)
    conf = zenoh.Config()
    
    print("📡 Otwieranie sesji Zenoh...")
    with zenoh.open(conf) as session:
        
        # ========================================================================
        # KROK 2: DEKLARACJA PUBLISHER'ÓW
        # ========================================================================
        # Deklarujemy osobne publisher'y dla różnych typów danych
        # Zwiększa to wydajność i pozwala na selektywną subskrypcję
        
        print("📢 Deklarowanie publisher'ów...")
        pub_pose = session.declare_publisher("robot/g1/state/pose")
        pub_battery = session.declare_publisher("robot/g1/state/battery")
        pub_imu = session.declare_publisher("robot/g1/sensors/imu/orientation")
        
        print("✅ Robot gotowy do publikowania danych!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # ========================================================================
        # KROK 3: SYMULACJA DANYCH POCZĄTKOWYCH
        # ========================================================================
        # W prawdziwej aplikacji: odczyt z rzeczywistych czujników
        x, y, z = 0.0, 0.0, 0.0  # Pozycja w metrach [m]
        heading = 0.0             # Kierunek w radianach [rad]
        battery_level = 100.0     # Procent baterii [%]
        
        try:
            idx = 0
            start_time = time.time()
            
            # ====================================================================
            # KROK 4: GŁÓWNA PĘTLA PUBLIKACJI
            # ====================================================================
            while True:
                idx += 1
                current_time = time.time()
                elapsed = current_time - start_time
                
                # ================================================================
                # SYMULACJA RUCHU ROBOTA
                # ================================================================
                # Robot porusza się w okręgu o promieniu 2m
                # W prawdziwej aplikacji: odczyt z enkoderów kół lub odometrii
                
                radius = 2.0           # Promień okręgu [m]
                angular_speed = 0.2    # Prędkość kątowa [rad/s]
                
                # Pozycja na okręgu
                x = radius * math.cos(angular_speed * elapsed)
                y = radius * math.sin(angular_speed * elapsed)
                z = 0.0  # Robot na ziemi
                
                # Kierunek ruchu (tangent do okręgu)
                heading = (angular_speed * elapsed + math.pi/2) % (2 * math.pi)
                
                # Symulacja rozładowania baterii (0.1% na sekundę)
                battery_level = max(0, 100 - elapsed * 0.1)
                
                # ================================================================
                # PRZYGOTOWANIE DANYCH DO PUBLIKACJI
                # ================================================================
                # Używamy JSON dla czytelności
                # W systemach wymagających wysokiej wydajności: Protocol Buffers, MessagePack
                
                # Dane pozycji (pose)
                pose_data = {
                    "x": round(x, 3),        # Pozycja X [m]
                    "y": round(y, 3),        # Pozycja Y [m]
                    "z": round(z, 3),        # Pozycja Z [m]
                    "heading": round(heading, 3),  # Kierunek [rad]
                    "timestamp": current_time      # Timestamp [s]
                }
                
                # Dane IMU (orientacja jako kąty Eulera)
                # Roll - przechył na boki, Pitch - przechył przód-tył, Yaw - obrót
                imu_data = {
                    "roll": 0.0,    # [rad] - robot stabilny, brak przechyłu
                    "pitch": 0.0,   # [rad] - robot stabilny, brak przechyłu
                    "yaw": round(heading, 3),  # [rad] - zgodne z kierunkiem ruchu
                    "timestamp": current_time
                }
                
                # ================================================================
                # PUBLIKACJA DANYCH
                # ================================================================
                # Konwersja do JSON i publikacja
                
                pub_pose.put(json.dumps(pose_data))
                pub_battery.put(str(battery_level))
                pub_imu.put(json.dumps(imu_data))
                
                # ================================================================
                # WYŚWIETLENIE INFORMACJI (co 10 iteracji = co 1s przy 10Hz)
                # ================================================================
                if idx % 10 == 0:
                    print(f"[{idx:4d}] 📍 Pozycja: ({x:6.2f}, {y:6.2f})  "
                          f"🧭 Kierunek: {math.degrees(heading):6.1f}°  "
                          f"🔋 Bateria: {battery_level:5.1f}%")
                
                # Czekaj przed następną iteracją
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie publikatora telemetrii...")
    
    print("✅ Moduł telemetrii zakończony.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Publikator telemetrii robota Unitree G1"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.1,
        help="Odstęp między publikacjami w sekundach (domyślnie 0.1 = 10 Hz)"
    )
    
    args = parser.parse_args()
    main(args.interval)
