#!/usr/bin/env python3
"""
================================================================================
PRZYKŁAD: SERWIS KONFIGURACJI ROBOTA (QUERYABLE)
================================================================================

CEL:
    Implementacja serwisu odpowiadającego na zapytania o konfigurację robota.
    Demonstracja wzorca Query/Queryable dla dostępu do konfiguracji.

DOSTĘPNE KONFIGURACJE:
    - robot/g1/config/pid_gains     : Wzmocnienia PID dla różnych stawów
    - robot/g1/config/joint_limits  : Limity pozycji stawów
    - robot/g1/config/max_velocity  : Maksymalne prędkości

FORMAT ODPOWIEDZI:
    JSON z odpowiednimi danymi konfiguracyjnymi

JAK URUCHOMIĆ:
    Terminal 1 (ten program - serwis konfiguracji):
        python3 robot_config_service.py
    
    Terminal 2 (zapytania):
        # Cała konfiguracja
        python3 ../z_get.py -s 'robot/g1/config/**'
        
        # Tylko PID gains
        python3 ../z_get.py -s 'robot/g1/config/pid_gains'
        
        # Tylko limity stawów
        python3 ../z_get.py -s 'robot/g1/config/joint_limits'

ZADANIA DLA STUDENTÓW:
    1. Uruchom serwis i wykonaj różne zapytania
    2. Dodaj nowe parametry konfiguracyjne
    3. Zaimplementuj możliwość modyfikacji konfiguracji
    4. Dodaj persystencję (zapis do pliku)

================================================================================
"""

import json
import zenoh
import time


# ================================================================================
# SYMULOWANA KONFIGURACJA ROBOTA
# ================================================================================
# W prawdziwej aplikacji: ładowana z pliku, bazy danych lub EEPROM robota
CONFIG = {
    "pid_gains": {
        "description": "Wzmocnienia regulatorów PID dla różnych grup stawów",
        "left_arm": {
            "p": 10.0,   # Wzmocnienie proporcjonalne
            "i": 0.5,    # Wzmocnienie całkujące
            "d": 2.0     # Wzmocnienie różniczkujące
        },
        "right_arm": {
            "p": 10.0,
            "i": 0.5,
            "d": 2.0
        },
        "left_leg": {
            "p": 15.0,   # Większe wzmocnienie dla nóg (większa masa)
            "i": 1.0,
            "d": 3.0
        },
        "right_leg": {
            "p": 15.0,
            "i": 1.0,
            "d": 3.0
        },
        "torso": {
            "p": 12.0,
            "i": 0.8,
            "d": 2.5
        }
    },
    "joint_limits": {
        "description": "Limity pozycji stawów w stopniach",
        "shoulder_pitch": {"min": -90, "max": 180},
        "shoulder_roll": {"min": -45, "max": 180},
        "shoulder_yaw": {"min": -90, "max": 90},
        "elbow": {"min": 0, "max": 150},
        "wrist_pitch": {"min": -90, "max": 90},
        "wrist_roll": {"min": -180, "max": 180},
        "hip_pitch": {"min": -120, "max": 60},
        "hip_roll": {"min": -45, "max": 45},
        "hip_yaw": {"min": -45, "max": 45},
        "knee": {"min": 0, "max": 150},
        "ankle_pitch": {"min": -45, "max": 45},
        "ankle_roll": {"min": -30, "max": 30}
    },
    "max_velocity": {
        "description": "Maksymalne prędkości ruchu",
        "linear": 1.5,      # Prędkość liniowa [m/s]
        "angular": 1.0,     # Prędkość kątowa [rad/s]
        "joint": {
            "shoulder": 3.0,  # Prędkość stawów ramion [rad/s]
            "elbow": 2.5,
            "hip": 2.0,       # Prędkość stawów nóg [rad/s]
            "knee": 3.0,
            "ankle": 2.0
        }
    },
    "safety": {
        "description": "Parametry bezpieczeństwa",
        "emergency_stop_decel": 5.0,  # Opóźnienie przy emergency stop [m/s²]
        "max_tilt_angle": 30.0,        # Maksymalny kąt przechyłu [°]
        "battery_critical_level": 10.0,  # Krytyczny poziom baterii [%]
        "temperature_limit": 80.0      # Maksymalna temperatura [°C]
    }
}


