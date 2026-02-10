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
PRZYKŁAD ZENOH: QUERYABLE (ODPOWIADANIE NA ZAPYTANIA)
================================================================================

CEL PRZYKŁADU:
    Demonstracja wzorca Queryable - serwisu odpowiadającego na zapytania.
    Queryable to odpowiednik serwera w modelu request-response (RPC).

WZORZEC QUERY/QUERYABLE:
    ┌─────────┐          GET          ┌────────────┐
    │ Querier │ ────────────────────> │ Queryable  │
    │         │ <──────────────────── │            │
    │ (klient)│         REPLY         │  (serwer)  │
    └─────────┘                       └────────────┘
    
    - QUERIER (z_get.py): Wysyła zapytanie, czeka na odpowiedzi
    - QUERYABLE (ten program): Odbiera zapytania, wysyła odpowiedzi

RÓŻNICE PUB/SUB vs QUERY/QUERYABLE:
    
    PUB/SUB (Publisher/Subscriber):
    ✓ Push model - dane wysyłane automatycznie
    ✓ Strumieniowanie - ciągły przepływ danych
    ✓ Broadcast - wielu odbiorców
    ✓ Best effort - brak gwarancji dostarczenia
    
    QUERY/QUERYABLE:
    ✓ Pull model - dane na żądanie
    ✓ Request-response - pytanie → odpowiedź
    ✓ Point-to-point lub multipoint
    ✓ Z timeoutem - czeka na odpowiedzi

KIEDY UŻYWAĆ QUERYABLE:
    - Serwisy zwracające aktualny stan (np. pozycja robota)
    - RPC (Remote Procedure Call) - wywoływanie funkcji zdalnie
    - Konfiguracja - get/set parametrów
    - Bazy danych / Storage - zapytania o dane
    - Diagnostyka - informacje o systemie na żądanie
    
DLA ROBOTA UNITREE G1:
    - Serwis zwracający aktualną pozycję robota
    - Serwis konfiguracji (PID gains, limity)
    - Serwis diagnostyczny (stan, błędy)
    - Serwis planowania (oblicz trajektorię)
    
URUCHOMIENIE:
    Terminal 1 (ten program - queryable/serwer):
        python3 z_queryable.pl.py -k robot/config/gains
    
    Terminal 2 (querier/klient):
        python3 z_get.py -s robot/config/gains

PARAMETRY:
    -k, --key      : Key expression dla queryable
    -p, --payload  : Odpowiedź do wysłania
    --complete     : Deklaruj jako "complete" (pełna odpowiedź)

