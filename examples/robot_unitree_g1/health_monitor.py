#!/usr/bin/env python3
"""
================================================================================
PRZYKŁAD: MONITOR ZDROWIA SYSTEMU ROBOTA (HEALTH MONITOR)
================================================================================

CEL:
    Monitorowanie stanu wszystkich modułów robota używając Liveness tokens.
    Wykrywanie awarii i wyświetlanie statusu systemu.

MONITOROWANE MODUŁY:
    - motion_controller  : Kontroler ruchu
    - config_service     : Serwis konfiguracji
    - telemetry          : Publisher telemetrii
    - (inne moduły...)

ZASADA DZIAŁANIA:
    Każdy moduł deklaruje liveness token przy starcie.
    Gdy moduł działa - token jest aktywny.
    Gdy moduł się wyłącza - token znika.
    Monitor obserwuje te zmiany w czasie rzeczywistym.

JAK URUCHOMIĆ:
    Terminal 1 (ten program - monitor):
        python3 health_monitor.py
    
    Terminal 2, 3, 4... (moduły do monitorowania):
        python3 robot_motion_controller.py
        python3 robot_config_service.py
        python3 robot_telemetry_publisher.py
    
    Monitor wyświetli gdy moduły się uruchomią/zatrzymają.

ZADANIA DLA STUDENTÓW:
    1. Uruchom monitor i obserwuj zmiany stanu modułów
    2. Dodaj alarm dla krytycznych modułów
    3. Zapisuj historię do pliku log
    4. Dodaj automatyczny restart przy awarii
    5. Stwórz graficzny dashboard

================================================================================
"""

import time
import zenoh
from datetime import datetime


