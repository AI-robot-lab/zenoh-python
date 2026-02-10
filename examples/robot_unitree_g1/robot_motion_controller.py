#!/usr/bin/env python3
"""
================================================================================
PRZYKŁAD: KONTROLER RUCHU ROBOTA UNITREE G1
================================================================================

CEL:
    Odbiera komendy ruchu i symuluje ich wykonanie.
    W prawdziwej aplikacji wysyłałby komendy do kontrolera niskiego poziomu.

ODBIERANE KOMENDY:
    - robot/g1/commands/motion/walk  : Komenda chodu (vx, vy, omega)
    - robot/g1/commands/motion/stop  : Zatrzymanie robota
    - robot/g1/commands/motion/pose  : Ruch do docelowej pozycji (x, y, heading)

FORMAT KOMEND (JSON):
    Walk:  {"vx": 0.5, "vy": 0.0, "omega": 0.0}
    Stop:  {}
    Pose:  {"x": 2.0, "y": 3.0, "heading": 0.0}

JAK URUCHOMIĆ:
    Terminal 1 (ten program - kontroler robota):
        python3 robot_motion_controller.py
    
    Terminal 2 (wysyłanie komend - stacja operatorska):
        python3 operator_station.py
    
    LUB ręcznie:
        python3 ../z_put.py -k robot/g1/commands/motion/walk -p '{"vx":0.5,"vy":0,"omega":0}'

ZADANIA DLA STUDENTÓW:
    1. Uruchom kontroler i wyślij różne komendy
    2. Obserwuj monitoring przez liveness token
    3. Dodaj nowe typy komend (np. sit, stand)
    4. Zintegruj z prawdziwym kontrolerem robota

================================================================================
"""

import time
import json
import zenoh


def main():
    """Główna funkcja kontrolera ruchu."""
    
    # ============================================================================
    # KROK 1: INICJALIZACJA ZENOH
    # ============================================================================
    print("🎮 Uruchamianie kontrolera ruchu robota Unitree G1...")
    zenoh.init_log_from_env_or("error")
    
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("📡 Połączono z Zenoh")
        
        # ========================================================================
        # KROK 2: DEFINICJA CALLBACK DLA KOMEND RUCHU
        # ========================================================================
        def motion_callback(sample: zenoh.Sample):
            """
            Funkcja wywoływana przy otrzymaniu komendy ruchu.
            
            Args:
                sample: Otrzymany sample z Zenoh zawierający komendę
            """
            
            # Konwersja payload (bytes) na string
            command = sample.payload.to_string()
            
            print(f"\n📨 Otrzymano komendę: {sample.key_expr}")
            print(f"   Payload: {command}")
            
            try:
                # Parsowanie JSON
                data = json.loads(command)
                
                # ============================================================
                # PRZETWARZANIE RÓŻNYCH TYPÓW KOMEND
                # ============================================================
                
                if "walk" in str(sample.key_expr):
                    # --------------------------------------------------------
                    # KOMENDA CHODU
                    # --------------------------------------------------------
                    # vx - prędkość do przodu/tyłu [m/s]
                    # vy - prędkość w bok (lewo/prawo) [m/s]
                    # omega - prędkość obrotowa [rad/s]
                    
                    vx = data.get("vx", 0.0)
                    vy = data.get("vy", 0.0)
                    omega = data.get("omega", 0.0)
                    
                    print(f"   🚶 Wykonuję chód:")
                    print(f"      vx (przód/tył): {vx:+.2f} m/s")
                    print(f"      vy (bok):       {vy:+.2f} m/s")
                    print(f"      omega (obrót):  {omega:+.2f} rad/s")
                    
                    # TU: Wysłanie do low-level controller
                    # W prawdziwej aplikacji:
                    # robot_controller.send_velocity_command(vx, vy, omega)
                    
                elif "stop" in str(sample.key_expr):
                    # --------------------------------------------------------
                    # KOMENDA STOP
                    # --------------------------------------------------------
                    print(f"   🛑 ZATRZYMUJĘ ROBOTA!")
                    
                    # TU: Wysłanie komendy stop
                    # robot_controller.send_velocity_command(0, 0, 0)
                    # robot_controller.emergency_stop()
                    
                elif "pose" in str(sample.key_expr):
                    # --------------------------------------------------------
                    # KOMENDA RUCHU DO POZYCJI DOCELOWEJ
                    # --------------------------------------------------------
                    x = data.get("x", 0.0)
                    y = data.get("y", 0.0)
                    heading = data.get("heading", 0.0)
                    
                    print(f"   🎯 Ruch do pozycji:")
                    print(f"      x:       {x:.2f} m")
                    print(f"      y:       {y:.2f} m")
                    print(f"      heading: {heading:.2f} rad")
                    
                    # TU: Planowanie i wykonanie trajektorii
                    # trajectory = plan_motion_to_goal(x, y, heading)
                    # robot_controller.execute_trajectory(trajectory)
                
                else:
                    print(f"   ⚠️  Nieznany typ komendy: {sample.key_expr}")
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Błąd parsowania JSON: {e}")
                print(f"   Otrzymano: {command}")
            except Exception as e:
                print(f"   ❌ Błąd wykonania: {e}")
        
        # ========================================================================
        # KROK 3: SUBSKRYPCJA KOMEND RUCHU
        # ========================================================================
        # Dopasowanie wszystkich komend pod robot/g1/commands/motion/
        print("🎧 Subskrybowanie komend ruchu...")
        subscriber = session.declare_subscriber(
            "robot/g1/commands/motion/**",
            motion_callback
        )
        
        print("✅ Kontroler gotowy do przyjmowania komend!")
        
        # ========================================================================
        # KROK 4: LIVENESS TOKEN - HEALTH MONITORING
        # ========================================================================
        # Token sygnalizujący że moduł działa
        # Jeśli proces umrze, token automatycznie znika
        # Monitorowanie: python3 ../z_get_liveliness.py -k 'robot/g1/health/**'
        
        liveness_token = session.liveliness().declare_token(
            "robot/g1/health/liveness/motion_controller"
        )
        print("💚 Liveness token aktywny - moduł jest monitorowany")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...\n")
        
        # ========================================================================
        # KROK 5: UTRZYMYWANIE PROGRAMU W DZIAŁANIU
        # ========================================================================
        try:
            while True:
                time.sleep(1)
                # Callback motion_callback jest wywoływany automatycznie w tle
                
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie kontrolera...")
    
    print("✅ Kontroler zakończony.")
    print("💀 Liveness token usunięty - moduł nieaktywny")


if __name__ == "__main__":
    main()
