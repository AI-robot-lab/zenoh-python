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
PRZYKŁAD ZENOH: SUBSCRIBER (SUBSKRYBOWANIE DANYCH)
================================================================================

CEL PRZYKŁADU:
    Demonstracja podstawowego wzorca Subscriber w protokole Zenoh.
    Subscriber to aplikacja, która nasłuchuje (subskrybuje) danych
    publikowanych pod określonym kluczem lub grupą kluczy.

KIEDY UŻYWAĆ SUBSCRIBER:
    - Odbieranie telemetrii w czasie rzeczywistym
    - Monitoring zdarzeń w systemie
    - Reagowanie na zmiany stanu
    - Zbieranie danych z wielu źródeł
    
KLUCZOWE KONCEPCJE:
    1. Subscriber - nasłuchiwacz danych na określonym kluczu
    2. Key Expression - wzorzec określający jakie klucze nas interesują
    3. Callback - funkcja wywoływana automatycznie przy otrzymaniu danych
    4. Sample - otrzymane dane zawierające klucz, payload, timestamp, etc.
    
WILDCARD'Y W KEY EXPRESSIONS:
    - *   : Jeden poziom (np. "robot/*/temperature" = robot/arm/temperature, robot/leg/temperature)
    - **  : Wiele poziomów (np. "robot/**" = wszystko pod robot/)
    
DLA ROBOTA UNITREE G1:
    Użyj tego wzorca do odbierania:
    - Telemetrii: pozycja, orientacja, prędkość
    - Danych czujników: IMU, kamery, enkodery
    - Komend: od operatora lub systemu planowania
    
URUCHOMIENIE:
    Terminal 1 (ten program - odbiera):
        python3 z_sub.pl.py -k 'robot/**'
    
    Terminal 2 (publikuje dane):
        python3 z_pub.py -k robot/status -p "OK"

PARAMETRY:
    -k, --key : Key expression określające jakie dane odbierać
                (domyślnie: "demo/example/**" - wszystko z demo/example/)

