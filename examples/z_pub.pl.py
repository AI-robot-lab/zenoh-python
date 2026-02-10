#
# Copyright (c) 2022 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#

"""
================================================================================
PRZYKŁAD ZENOH: PUBLISHER (PUBLIKOWANIE DANYCH)
================================================================================

CEL PRZYKŁADU:
    Demonstracja podstawowego wzorca Publisher w protokole Zenoh.
    Publisher to aplikacja, która regularnie publikuje (wysyła) dane
    pod określonym kluczem. Dane te mogą być odbierane przez dowolną
    liczbę Subscriber'ów.

KIEDY UŻYWAĆ PUBLISHER:
    - Publikowanie telemetrii (np. pozycja robota, dane z czujników)
    - Strumieniowanie danych w czasie rzeczywistym
    - Broadcasting informacji do wielu odbiorców jednocześnie
    
KLUCZOWE KONCEPCJE:
    1. Session - połączenie z siecią Zenoh
    2. Publisher - zadeklarowany nadajnik dla konkretnego klucza
    3. Key Expression - hierarchiczny identyfikator danych (np. "robot/sensors/imu")
    4. Put - operacja publikacji danych
    
RÓŻNICA PUBLISHER vs PUT:
    - Publisher: deklarowany raz, używany wielokrotnie (EFEKTYWNE)
    - Put: jednorazowa operacja wysłania (z_put.py)
    
DLA ROBOTA UNITREE G1:
    Użyj tego wzorca do publikowania:
    - Pozycji robota w czasie rzeczywistym
    - Danych z czujników (IMU, enkodery, siły)
    - Stanu systemów (bateria, temperatura)
    
URUCHOMIENIE:
    Terminal 1 (ten program - publikuje):
        python3 z_pub.pl.py -k robot/telemetry -p "Status OK"
    
    Terminal 2 (odbiera dane):
        python3 z_sub.py -k 'robot/**'

PARAMETRY:
    -k, --key       : Klucz, pod którym publikowane są dane
                      (domyślnie: demo/example/zenoh-python-pub)
    -p, --payload   : Treść wiadomości do publikacji
                      (domyślnie: "Pub from Python!")
    --iter          : Liczba iteracji (brak = nieskończoność)
    --interval      : Odstęp czasu między publikacjami w sekundach
    --add-matching-listener : Monitoruj czy są aktywni subscriber'zy

================================================================================
"""

# IMPORT: Moduł time do kontroli odstępów czasowych między publikacjami
import time

# IMPORT: Optional z typing do oznaczenia opcjonalnych parametrów
from typing import Optional

# IMPORT: Główna biblioteka Zenoh - protokół komunikacyjny
import zenoh