================================================================================
"""

# IMPORT: time do utrzymania programu w działaniu
import time

# IMPORT: Biblioteka Zenoh
import zenoh


def main(conf: zenoh.Config, key: str, payload: str, complete: bool):
    """
    Główna funkcja programu Queryable.
    
    PRZEPŁYW PROGRAMU:
        1. Inicjalizacja logowania
        2. Otwarcie sesji Zenoh
        3. Deklaracja Queryable
        4. Pętla odbierania zapytań i wysyłania odpowiedzi
        
    PARAMETRY:
        conf : zenoh.Config
            Konfiguracja Zenoh
        key : str
            Key expression określające na jakie zapytania odpowiadamy
            Przykład: "robot/config/**" - wszystkie zapytania o konfigurację
        payload : str
            Domyślna odpowiedź do wysłania
            W prawdziwej aplikacji: generowana dynamicznie
        complete : bool
            Jeśli True, ten queryable jest "kompletny" dla tego klucza
            (jedyna/ostateczna odpowiedź, nie ma innych queryable)
    """
    
    # ============================================================================
    # KROK 1: INICJALIZACJA LOGOWANIA
    # ============================================================================
    zenoh.init_log_from_env_or("error")

    # ============================================================================
    # KROK 2: OTWARCIE SESJI ZENOH
    # ============================================================================
    print("Opening session...")
    print("  → Łączenie z siecią Zenoh...")
    
    with zenoh.open(conf) as session:
        
        # ========================================================================
        # KROK 3: DEKLARACJA QUERYABLE
        # ========================================================================
        # Queryable to zadeklarowany "serwis" odpowiadający na zapytania
        # pasujące do określonego key expression.
        #
        # COMPLETE FLAG:
        # - complete=True : Ten queryable dostarcza kompletną odpowiedź
        #                   Querier może przestać czekać po otrzymaniu tej odpowiedzi
        # - complete=False : Mogą być inne queryable z dodatkowymi odpowiedziami
        #                   Querier czeka na timeout lub na wszystkie odpowiedzi
        #
        # PRZYKŁAD:
        #   Key: "robot/config/**"
        #   Zapytanie: "robot/config/gains"
        #   ✅ Dopasowane - queryable odpowie
        print(f"Declaring Queryable on '{key}'...")
        print(f"  → Będę odpowiadać na zapytania pasujące do: {key}")
        print(f"  → Complete mode: {complete}")
        
        queryable = session.declare_queryable(key, complete=complete)

        # ========================================================================
        # KROK 4: PĘTLA ODBIERANIA ZAPYTAŃ
        # ========================================================================
        print("Press CTRL-C to quit...")
        print("=" * 60)
        print("QUERYABLE AKTYWNY - OCZEKIWANIE NA ZAPYTANIA")
        print("=" * 60)
        print("→ Queryable gotowy do odpowiadania")
        print("→ Wyślij zapytanie używając z_get.py\n")
        
        try:
            while True:
                # ----------------------------------------------------------------
                # ODBIERANIE ZAPYTANIA
                # ----------------------------------------------------------------
                # queryable.recv() blokuje do momentu otrzymania zapytania
                # Używamy context managera (with) do automatycznego czyszczenia
                with queryable.recv() as query:
                    """
                    OBIEKT QUERY zawiera:
                        - query.selector : Selector zapytania (key expression)
                        - query.payload : Opcjonalny payload w zapytaniu (może być None)
                        - query.parameters : Parametry zapytania (np. ?param=value)
                    """
                    
                    # ------------------------------------------------------------
                    # WYŚWIETLENIE OTRZYMANEGO ZAPYTANIA
                    # ------------------------------------------------------------
                    if query.payload is not None:
                        # Zapytanie z payload (dane w zapytaniu)
                        # Użyteczne dla zapytań z parametrami: "get temperature for room=5"
                        print(
                            f"\n>> [Queryable] Otrzymano Query '{query.selector}'"
                            f" z payload: '{query.payload.to_string()}'"
                        )
                        print(f"   → Ktoś pyta i dostarcza dodatkowe dane")
                    else:
                        # Proste zapytanie bez payload
                        print(f"\n>> [Queryable] Otrzymano Query '{query.selector}'")
                        print(f"   → Ktoś pyta o: {query.selector}")
                    
                    # ------------------------------------------------------------
                    # PRZETWARZANIE ZAPYTANIA I PRZYGOTOWANIE ODPOWIEDZI
                    # ------------------------------------------------------------
                    # W tym miejscu normalnie:
                    # 1. Parsujemy selector i payload
                    # 2. Wykonujemy odpowiednie operacje (odczyt z bazy, obliczenia)
                    # 3. Generujemy odpowiedź
                    #
                    # PRZYKŁAD:
                    # if "gains" in query.selector:
                    #     response = get_pid_gains()
                    # elif "status" in query.selector:
                    #     response = get_robot_status()
                    # else:
                    #     response = "Unknown query"
                    
                    # Ten przykład zawsze zwraca ten sam payload
                    response_payload = payload
                    
                    # ------------------------------------------------------------
                    # WYSŁANIE ODPOWIEDZI
                    # ------------------------------------------------------------
                    # query.reply() wysyła odpowiedź z powrotem do querier'a
                    # 
                    # PARAMETRY reply():
                    #   - key_expr : Klucz odpowiedzi (zazwyczaj taki sam jak query)
                    #   - payload : Dane odpowiedzi
                    #
                    # WAŻNE: Można wysłać wiele odpowiedzi dla jednego zapytania!
                    # Przykład: query o "sensors/**" może dać wiele odpowiedzi
                    print(f"   📤 Wysyłam odpowiedź: '{response_payload}'")
                    query.reply(key, response_payload)
                    
                    # ------------------------------------------------------------
                    # ALTERNATYWNY SPOSÓB WYSŁANIA ODPOWIEDZI
                    # ------------------------------------------------------------
                    # Zamiast używać 'with', można ręcznie wywołać query.drop()
                    # po obsłużeniu zapytania:
                    #
                    # query = queryable.recv()
                    # query.reply(key, payload)
                    # query.drop()  # Zwalnia zasoby
                    #
                    # Context manager ('with') robi to automatycznie
                    
                    # ------------------------------------------------------------
                    # WYSŁANIE BŁĘDU JAKO ODPOWIEDZI
                    # ------------------------------------------------------------
                    # Jeśli zapytanie nie może być obsłużone, możesz wysłać błąd:
                    #
                    # try:
                    #     response = process_query(query)
                    #     query.reply(key, response)
                    # except Exception as e:
                    #     query.reply_err(key, f"Error: {str(e)}")
                    
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("ZATRZYMYWANIE QUERYABLE")
            print("=" * 60)
    
    # Session i queryable automatycznie zamknięte
    print("✅ Queryable zakończony.")


# ================================================================================
# PARSOWANIE ARGUMENTÓW WIERSZA POLECEŃ
# ================================================================================
if __name__ == "__main__":
    import argparse
    import json

    import common

    # Tworzenie parsera
    parser = argparse.ArgumentParser(
        prog="z_queryable", 
        description="zenoh queryable example - Serwis odpowiadający na zapytania"
    )
    
    common.add_config_arguments(parser)
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --key / -k
    # ----------------------------------------------------------------------------
    # Key expression określające na jakie zapytania odpowiadamy
    # 
    # DOPASOWANIE:
    # - Zapytanie: "robot/config/gains"
    # - Queryable key: "robot/config/**"
    # - ✅ DOPASOWANE - queryable odpowie
    # 
    # - Zapytanie: "robot/status"
    # - Queryable key: "robot/config/**"
    # - ❌ NIE DOPASOWANE - queryable NIE odpowie
    #
    # MOŻE BYĆ WIELU QUERYABLE:
    # - Queryable 1: "robot/config/gains"
    # - Queryable 2: "robot/config/limits"
    # - Zapytanie: "robot/config/**"
    # - Oba queryable odpowiedzą!
    parser.add_argument(
        "--key",
        "-k",
        dest="key",
        default="demo/example/zenoh-python-queryable",
        type=str,
        help="The key expression matching queries to reply to.",
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --payload / -p
    # ----------------------------------------------------------------------------
    # Domyślna odpowiedź do wysłania
    # W prawdziwej aplikacji byłaby generowana dynamicznie
    parser.add_argument(
        "--payload",
        "-p",
        dest="payload",
        default="Queryable from Python!",
        type=str,
        help="The payload to reply to queries.",
    )
    
    # ----------------------------------------------------------------------------
    # ARGUMENT: --complete
    # ----------------------------------------------------------------------------
    # Deklaruje queryable jako "complete" (kompletne)
    # 
    # COMPLETE vs NON-COMPLETE:
    # 
    # COMPLETE (--complete):
    # - Ten queryable dostarcza kompletną odpowiedź
    # - Querier może przestać czekać po otrzymaniu odpowiedzi
    # - Użyj gdy: jeden queryable ma wszystkie dane
    # 
    # NON-COMPLETE (domyślnie):
    # - Mogą być inne queryable z dodatkowymi odpowiedziami
    # - Querier czeka na timeout lub wszystkie odpowiedzi
    # - Użyj gdy: wiele queryable może odpowiedzieć (np. distributed storage)
    #
    # PRZYKŁAD:
    # Terminal 1: python3 z_queryable.pl.py -k robot/status --complete
    # Terminal 2: python3 z_get.py -s robot/status
    # → Querier dostanie odpowiedź i zakończy (nie czeka na timeout)
    parser.add_argument(
        "--complete",
        dest="complete",
        default=False,
        action="store_true",
        help="Declare the queryable as complete w.r.t. the key expression.",
    )

    args = parser.parse_args()
    conf = common.get_config_from_args(args)

    main(conf, args.key, args.payload, args.complete)


# ================================================================================
# PRZYKŁADY UŻYCIA
# ================================================================================
"""
1. PODSTAWOWY QUERYABLE:
   Terminal 1 (queryable - odpowiada):
       python3 z_queryable.pl.py
   
   Terminal 2 (querier - pyta):
       python3 z_get.py -s demo/example/zenoh-python-queryable
   
   → Queryable odpowie: "Queryable from Python!"

