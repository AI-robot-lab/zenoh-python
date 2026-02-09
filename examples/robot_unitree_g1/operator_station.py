#!/usr/bin/env python3
"""
================================================================================
PRZYKŁAD: STACJA OPERATORSKA - WYSYŁANIE KOMEND DO ROBOTA
================================================================================

CEL:
    Interaktywna aplikacja pozwalająca operatorowi wysyłać komendy do robota.
    Symuluje panel sterowania robotem Unitree G1.

DOSTĘPNE KOMENDY:
    1. Chód do przodu (vx=0.5 m/s)
    2. Chód do tyłu (vx=-0.5 m/s)
    3. Obrót w lewo (omega=0.3 rad/s)
    4. Obrót w prawo (omega=-0.3 rad/s)
    5. Stop (zatrzymanie)
    6. Ruch do pozycji (x=2, y=3)

JAK URUCHOMIĆ:
    Terminal 1 (kontroler robota - musi działać!):
        python3 robot_motion_controller.py
    
    Terminal 2 (ta aplikacja - stacja operatorska):
        python3 operator_station.py
    
    Następnie wybierz komendy z menu.

ZADANIA DLA STUDENTÓW:
    1. Uruchom stację i wyślij różne komendy
    2. Obserwuj reakcję kontrolera
    3. Dodaj nowe komendy (np. chód w bok)
    4. Zaimplementuj joystick control
    5. Dodaj wizualizację pozycji robota

================================================================================
"""

import json
import zenoh


def main():
    """Główna funkcja stacji operatorskiej."""
    
    # ============================================================================
    # KROK 1: INICJALIZACJA ZENOH
    # ============================================================================
    print("🖥️  Stacja operatorska robota Unitree G1")
    print("=" * 60)
    
    zenoh.init_log_from_env_or("error")
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("✅ Połączono z Zenoh\n")
        
        # ========================================================================
        # KROK 2: GŁÓWNA PĘTLA MENU
        # ========================================================================
        while True:
            # ================================================================
            # WYŚWIETLENIE MENU
            # ================================================================
            print("\n" + "=" * 60)
            print("MENU KOMEND:")
            print("=" * 60)
            print("  1 - 🚶 Chód do przodu (0.5 m/s)")
            print("  2 - 🔙 Chód do tyłu (0.5 m/s)")
            print("  3 - ↺  Obrót w lewo (0.3 rad/s)")
            print("  4 - ↻  Obrót w prawo (0.3 rad/s)")
            print("  5 - 🛑 STOP - zatrzymanie")
            print("  6 - 🎯 Ruch do pozycji (2, 3)")
            print("  7 - 🚀 Szybki chód (1.0 m/s)")
            print("  8 - 🐌 Wolny chód (0.2 m/s)")
            print("  q - ❌ Wyjście")
            print("=" * 60)
            
            choice = input("\n➤ Wybierz komendę: ").strip()
            
            if choice == 'q' or choice == 'Q':
                print("👋 Zamykanie stacji operatorskiej...")
                break
            
            # ================================================================
            # PRZYGOTOWANIE KOMENDY
            # ================================================================
            key = None      # Klucz Zenoh dla komendy
            payload = None  # Dane komendy (JSON)
            
            if choice == '1':
                # Chód do przodu
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": 0.5,   # Prędkość do przodu [m/s]
                    "vy": 0.0,   # Brak ruchu w bok
                    "omega": 0.0 # Brak obrotu
                })
                
            elif choice == '2':
                # Chód do tyłu
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": -0.5,  # Prędkość do tyłu [m/s]
                    "vy": 0.0,
                    "omega": 0.0
                })
                
            elif choice == '3':
                # Obrót w lewo
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": 0.0,
                    "vy": 0.0,
                    "omega": 0.3  # Obrót w lewo [rad/s]
                })
                
            elif choice == '4':
                # Obrót w prawo
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": 0.0,
                    "vy": 0.0,
                    "omega": -0.3  # Obrót w prawo [rad/s]
                })
                
            elif choice == '5':
                # Stop
                key = "robot/g1/commands/motion/stop"
                payload = json.dumps({})
                
            elif choice == '6':
                # Ruch do pozycji
                key = "robot/g1/commands/motion/pose"
                payload = json.dumps({
                    "x": 2.0,       # Docelowa pozycja X [m]
                    "y": 3.0,       # Docelowa pozycja Y [m]
                    "heading": 0.0  # Docelowa orientacja [rad]
                })
                
            elif choice == '7':
                # Szybki chód
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": 1.0,   # Szybka prędkość
                    "vy": 0.0,
                    "omega": 0.0
                })
                
            elif choice == '8':
                # Wolny chód
                key = "robot/g1/commands/motion/walk"
                payload = json.dumps({
                    "vx": 0.2,   # Wolna prędkość
                    "vy": 0.0,
                    "omega": 0.0
                })
                
            else:
                print("❌ Nieprawidłowy wybór! Spróbuj ponownie.")
                continue
            
            # ================================================================
            # WYSŁANIE KOMENDY
            # ================================================================
            print(f"\n📤 Wysyłanie komendy...")
            print(f"   Klucz: {key}")
            print(f"   Dane:  {payload}")
            
            session.put(key, payload)
            
            print("✅ Komenda wysłana!")
            print("   ℹ️  Sprawdź terminal kontrolera aby zobaczyć reakcję")
    
    print("\n👋 Do widzenia!")


if __name__ == "__main__":
    main()