def main(
    conf: zenoh.Config,           # Konfiguracja sesji Zenoh
    key: str,                      # Klucz pod którym publikujemy
    payload: str,                  # Bazowa treść wiadomości
    iter: Optional[int],           # Liczba iteracji (None = ∞)
    interval: int,                 # Odstęp między publikacjami [s]
    add_matching_listener: bool,   # Czy monitorować subscriber'ów
):
    """
    Główna funkcja programu Publisher.
    
    PRZEPŁYW PROGRAMU:
        1. Inicjalizacja logowania
        2. Otwarcie sesji Zenoh
        3. Deklaracja Publisher
        4. Pętla publikacji danych
        
    PARAMETRY:
        conf : zenoh.Config
            Konfiguracja Zenoh (endpoint'y, tryb pracy, etc.)
        key : str
            Key expression - identyfikator kanału publikacji
            Przykłady: "robot/pose", "sensors/camera/left"
        payload : str
            Bazowa treść wiadomości. Będzie numerowana: "[0] payload", "[1] payload"...
        iter : Optional[int]
            Liczba publikacji do wykonania. None = nieskończona pętla
        interval : int
            Czas oczekiwania między publikacjami w sekundach
        add_matching_listener : bool
            Jeśli True, program będzie informować o pojawieniu/zniknięciu subscriber'ów
    """
    
    # ============================================================================
    # KROK 1: INICJALIZACJA LOGOWANIA
    # ============================================================================
    # Zenoh używa systemu logowania Rust.
    # Poziomy logów: trace, debug, info, warn, error
    # "error" = tylko błędy (zalecane dla normalnego użycia)
    # Można zmienić przez zmienną środowiskową RUST_LOG, np.: RUST_LOG=debug python3 z_pub.py
    zenoh.init_log_from_env_or("error")

    # ============================================================================
    # KROK 2: OTWARCIE SESJI ZENOH
    # ============================================================================
    # Session to główny obiekt reprezentujący połączenie z siecią Zenoh.
    # 'with' zapewnia automatyczne zamknięcie sesji po wyjściu z bloku (cleanup)
    print("Opening session...")
    print("  → Łączenie z siecią Zenoh...")
    print("  → Tryb: Peer-to-Peer (automatyczne wykrywanie innych węzłów)")
    
    with zenoh.open(conf) as session:
        # W tym momencie sesja jest otwarta i możemy wykonywać operacje
        
        # ========================================================================
        # KROK 3: DEKLARACJA PUBLISHER
        # ========================================================================
        # Publisher to zadeklarowany "nadajnik" dla konkretnego klucza.
        # 
        # DLACZEGO DEKLAROWAĆ PUBLISHER?
        # 1. WYDAJNOŚĆ: Zenoh optymalizuje routing dla zadeklarowanego publishera
        # 2. MATCHING: Zenoh wie, że dane na tym kluczu będą dostępne
        # 3. DISCOVERY: Subscriber'zy mogą wykryć dostępnych publisher'ów
        #
        # ALTERNATYWA: session.put(key, data) - pojedyncze wysłanie bez deklaracji
        print(f"Declaring Publisher on '{key}'...")
        print(f"  → Publisher będzie wysyłać dane pod kluczem: {key}")
        pub = session.declare_publisher(key)

        # ========================================================================
        # OPCJONALNIE: MATCHING LISTENER
        # ========================================================================
        # Matching Listener to callback wywoływany gdy zmienia się liczba
        # subscriber'ów "pasujących" do tego publishera.
        # 
        # ZASTOSOWANIE:
        # - Logowanie informacji o odbiorcach
        # - Optymalizacja (nie wysyłaj jeśli nikt nie słucha)
        # - Diagnostyka sieci
        #
        # UWAGA: W peer-to-peer może być opóźnienie w wykrywaniu
        if add_matching_listener:

            def on_matching_status_update(status: zenoh.MatchingStatus):
                """
                Callback wywoływany gdy zmienia się status dopasowania.
                
                PARAMETRY:
                    status.matching : bool
                        True = jest przynajmniej jeden pasujący subscriber
                        False = brak pasujących subscriber'ów
                """
                if status.matching:
                    print("✅ Publisher has matching subscribers.")
                    print("   → Ktoś odbiera nasze dane!")
                else:
                    print("⚠️  Publisher has NO MORE matching subscribers")
                    print("   → Dane są publikowane, ale nikt nie odbiera")

            # Rejestracja listener'a
            pub.declare_matching_listener(on_matching_status_update)
            print("  → Matching listener aktywny (monitoruje subscriber'ów)")

        # ========================================================================
        # KROK 4: GŁÓWNA PĘTLA PUBLIKACJI
        # ========================================================================
        print("Press CTRL-C to quit...")
        print("=" * 60)
        print("ROZPOCZYNAM PUBLIKACJĘ DANYCH")
        print("=" * 60)
        
        # Pętla:
        # - Jeśli iter=None: nieskończona pętla (itertools.count())
        # - Jeśli iter=N: pętla od 0 do N-1
        for idx in itertools.count() if iter is None else range(iter):
            
            # Czekaj określony interwał przed następną publikacją
            # W prawdziwej aplikacji: synchronizuj z częstotliwością czujnika
            time.sleep(interval)
            
            # --------------------------------------------------------------------
            # PRZYGOTOWANIE DANYCH
            # --------------------------------------------------------------------
            # Formatowanie wiadomości z numerem iteracji
            # Przykład: "[   0] Pub from Python!"
            #           "[   1] Pub from Python!"
            buf = f"[{idx:4d}] {payload}"
            
            # --------------------------------------------------------------------
            # PUBLIKACJA DANYCH
            # --------------------------------------------------------------------
            # pub.put(data) wysyła dane do wszystkich pasujących subscriber'ów
            # 
            # CO SIĘ DZIEJE:
            # 1. Zenoh serializuje dane
            # 2. Znajduje wszystkie pasujące subscriber'y (local + remote)
            # 3. Wysyła dane (multicast jeśli możliwe)
            # 4. Subscriber'zy otrzymują callback z danymi
            print(f"📤 [{idx:4d}] Putting Data ('{key}': '{buf}')...")
            pub.put(buf)
            
            # W tym momencie dane są w sieci Zenoh
            # Subscriber'zy otrzymają je (prawie) natychmiast
        
        # Koniec pętli - zamykanie sesji
        print("\n" + "=" * 60)
        print("PUBLIKACJA ZAKOŃCZONA")
        print("=" * 60)
    
    # Session automatycznie zamknięta dzięki 'with'
    print("✅ Session closed.")