def main():
    """Główna funkcja monitora zdrowia."""
    
    # ============================================================================
    # KROK 1: INICJALIZACJA
    # ============================================================================
    print("🏥 Uruchamianie monitora zdrowia systemu robota Unitree G1...")
    print("=" * 70)
    
    zenoh.init_log_from_env_or("error")
    conf = zenoh.Config()
    
    with zenoh.open(conf) as session:
        print("📡 Połączono z Zenoh\n")
        
        # ========================================================================
        # STAN MONITOROWANIA
        # ========================================================================
        # Słownik przechowujący aktywne moduły i czas ich uruchomienia
        active_modules = {}
        
        # Lista modułów krytycznych - ich awaria to poważny problem
        critical_modules = {
            "motion_controller",
            "config_service"
        }
        
        # ========================================================================
        # KROK 2: CALLBACK DLA LIVENESS
        # ========================================================================
        def liveness_callback(sample: zenoh.Sample):
            """
            Funkcja wywoływana gdy moduł się uruchomi lub zatrzyma.
            
            Args:
                sample: Sample z informacją o zmianie liveness
            """
            
            # Wyciągnięcie nazwy modułu z klucza
            # Przykład: "robot/g1/health/liveness/motion_controller" → "motion_controller"
            key_parts = str(sample.key_expr).split('/')
            module_name = key_parts[-1] if len(key_parts) > 0 else "unknown"
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # ================================================================
            # MODUŁ URUCHOMIONY (PUT)
            # ================================================================
            if sample.kind == zenoh.SampleKind.PUT:
                # Moduł się uruchomił
                active_modules[module_name] = time.time()
                
                # Sprawdź czy to moduł krytyczny
                is_critical = module_name in critical_modules
                critical_marker = "🔴 KRYTYCZNY" if is_critical else ""
                
                print(f"\n[{current_time}] ✅ Moduł ONLINE: {module_name} {critical_marker}")
                print(f"   → Moduł aktywny i gotowy do pracy")
                
            # ================================================================
            # MODUŁ ZATRZYMANY (DELETE)
            # ================================================================
            else:  # DELETE
                # Moduł się zatrzymał
                if module_name in active_modules:
                    uptime = time.time() - active_modules[module_name]
                    del active_modules[module_name]
                    
                    # Sprawdź czy to moduł krytyczny
                    is_critical = module_name in critical_modules
                    
                    if is_critical:
                        print(f"\n[{current_time}] 🔴 ALARM! Moduł KRYTYCZNY OFFLINE: {module_name}")
                        print(f"   ⚠️  WYMAGANA INTERWENCJA!")
                    else:
                        print(f"\n[{current_time}] ❌ Moduł OFFLINE: {module_name}")
                    
                    print(f"   → Czas działania: {uptime:.1f} sekund")
            
            # ================================================================
            # WYŚWIETLENIE AKTUALNEGO STATUSU
            # ================================================================
            print(f"\n   📊 Status systemu:")
            print(f"   Aktywne moduły: {len(active_modules)}")
            
            if active_modules:
                print(f"   Lista aktywnych:")
                for mod in sorted(active_modules.keys()):
                    uptime = time.time() - active_modules[mod]
                    critical = " [KRYTYCZNY]" if mod in critical_modules else ""
                    print(f"      • {mod}{critical} - uptime: {uptime:.0f}s")
            else:
                print(f"   ⚠️  BRAK AKTYWNYCH MODUŁÓW!")
            
            print()
        
        # ========================================================================
        # KROK 3: SUBSKRYPCJA LIVENESS TOKENS
        # ========================================================================
        # Nasłuchujemy wszystkich tokenów pod robot/g1/health/liveness/
        print("🎧 Subskrybowanie liveness tokens...")
        print("   → Monitoruję: robot/g1/health/liveness/**")
        
        session.liveliness().declare_subscriber(
            "robot/g1/health/liveness/**",
            liveness_callback
        )
        
        print("\n✅ Monitor zdrowia gotowy!")
        print("⏹️  Naciśnij CTRL-C aby zatrzymać...")
        print("=" * 70)
        print()
        
        # ========================================================================
        # KROK 4: OKRESOWE SPRAWDZANIE STANU
        # ========================================================================
        # Co 10 sekund wyświetl podsumowanie
        
        check_interval = 10  # sekund
        last_check = time.time()
        
        try:
            while True:
                time.sleep(1)
                
                current_time = time.time()
                
                # Co 10 sekund: wyświetl podsumowanie
                if current_time - last_check >= check_interval:
                    last_check = current_time
                    
                    print("\n" + "=" * 70)
                    print(f"RAPORT OKRESOWY - {datetime.now().strftime('%H:%M:%S')}")
                    print("=" * 70)
                    
                    if len(active_modules) == 0:
                        print("⚠️  UWAGA: Brak aktywnych modułów!")
                        print("   System robota może nie działać poprawnie.")
                    else:
                        print(f"💚 System działa: {len(active_modules)} modułów aktywnych")
                        
                        # Sprawdź moduły krytyczne
                        missing_critical = critical_modules - set(active_modules.keys())
                        if missing_critical:
                            print(f"\n🔴 BRAKUJĄCE MODUŁY KRYTYCZNE:")
                            for mod in missing_critical:
                                print(f"   • {mod}")
                        else:
                            print(f"✅ Wszystkie moduły krytyczne działają")
                        
                        # Wyświetl uptime każdego modułu
                        print(f"\n📈 Uptime modułów:")
                        for mod, start_time in sorted(active_modules.items()):
                            uptime = current_time - start_time
                            hours = int(uptime // 3600)
                            minutes = int((uptime % 3600) // 60)
                            seconds = int(uptime % 60)
                            
                            critical = " [KRYTYCZNY]" if mod in critical_modules else ""
                            print(f"   • {mod}{critical}: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    
                    print("=" * 70)
                    print()
                    
        except KeyboardInterrupt:
            print("\n⏹️  Zatrzymywanie monitora zdrowia...")
    
    print("✅ Monitor zakończony.")


if __name__ == "__main__":
    main()