================================================================================
"""

# IMPORT: Moduł time do utrzymania programu w działaniu
import time

# IMPORT: Główna biblioteka Zenoh
import zenoh


def main(conf: zenoh.Config, key: str):
    """
    Główna funkcja programu Subscriber.
    
    PRZEPŁYW PROGRAMU:
        1. Inicjalizacja logowania
        2. Otwarcie sesji Zenoh
        3. Deklaracja Subscriber z callback'iem
        4. Nieskończona pętla oczekiwania na dane
        
    PARAMETRY:
        conf : zenoh.Config
            Konfiguracja Zenoh (endpoint'y, tryb pracy, etc.)
        key : str
            Key expression - wzorzec kluczy do subskrypcji
            Przykłady: 
                - "robot/pose" - tylko ten konkretny klucz
                - "robot/*" - wszystko bezpośrednio pod robot/
                - "robot/**" - wszystko pod robot/ rekurencyjnie
    """
    
    # ============================================================================
    # KROK 1: INICJALIZACJA LOGOWANIA
    # ============================================================================
    # Ustawienie poziomu logów na "error" (tylko błędy)
    # Można zmienić przez zmienną środowiskową: RUST_LOG=debug python3 z_sub.py
    zenoh.init_log_from_env_or("error")

    # ============================================================================
    # KROK 2: OTWARCIE SESJI ZENOH
    # ============================================================================
    # Session to połączenie z siecią Zenoh
    # 'with' zapewnia automatyczne zamknięcie po zakończeniu
    print("Opening session...")
    print("  → Łączenie z siecią Zenoh...")
    print("  → Rozpoczynam wykrywanie innych węzłów (scouting)...")
    
    with zenoh.open(conf) as session:
        # Sesja otwarta - możemy deklarować subscriber'y
        
        print(f"Declaring Subscriber on '{key}'...")
        print(f"  → Będę odbierać dane pasujące do klucza: {key}")

        # ========================================================================
        # KROK 3: DEFINICJA CALLBACK FUNCTION
        # ========================================================================
        # Callback to funkcja wywoływana automatycznie za każdym razem gdy
        # otrzymamy dane pasujące do naszego key expression.
        # 
        # WAŻNE: Callback jest wywoływany w wątku Zenoh!
        # - Unikaj długich operacji (blokują odbiór kolejnych danych)
        # - Dla czasochłonnych zadań użyj kolejki (queue) lub wątków
        def listener(sample: zenoh.Sample):
            """
            Funkcja callback wywoływana przy otrzymaniu danych.
            
            PARAMETRY:
                sample : zenoh.Sample
                    Obiekt zawierający otrzymane dane i metadane
                    
            POLA SAMPLE:
                - sample.key_expr : Key expression danych (str)
                - sample.payload : Dane (zenoh.Bytes)
                - sample.kind : Typ sample (PUT, DELETE)
                - sample.timestamp : Timestamp (opcjonalny)
                - sample.encoding : Encoding danych
                
            KONWERSJA PAYLOAD:
                - sample.payload.to_string() : do string (UTF-8)
                - sample.payload.to_bytes() : do raw bytes
                - sample.payload.deserialize(T) : do konkretnego typu
            """
            
            # ----------------------------------------------------------------
            # PRZETWARZANIE OTRZYMANYCH DANYCH
            # ----------------------------------------------------------------
            
            # Konwersja payload z bytes na string
            # W prawdziwej aplikacji: deserializacja JSON, protobuf, etc.
            payload_str = sample.payload.to_string()
            
            # Wyświetlenie otrzymanych danych
            # sample.kind - typ operacji (PUT = nowe dane, DELETE = usunięcie)
            print(
                f">> [Subscriber] Received {sample.kind} "
                f"('{sample.key_expr}': '{payload_str}')"
            )
            
            # ----------------------------------------------------------------
            # TU: PRZETWARZANIE DANYCH DLA TWOJEJ APLIKACJI
            # ----------------------------------------------------------------
            # Przykłady:
            # 1. Parsowanie JSON:
            #    import json
            #    data = json.loads(payload_str)
            #    x, y, z = data['x'], data['y'], data['z']
            #
            # 2. Aktualizacja stanu robota:
            #    robot.update_position(x, y, z)
            #
            # 3. Logowanie do bazy:
            #    db.insert(sample.key_expr, payload_str, sample.timestamp)
            #
            # 4. Wysłanie do innego systemu:
            #    forward_to_controller(data)

        # ========================================================================
        # KROK 4: DEKLARACJA SUBSCRIBER
        # ========================================================================
        # Deklarujemy subscriber, który będzie odbierać dane pasujące do 'key'
        # i wywołuje 'listener' dla każdego otrzymanego sample.
        # 
        # CO SIĘ DZIEJE:
        # 1. Zenoh rejestruje nasz subscriber w sieci
        # 2. Informuje publisher'ów o naszym zainteresowaniu
        # 3. Publisher'y zaczynają wysyłać dane
        # 4. Każdy sample wywołuje listener()
        #
        # UWAGA: Deklaracja jest asynchroniczna!
        # Dane mogą zacząć przychodzić natychmiast po deklaracji.
        session.declare_subscriber(key, listener)

        # ========================================================================
        # KROK 5: UTRZYMYWANIE PROGRAMU W DZIAŁANIU
        # ========================================================================
        # Subscriber działa w tle (asynchronicznie), więc główny wątek musi
        # być podtrzymany. Inaczej program zakończyłby się natychmiast.
        print("Press CTRL-C to quit...")
        print("=" * 60)
        print("OCZEKIWANIE NA DANE")
        print("=" * 60)
        print("→ Subscriber aktywny i gotowy do odbioru")
        print("→ Callback będzie wywoływany automatycznie")
        print("→ Naciśnij CTRL-C aby zakończyć\n")
        
        try:
            # Nieskończona pętla - czeka na dane
            # sleep(1) redukuje zużycie CPU (zamiast while True bez sleep)
            while True:
                time.sleep(1)
                # W tym czasie callback'i są wywoływane w tle!
                
        except KeyboardInterrupt:
            # Graceful shutdown po CTRL-C
            print("\n" + "=" * 60)
            print("ZATRZYMYWANIE SUBSCRIBER")
            print("=" * 60)
    
    # Session automatycznie zamknięta (dzięki 'with')
    # Subscriber automatycznie wyrejestrowany
    print("✅ Subscriber zakończony.")


# ================================================================================
# PARSOWANIE ARGUMENTÓW WIERSZA POLECEŃ
# ================================================================================
if __name__ == "__main__":
    # IMPORT: argparse do parsowania CLI
    import argparse

    # IMPORT: moduł common z helper functions
    import common

    # Tworzenie parsera argumentów
    parser = argparse.ArgumentParser(
        prog="z_sub", 
        description="zenoh sub example - Przykład subskrybowania danych w Zenoh"
    )
    
    # Dodanie standardowych argumentów Zenoh
    common.add_config_arguments(parser)
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --key / -k
    # ----------------------------------------------------------------------------
    # Key expression określające jakie dane chcemy odbierać
    # 
    # PRZYKŁADY KEY EXPRESSIONS:
    # 
    # 1. DOKŁADNE DOPASOWANIE:
    #    "robot/pose" - tylko ten konkretny klucz
    # 
    # 2. WILDCARD JEDEN POZIOM (*):
    #    "robot/*/temperature"
    #    ✅ Dopasuje: robot/arm/temperature, robot/leg/temperature
    #    ❌ NIE dopasuje: robot/arm/joint1/temperature (zbyt głęboko)
    # 
    # 3. WILDCARD WIELE POZIOMÓW (**):
    #    "robot/**"
    #    ✅ Dopasuje: robot/pose, robot/arm/temperature, robot/sensors/imu/acc
    # 
    # 4. KOMBINACJE:
    #    "robot/sensors/*/temperature"
    #    ✅ Dopasuje: robot/sensors/cpu/temperature, robot/sensors/motor/temperature
    # 
    # UWAGA NA WYDAJNOŚĆ:
    # - "**" odbiera WSZYSTKO - używaj ostrożnie!
    # - Im bardziej specyficzny klucz, tym lepiej
    parser.add_argument(
        "--key",
        "-k",
        dest="key",
        default="demo/example/**",
        type=str,
        help="The key expression to subscribe to (może zawierać * i **)",
    )

    # Parse argumentów
    args = parser.parse_args()
    
    # Utworzenie konfiguracji Zenoh
    conf = common.get_config_from_args(args)

    # Wywołanie głównej funkcji
    main(conf, args.key)


# ================================================================================
# PRZYKŁADY UŻYCIA
# ================================================================================
"""
1. PODSTAWOWE UŻYCIE - ODBIERANIE WSZYSTKIEGO Z DEMO:
   python3 z_sub.pl.py
   → Odbiera wszystko pasujące do "demo/example/**"

2. KONKRETNY KLUCZ:
   python3 z_sub.pl.py -k robot/pose
   → Odbiera tylko dane z klucza "robot/pose"

3. WSZYSTKIE CZUJNIKI ROBOTA:
   python3 z_sub.pl.py -k 'robot/sensors/**'
   → Odbiera wszystkie dane z czujników
   UWAGA: Cudzysłowy ' ' są ważne w bash (** to wildcard bash)

4. TYLKO TEMPERATURY:
   python3 z_sub.pl.py -k 'robot/*/temperature'
   → Odbiera: robot/cpu/temperature, robot/motor/temperature, etc.

5. KONKRETNA KAMERA:
   python3 z_sub.pl.py -k robot/sensors/camera/left
   → Odbiera tylko dane z lewej kamery

6. WSZYSTKO:
   python3 z_sub.pl.py -k '**'
   → Odbiera WSZYSTKIE dane w sieci Zenoh
   UWAGA: Może być dużo danych!

7. Z POŁĄCZENIEM DO ROUTERA:
   python3 z_sub.pl.py -k 'robot/**' -e tcp/192.168.1.100:7447
   → Łączy się z routerem i odbiera dane robota

TEST Z PUBLISHER'EM:
   Terminal 1:
       python3 z_sub.pl.py -k 'test/**'
   
   Terminal 2:
       python3 z_pub.py -k test/data -p "Hello Zenoh"
   
   → Subscriber otrzyma: ">> [Subscriber] Received PUT ('test/data': 'Hello Zenoh')"
"""


# ================================================================================
# ZADANIA DLA STUDENTÓW
# ================================================================================
"""
ZADANIE 1 - PODSTAWY:
    a) Uruchom subscriber z kluczem 'demo/**'
    b) W innym terminalu uruchom z_pub.py
    c) Obserwuj jak dane przepływają
    d) Zatrzymaj publisher - co się dzieje?