# ================================================================================
# PARSOWANIE ARGUMENTÓW WIERSZA POLECEŃ
# ================================================================================
# Ta sekcja wykonuje się tylko gdy skrypt jest uruchamiany bezpośrednio
# (nie gdy jest importowany jako moduł)
if __name__ == "__main__":
    # IMPORT: argparse do parsowania argumentów CLI
    import argparse
    
    # IMPORT: itertools.count() do nieskończonej pętli
    import itertools

    # IMPORT: moduł common z helper functions dla przykładów
    import common

    # Tworzenie parsera argumentów
    parser = argparse.ArgumentParser(
        prog="z_pub",
        description="zenoh pub example - Przykład publikowania danych w Zenoh"
    )
    
    # Dodanie standardowych argumentów Zenoh (z modułu common)
    # Obejmuje: --mode, --connect, --listen, --config
    common.add_config_arguments(parser)
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --key / -k
    # ----------------------------------------------------------------------------
    # Klucz (key expression) pod którym dane będą publikowane
    # 
    # KEY EXPRESSIONS - DOBRE PRAKTYKI:
    # ✅ Hierarchiczne: "robot/sensors/imu"
    # ✅ Opisowe: "unitree_g1/joints/left_arm/shoulder"
    # ❌ Płaskie: "imu_data"
    # ❌ Z spacjami: "robot state" (użyj _ lub /)
    parser.add_argument(
        "--key",
        "-k",
        dest="key",
        default="demo/example/zenoh-python-pub",
        type=str,
        help="The key expression to publish onto.",
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --payload / -p
    # ----------------------------------------------------------------------------
    # Treść wiadomości do publikacji
    # Może być: string, JSON, binary data (tutaj: string dla prostoty)
    parser.add_argument(
        "--payload",
        "-p",
        dest="payload",
        default="Pub from Python!",
        type=str,
        help="The payload to publish.",
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --iter
    # ----------------------------------------------------------------------------
    # Liczba publikacji do wykonania
    # Brak argumentu = nieskończona pętla
    parser.add_argument(
        "--iter", 
        dest="iter", 
        type=int, 
        help="How many puts to perform (brak = nieskończoność)"
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --interval
    # ----------------------------------------------------------------------------
    # Odstęp czasowy między publikacjami w sekundach
    # Może być float: 0.1 = 100ms, 1.0 = 1s
    parser.add_argument(
        "--interval",
        dest="interval",
        type=float,
        default=1.0,
        help="Interval between each put in seconds",
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --add-matching-listener
    # ----------------------------------------------------------------------------
    # Flaga (brak wartości) - gdy podana, włącza matching listener
    # action="store_true" - obecność flagi ustawia True
    parser.add_argument(
        "--add-matching-listener",
        default=False,
        action="store_true",
        help="Add matching listener (monitoruj subscriber'ów)",
    )

    # Parse argumentów z linii komend
    args = parser.parse_args()
    
    # Utworzenie konfiguracji Zenoh z argumentów
    # common.get_config_from_args() przetwarza --mode, --connect, etc.
    conf = common.get_config_from_args(args)

    # Wywołanie głównej funkcji z rozpakowanymi argumentami
    main(
        conf,
        args.key,
        args.payload,
        args.iter,
        args.interval,
        args.add_matching_listener,
    )

# ================================================================================
# PRZYKŁADY UŻYCIA
# ================================================================================
"""
1. PODSTAWOWE UŻYCIE:
   python3 z_pub.pl.py
   → Publikuje "Pub from Python!" pod kluczem "demo/example/zenoh-python-pub"

2. WŁASNY KLUCZ I PAYLOAD:
   python3 z_pub.pl.py -k robot/status -p "OPERATIONAL"
   → Publikuje własną wiadomość pod własnym kluczem

3. OGRANICZONA LICZBA PUBLIKACJI:
   python3 z_pub.pl.py --iter 10
   → Publikuje tylko 10 razy i kończy

4. SZYBKA PUBLIKACJA:
   python3 z_pub.pl.py --interval 0.1
   → Publikuje co 100ms (10 Hz)

5. Z MATCHING LISTENER:
   python3 z_pub.pl.py --add-matching-listener
   → Informuje gdy pojawi/zniknie subscriber

6. TELEMETRIA ROBOTA (100 Hz):
   python3 z_pub.pl.py -k robot/pose --interval 0.01 -p "x:0,y:0,z:0"
   → Symuluje publikację pozycji robota z częstotliwością 100 Hz

7. POŁĄCZENIE Z ROUTEREM:
   python3 z_pub.pl.py -e tcp/192.168.1.100:7447
   → Łączy się z konkretnym routerem Zenoh
"""

# ================================================================================
# ZADANIA DLA STUDENTÓW
# ================================================================================
"""
ZADANIE 1 - PODSTAWOWE:
    Uruchom ten program i z_sub.py w dwóch terminalach.
    Obserwuj jak dane przepływają z pub do sub.
    
ZADANIE 2 - EKSPERYMENTY Z KLUCZAMI:
    Eksperymentuj z różnymi key expressions:
    - "robot/sensors/temperature"
    - "unitree_g1/joints/left_arm"
    Jak subscriber reaguje na różne wzorce?

ZADANIE 3 - CZĘSTOTLIWOŚĆ:
    Zmień --interval na różne wartości (0.01, 0.1, 1.0, 5.0).
    Jak to wpływa na odbiór danych? Jakie są limity?

ZADANIE 4 - MATCHING:
    Uruchom z --add-matching-listener.
    Zaobserwuj co się dzieje gdy:
    a) Uruchomisz subscriber po publisherze
    b) Zatrzymasz subscriber (CTRL-C)
    
ZADANIE 5 - ROBOT:
    Napisz własny publisher publikujący symulowane dane z robota:
    - Pozycję (x, y, z)
    - Orientację (roll, pitch, yaw)
    - Stan baterii
    Użyj JSON do formatowania danych.

ZADANIE 6 - ZAAWANSOWANE:
    Zmodyfikuj program aby publikował dane z rzeczywistego czujnika
    (np. webcam, GPIO Raspberry Pi, joystick).
"""

# ================================================================================
# CZĘSTO ZADAWANE PYTANIA
# ================================================================================
"""
Q: Czy muszę czekać aż subscriber się podłączy?
A: Nie. Publisher może działać przed subscriber'em. Subscriber otrzyma dane
   od momentu podłączenia. Wcześniejsze dane są tracone (chyba że używasz Storage).

Q: Co jeśli nikt nie odbiera danych?
A: Dane są publikowane niezależnie od odbiorców. Można użyć matching listener
   do optymalizacji (nie publikuj jeśli nikt nie słucha).

Q: Jak wysłać duże dane (np. obraz)?
A: Użyj shared memory (SHM) dla danych >1MB. Wymaga kompilacji z feature SHM.

Q: Jaka jest maksymalna częstotliwość publikacji?
A: Zależy od rozmiaru danych i sieci. Dla małych wiadomości: >1000 Hz możliwe.

Q: Czy mogę mieć wielu publisher'ów na tym samym kluczu?
A: Tak! Subscriber otrzyma dane od wszystkich publisher'ów.
"""