def main():
    """Główna funkcja serwisu konfiguracji."""
    
    # ============================================================================
    # KROK 1: INICJALIZACJA ZENOH
    # ============================================================================
    print("⚙️  Uruchamianie serwisu konfiguracji robota Unitree G1...")
    zenoh.init_log_from_env_or("error")
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("📡 Połączono z Zenoh")
        
        # ========================================================================
        # KROK 2: DEFINICJA QUERYABLE CALLBACK
        # ========================================================================
        def config_queryable(query: zenoh.Query):
            """
            Funkcja wywoływana gdy ktoś wysyła zapytanie o konfigurację.
            
            Args:
                query: Obiekt zapytania z Zenoh
            """
            
            selector = str(query.selector)
            print(f"\n📨 Otrzymano zapytanie: {selector}")
            
            try:
                # ============================================================
                # PARSOWANIE ZAPYTANIA I PRZYGOTOWANIE ODPOWIEDZI
                # ============================================================
                
                if "pid_gains" in selector:
                    # Zapytanie o PID gains
                    response = CONFIG["pid_gains"]
                    print(f"   📤 Odpowiadam: PID gains")
                    
                elif "joint_limits" in selector:
                    # Zapytanie o limity stawów
                    response = CONFIG["joint_limits"]
                    print(f"   📤 Odpowiadam: Joint limits")
                    
                elif "max_velocity" in selector:
                    # Zapytanie o maksymalne prędkości
                    response = CONFIG["max_velocity"]
                    print(f"   📤 Odpowiadam: Max velocity")
                    
                elif "safety" in selector:
                    # Zapytanie o parametry bezpieczeństwa
                    response = CONFIG["safety"]
                    print(f"   📤 Odpowiadam: Safety parameters")
                    
                elif selector.endswith("config/**") or selector.endswith("config"):
                    # Zapytanie o całą konfigurację
                    response = CONFIG
                    print(f"   📤 Odpowiadam: Pełna konfiguracja")
                    
                else:
                    # Nieznane zapytanie
                    error_msg = {
                        "error": "Unknown configuration key",
                        "requested": selector,
                        "available": list(CONFIG.keys())
                    }
                    print(f"   ❌ Nieznany klucz konfiguracji")
                    # Użyj prostego klucza (nie selector z parametrami) dla błędu
                    query.reply_err("robot/g1/config", json.dumps(error_msg, indent=2))
                    return
                
                # ============================================================
                # WYSŁANIE ODPOWIEDZI
                # ============================================================
                # Formatowanie JSON z wcięciami dla czytelności
                response_json = json.dumps(response, indent=2)
                
                query.reply(selector, response_json)
                
                # Wyświetl rozmiar odpowiedzi
                print(f"   ℹ️  Rozmiar odpowiedzi: {len(response_json)} bajtów")
                
            except Exception as e:
                print(f"   ❌ Błąd przetwarzania zapytania: {e}")
                # Wysłanie błędu jako odpowiedzi
                error_payload = json.dumps({
                    "error": str(e),
                    "type": type(e).__name__
                })
                query.reply_err(selector, error_payload)
        
        # ========================================================================
        # KROK 3: DEKLARACJA QUERYABLE
        # ========================================================================
        # Odpowiadamy na wszystkie zapytania pod robot/g1/config/
        print("🎧 Deklarowanie queryable dla konfiguracji...")
        queryable = session.declare_queryable(
            "robot/g1/config/**",
            config_queryable
        )
        
        print("✅ Serwis konfiguracji gotowy!")
        
        # ========================================================================
        # KROK 4: LIVENESS TOKEN
        # ========================================================================
        liveness_token = session.liveliness().declare_token(
            "robot/g1/health/liveness/config_service"
        )
        print("💚 Liveness token aktywny")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # Wyświetl dostępne klucze konfiguracji
        print("📋 Dostępne klucze konfiguracji:")
        for key in CONFIG.keys():
            print(f"   - robot/g1/config/{key}")
        print()
        
        # ========================================================================
        # KROK 5: UTRZYMYWANIE PROGRAMU W DZIAŁANIU
        # ========================================================================
        try:
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie serwisu konfiguracji...")
    
    print("✅ Serwis zakończony.")


if __name__ == "__main__":
    main()