ZADANIE 2 - KEY EXPRESSIONS:
    Eksperymentuj z różnymi key expressions:
    a) 'robot/pose' - konkretny klucz
    b) 'robot/*' - jeden poziom
    c) 'robot/**' - wszystkie poziomy
    d) 'robot/*/temperature' - wzorzec
    
    Dla każdego przypadku przetestuj z różnymi publisher'ami.
    Które dane są odbierane, a które nie?

ZADANIE 3 - WIELE SUBSCRIBER'ÓW:
    Uruchom 3 subscriber'y w 3 terminalach:
    Terminal 1: python3 z_sub.pl.py -k 'robot/**'
    Terminal 2: python3 z_sub.pl.py -k 'robot/sensors/**'
    Terminal 3: python3 z_sub.pl.py -k 'robot/sensors/imu'
    
    Następnie publikuj:
    python3 z_pub.py -k robot/sensors/imu -p "acc:9.8"
    
    Które subscriber'y otrzymają dane?

ZADANIE 4 - PRZETWARZANIE DANYCH:
    Zmodyfikuj callback listener() aby:
    a) Parsował JSON (json.loads())
    b) Ekstraktował konkretne pola
    c) Wyświetlał je w czytelnej formie
    d) Liczył ile wiadomości otrzymano

ZADANIE 5 - ROBOT:
    Napisz subscriber dla symulowanego robota, który:
    a) Odbiera dane pozycji (x, y, z)
    b) Wyświetla pozycję na wykresie (matplotlib) w czasie rzeczywistym
    c) Zapisuje historię do pliku CSV
    d) Alarmuje gdy bateria <20%