2. SERWIS STATUSU ROBOTA:
   Terminal 1:
       python3 z_queryable.pl.py -k robot/status -p "OPERATIONAL"
   
   Terminal 2:
       python3 z_get.py -s robot/status
   
   → Odpowiedź: "OPERATIONAL"

3. SERWIS KONFIGURACJI:
   Terminal 1:
       python3 z_queryable.pl.py -k robot/config/gains -p '{"p":10,"i":0.5,"d":2}'
   
   Terminal 2:
       python3 z_get.py -s robot/config/gains
   
   → Odpowiedź: JSON z PID gains

4. COMPLETE QUERYABLE:
   Terminal 1:
       python3 z_queryable.pl.py -k robot/data --complete -p "Final answer"
   
   Terminal 2:
       python3 z_get.py -s robot/data --timeout 1.0
   
   → Querier dostanie odpowiedź i zakończy natychmiast (nie czeka timeout)

5. WIELE QUERYABLE (DISTRIBUTED):
   Terminal 1:
       python3 z_queryable.pl.py -k 'robot/sensors/**' -p 'sensor1: 23.5'
   
   Terminal 2:
       python3 z_queryable.pl.py -k 'robot/sensors/**' -p 'sensor2: 42.1'
   
   Terminal 3:
       python3 z_get.py -s 'robot/sensors/**'
   
   → Querier dostanie 2 odpowiedzi (od obu queryable)