ZADANIE 6 - ZAAWANSOWANE - FILTROWANIE:
    Zmodyfikuj callback aby:
    a) Odrzucał dane starsze niż 1 sekunda (timestamp)
    b) Filtrował duplikaty
    c) Agregował dane (średnia z ostatnich 10 samples)
    d) Wysyłał przetworzone dane dalej (do innego klucza)

ZADANIE 7 - PERFORMANCE:
    Zmierz:
    a) Maksymalną częstotliwość odbioru (samples/s)
    b) Latencję (czas od publikacji do odbioru)
    c) Opóźnienie przy wielu subscriber'ach
    
    Użyj: time.time() lub time.perf_counter()
"""


# ================================================================================
# CZĘSTO ZADAWANE PYTANIA
# ================================================================================
"""
Q: Co się stanie jeśli callback jest wolny?
A: Zenoh buforuje nadchodzące samples. Ale uważaj - zbyt wolny callback może
   prowadzić do opóźnień lub utraty danych. Rozwiązanie: użyj kolejki (queue)
   i przetwarzaj dane w osobnym wątku.

Q: Czy mogę mieć wielu subscriber'ów na tym samym kluczu?
A: TAK! Każdy subscriber otrzyma kopię danych. To podstawa wzorca pub/sub.

Q: Czy subscriber otrzyma dane opublikowane przed jego uruchomieniem?
A: NIE (domyślnie). Dane są strumieniowane. Aby otrzymać historyczne dane,
   użyj Storage lub Query/Queryable.

Q: Co oznacza sample.kind = DELETE?
A: Publisher może wysłać DELETE zamiast PUT, sygnalizując usunięcie danych.
   Użyteczne dla storage - wiedzą że mają usunąć wartość.

Q: Jak obsłużyć błędy w callback?
A: ZAWSZE używaj try-except w callback! Nieobsłużony błąd może zatrzymać
   odbieranie danych:
   
   def listener(sample):
       try:
           # przetwarzanie...
       except Exception as e:
           print(f"Błąd: {e}")
           # NIE pozwól błędowi przerwać subscriber'a

Q: Jaka jest różnica między subscriber a queryable?
A: 
   - SUBSCRIBER: Odbiera dane PUSHED w czasie rzeczywistym (strumieniowanie)
   - QUERYABLE: Odpowiada na zapytania ON-DEMAND (request-response)
   
   Użyj subscriber dla telemetrii, queryable dla konfiguracji/stanu.

Q: Czy mogę dynamicznie zmieniać key expression?
A: Musisz undeclare starego subscriber'a i declare nowego.
   Lub użyj wielu subscriber'ów jednocześnie.
"""


# ================================================================================
# WZORCE PROJEKTOWE
# ================================================================================
"""
WZORZEC 1: MULTI-THREADED PROCESSING
    Callback tylko dodaje do kolejki, osobny wątek przetwarza:
    
    import queue
    import threading
    
    q = queue.Queue()
    
    def listener(sample):
        q.put(sample)  # Szybkie - tylko dodanie do kolejki
    
    def processor():
        while True:
            sample = q.get()
            # Czasochłonne przetwarzanie...
            process(sample)
    
    threading.Thread(target=processor, daemon=True).start()
    session.declare_subscriber(key, listener)

WZORZEC 2: STATEFUL SUBSCRIBER
    Subscriber utrzymuje stan między callback'ami:
    
    class StatefulSubscriber:
        def __init__(self):
            self.count = 0
            self.last_value = None
        
        def callback(self, sample):
            self.count += 1
            self.last_value = sample.payload.to_string()
            print(f"Otrzymano {self.count} wiadomości")
    
    sub = StatefulSubscriber()
    session.declare_subscriber(key, sub.callback)

WZORZEC 3: AGGREGATOR
    Zbieranie danych z wielu źródeł:
    
    data_cache = {}
    
    def listener(sample):
        key = str(sample.key_expr)
        data_cache[key] = sample.payload.to_string()
        
        # Gdy mamy dane ze wszystkich czujników
        if all(k in data_cache for k in required_keys):
            process_complete_dataset(data_cache)

WZORZEC 4: FORWARDER
    Subscriber otrzymuje dane i przekazuje dalej (transformacja):
    
    def listener(sample):
        # Przetwórz dane
        processed = transform(sample.payload)
        
        # Przekaż dalej
        session.put("processed/" + sample.key_expr, processed)
"""