"""


# ================================================================================
# ZADANIA DLA STUDENTÓW
# ================================================================================
"""
ZADANIE 1 - PODSTAWY:
    a) Uruchom queryable z domyślnymi parametrami
    b) W innym terminalu użyj z_get.py do wysłania zapytania
    c) Obserwuj przepływ: zapytanie → queryable → odpowiedź → querier

ZADANIE 2 - KEY MATCHING:
    Eksperymentuj z dopasowaniem kluczy:
    
    Terminal 1: python3 z_queryable.pl.py -k 'robot/config/**'
    
    Następnie testuj różne zapytania:
    Terminal 2a: python3 z_get.py -s 'robot/config/gains'        # ✅ Dopasuje
    Terminal 2b: python3 z_get.py -s 'robot/config/limits'       # ✅ Dopasuje
    Terminal 2c: python3 z_get.py -s 'robot/status'              # ❌ NIE dopasuje
    Terminal 2d: python3 z_get.py -s 'robot/**'                  # ✅ Dopasuje

ZADANIE 3 - WIELE QUERYABLE:
    Uruchom 3 queryable:
    Terminal 1: python3 z_queryable.pl.py -k 'data/**' -p 'answer from Q1'
    Terminal 2: python3 z_queryable.pl.py -k 'data/**' -p 'answer from Q2'
    Terminal 3: python3 z_queryable.pl.py -k 'data/**' -p 'answer from Q3'
    
    Następnie zapytaj:
    Terminal 4: python3 z_get.py -s 'data/**' --timeout 2.0
    
    Ile odpowiedzi otrzymasz? Dlaczego?

ZADANIE 4 - COMPLETE FLAG:
    Porównaj zachowanie:
    
    A) BEZ --complete:
       Terminal 1: python3 z_queryable.pl.py -k 'test' -p 'response'
       Terminal 2: python3 z_get.py -s 'test' --timeout 5.0
       → Querier czeka pełne 5 sekund
    
    B) Z --complete:
       Terminal 1: python3 z_queryable.pl.py -k 'test' -p 'response' --complete
       Terminal 2: python3 z_get.py -s 'test' --timeout 5.0
       → Querier kończy natychmiast po otrzymaniu odpowiedzi

ZADANIE 5 - DYNAMICZNE ODPOWIEDZI:
    Zmodyfikuj kod queryable aby:
    a) Parsować selector (np. if "temperature" in query.selector)
    b) Generować odpowiedź na podstawie selektora
    c) Zwracać JSON z aktualnymi danymi
    d) Obsługiwać payload w zapytaniu (query.payload)
    
    Przykład:
        if "gains" in query.selector:
            response = json.dumps({"p": 10, "i": 0.5, "d": 2})
        elif "status" in query.selector:
            response = "OPERATIONAL"
        else:
            response = "Unknown query"

ZADANIE 6 - ROBOT SERVICE:
    Napisz queryable service dla robota:
    a) Serwis konfiguracji - zwraca PID gains dla różnych stawów
    b) Serwis statusu - zwraca aktualny stan robota
    c) Serwis diagnostyczny - zwraca błędy i ostrzeżenia
    d) Serwis obliczeniowy - oblicza trajektorię (z payloadem w query)
    
    Użyj JSON dla strukturyzowanych odpowiedzi.

ZADANIE 7 - STORAGE QUERYABLE:
    Zaimplementuj prosty queryable storage:
    a) Użyj dict do przechowywania wartości (klucz → wartość)
    b) Queryable zwraca wartości pasujące do selektora
    c) Połącz z subscriber'em do zapisywania danych
    
    Wskazówka: Zobacz z_storage.py
"""


# ================================================================================
# CZĘSTO ZADAWANE PYTANIA
# ================================================================================
"""
Q: Jaka jest różnica między queryable a subscriber?
A: 
   SUBSCRIBER: Odbiera dane PUSH'owane automatycznie (strumieniowanie)
   QUERYABLE: Odpowiada na zapytania ON-DEMAND (request-response)
   
   Użyj subscriber dla ciągłych danych (telemetria).
   Użyj queryable dla danych na żądanie (stan, konfiguracja).

Q: Czy mogę wysłać wiele odpowiedzi dla jednego zapytania?
A: TAK! Wielokrotnie wywołaj query.reply(). Przydatne gdy queryable
   ma wiele wartości pasujących do selektora.
   
   Example:
       for item in matching_items:
           query.reply(item.key, item.value)

Q: Co się stanie jeśli queryable nie wyśle odpowiedzi?
A: Querier poczeka do timeout i zakończy (możliwe bez odpowiedzi).
   ZAWSZE wysyłaj odpowiedź lub error (query.reply_err()).

Q: Czy mogę mieć wielu queryable na tym samym kluczu?
A: TAK! Każdy queryable może odpowiedzieć. Querier otrzyma wszystkie
   odpowiedzi. Użyteczne dla distributed storage.

Q: Kiedy używać --complete?
A: Użyj gdy:
   - Tylko jeden queryable odpowiada
   - Odpowiedź jest kompletna (nie potrzeba czekać na innych)
   - Chcesz zmniejszyć latencję (querier nie czeka timeout)
   
   NIE używaj gdy:
   - Wiele queryable może odpowiedzieć (distributed)
   - Chcesz zbierać odpowiedzi od wszystkich

Q: Jak obsłużyć błędy?
A: Użyj query.reply_err():
   
   try:
       result = process_query(query)
       query.reply(key, result)
   except Exception as e:
       query.reply_err(key, f"Error: {str(e)}")

Q: Czy queryable.recv() blokuje?
A: TAK. Blokuje do otrzymania zapytania. Jeśli chcesz non-blocking,
   użyj timeout lub select/poll z innymi operacjami.

Q: Jak zaimplementować timeout po stronie queryable?
A: Użyj tryby asynchronicznego lub wielowątkowego:
   
   import select
   # Sprawdź czy jest zapytanie bez blokowania
   # Jeśli nie, wykonaj inne zadania
"""


# ================================================================================
# WZORCE PROJEKTOWE
# ================================================================================
"""
WZORZEC 1: SIMPLE RPC (Remote Procedure Call)
    Queryable jako serwis wykonujący operacje:
    
    def queryable_callback(query):
        # Parse operation from selector
        if "add" in query.selector:
            a, b = parse_numbers(query.payload)
            result = a + b
        elif "multiply" in query.selector:
            a, b = parse_numbers(query.payload)
            result = a * b
        query.reply(query.selector, str(result))

WZORZEC 2: CONFIGURATION SERVICE
    Centralna konfiguracja dla systemu:
    
    config = {
        "robot/gains": {"p": 10, "i": 0.5, "d": 2},
        "robot/limits": {"max_speed": 1.5, "max_accel": 2.0}
    }
    
    def config_queryable(query):
        selector = str(query.selector)
        if selector in config:
            query.reply(selector, json.dumps(config[selector]))
        else:
            query.reply_err(selector, "Config not found")

WZORZEC 3: MULTI-VALUE QUERYABLE
    Queryable zwracający wiele wartości:
    
    storage = {
        "robot/sensors/temp1": "23.5",
        "robot/sensors/temp2": "24.1",
        "robot/sensors/humidity": "60"
    }
    
    def storage_queryable(query):
        selector = str(query.selector)
        # Znajdź wszystkie pasujące klucze
        for key, value in storage.items():
            if matches(key, selector):
                query.reply(key, value)
        
        # Jeśli nic nie znaleziono
        if no_matches:
            query.reply_err(selector, "No data found")

WZORZEC 4: COMPUTE SERVICE
    Queryable wykonujący obliczenia na żądanie:
    
    def compute_queryable(query):
        # Odbierz parametry z payload
        params = json.loads(query.payload.to_string())
        
        # Wykonaj obliczenia
        if "trajectory" in query.selector:
            result = compute_trajectory(params)
        elif "kinematics" in query.selector:
            result = compute_inverse_kinematics(params)
        
        # Wyślij wynik
        query.reply(query.selector, json.dumps(result))

WZORZEC 5: FALLBACK CHAIN
    Wiele queryable z fallback:
    
    # Queryable 1 (primary) - complete=True jeśli ma odpowiedź
    def primary_queryable(query):
        if has_answer(query):
            query.reply(query.selector, get_answer())
        # Jeśli nie ma odpowiedzi, nie odpowiada
        # Inne queryable mogą odpowiedzieć
    
    # Queryable 2 (fallback)
    def fallback_queryable(query):
        # Zawsze odpowiada (default value)
        query.reply(query.selector, "default_value")
"""
