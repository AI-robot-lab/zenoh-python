# Przykłady Zenoh Python

## Wprowadzenie

Ten katalog zawiera przykłady demonstrujące różne funkcjonalności biblioteki Zenoh w Pythonie.

**Cel przykładów:**
- Nauczyć podstawowych wzorców komunikacji w Zenoh
- Pokazać praktyczne zastosowania API
- Zapewnić gotowe szablony do własnych projektów

---

## Jak uruchomić przykłady

### Podstawowe uruchomienie

```bash
python3 <nazwa_przykładu.py>
```

### Pomoc dla każdego przykładu

Każdy przykład akceptuje opcję `-h` lub `--help`, która wyświetla:
- Opis działania przykładu
- Listę dostępnych argumentów
- Wartości domyślne parametrów

```bash
python3 z_pub.py --help
```

### Konfiguracja dla Docker

**Problem:** Docker nie wspiera multicast UDP, który jest używany przez Zenoh do automatycznego odkrywania (scouting).

**Rozwiązanie:** Dodaj opcję `-e tcp/localhost:7447` do wymuszenia połączenia TCP:

```bash
python3 z_pub.py -e tcp/localhost:7447
```

**Co oznacza ta opcja:**
- `-e` - endpoint (punkt końcowy)
- `tcp` - protokół TCP zamiast UDP
- `localhost:7447` - adres i port Zenoh Router w kontenerze Docker

---

## Opis przykładów

### 🔍 z_scout

**Cel:** Wykrywa dostępne w sieci węzły Zenoh (peers) i routery.

**Kiedy używać:**
- Diagnostyka sieci Zenoh
- Sprawdzenie, czy router jest dostępny
- Odkrycie innych aplikacji Zenoh w sieci

**Typowe użycie:**

```bash
python3 z_scout.py
```

**Co zobaczysz:**
- Listę wykrytych routerów z ich ID
- Listę wykrytych peer-ów (innych aplikacji)
- Informacje o lokalizacji (local/remote)

**Przykładowe wyjście:**
```
>> [SCOUT] Router 01234567 at tcp/192.168.1.100:7447
>> [SCOUT] Peer 89ABCDEF at udp/192.168.1.101:7447
```

---

### ℹ️ z_info

**Cel:** Wyświetla informacje o bieżącej sesji Zenoh.

**Kiedy używać:**
- Weryfikacja poprawności połączenia
- Sprawdzenie ID sesji
- Debugowanie konfiguracji

**Typowe użycie:**

```bash
python3 z_info.py
```

**Co zobaczysz:**
- ID sesji (unique identifier)
- Listę aktywnych locatorów (punkty połączenia)
- Tryb działania (peer/client)

**Praktyczne zastosowanie:**
- Przed rozpoczęciem pracy sprawdź, czy sesja się otworzyła
- Zweryfikuj, czy aplikacja łączy się z routerem

---

### 📤 z_put

**Cel:** Wysyła pojedynczą wartość (path/payload) do Zenoh.

**Jak to działa:**
1. Otwiera sesję Zenoh
2. Wysyła wartość pod określonym kluczem (key expression)
3. Zamyka sesję

**Kto odbierze dane:**
- Wszyscy subscriber'zy pasujący do klucza (np. [z_sub](#z_sub))
- Storage'y przechwytujące dane (np. [z_storage](#z_storage))

**Typowe użycie:**

```bash
# Domyślne wartości
python3 z_put.py

# Z własnymi parametrami
python3 z_put.py -k demo/example/test -p 'Hello World'
```

**Parametry:**
- `-k` / `--key` - klucz (key expression), np. `sensors/temperature`
- `-p` / `--payload` - dane do wysłania, np. `23.5`

**Przykład dla robota:**
```bash
# Wysłanie pozycji stawu
python3 z_put.py -k robot/joints/left_arm/shoulder -p '45.5'

# Wysłanie stanu baterii
python3 z_put.py -k robot/battery/level -p '87'
```

**Różnica put vs pub:**
- `put` - jednorazowe wysłanie
- `pub` - ciągłe publikowanie (patrz [z_pub](#z_pub))

---

### 📡 z_pub

**Cel:** Deklaruje publisher i regularnie publikuje dane.

**Jak to działa:**
1. Otwiera sesję Zenoh
2. Deklaruje publisher na określonym kluczu
3. W pętli wysyła kolejne wiadomości
4. Działa do momentu przerwania (CTRL-C)

**Różnice między `put` a `pub`:**

| Funkcja | z_put | z_pub |
|---------|-------|-------|
| Liczba wysłań | 1 (single-shot) | Wiele (w pętli) |
| Deklaracja publishera | Nie | Tak |
| Wydajność | Niższa dla wielu | Wyższa dla wielu |
| Użycie | Pojedyncze eventy | Strumieniowanie |

**Typowe użycie:**

```bash
# Domyślne: wysyła co sekundę
python3 z_pub.py

# Własne parametry
python3 z_pub.py -k demo/example/test -p 'Hello World'

# Z określoną liczbą iteracji
python3 z_pub.py --iter 100 --interval 0.5
```

**Parametry:**
- `-k` / `--key` - klucz publikacji
- `-p` / `--payload` - bazowa treść wiadomości (będzie numerowana)
- `--iter` - liczba iteracji (brak = nieskończoność)
- `--interval` - odstęp między publikacjami w sekundach
- `--add-matching-listener` - monitorowanie subscriber'ów

**Matching Listener:**
```bash
python3 z_pub.py --add-matching-listener
```
Wyświetla, gdy:
- Pojawi się nowy subscriber
- Ostatni subscriber się rozłączy

**Przykład dla robota - telemetria:**
```bash
# Publikowanie pozycji robota co 100ms
python3 z_pub.py -k robot/pose/position --interval 0.1 -p 'x:0,y:0,z:0'

# Publikowanie danych z czujników IMU
python3 z_pub.py -k robot/sensors/imu --interval 0.01 -p 'ax:0,ay:0,az:9.81'
```

---

### 📥 z_sub

**Cel:** Tworzy subscriber, który nasłuchuje danych na określonym kluczu.

**Jak to działa:**
1. Otwiera sesję Zenoh
2. Deklaruje subscriber z funkcją callback
3. Czeka na nadchodzące dane
4. Wywołuje callback przy każdym otrzymaniu danych

**Typowe użycie:**

```bash
# Domyślny klucz (odbiera wszystko z demo/example/)
python3 z_sub.py

# Własny klucz
python3 z_sub.py -k 'demo/**'
```

**Key expressions (wyrażenia kluczy):**
- `demo/example` - dokładne dopasowanie
- `demo/*` - wszystko bezpośrednio pod demo (jeden poziom)
- `demo/**` - wszystko pod demo (wszystkie poziomy, rekurencyjnie)
- `robot/*/temperature` - np. robot/arm/temperature, robot/leg/temperature

**Przykłady zastosowania:**

```bash
# Nasłuchiwanie wszystkich danych z robota
python3 z_sub.py -k 'robot/**'

# Tylko dane z czujników
python3 z_sub.py -k 'robot/sensors/**'

# Konkretny czujnik
python3 z_sub.py -k 'robot/sensors/camera/front'
```

**Co zobaczysz:**
```
>> [Subscriber] Received PUT ('robot/sensors/imu': 'ax:0.1,ay:0.2,az:9.8')
>> [Subscriber] Received PUT ('robot/battery/level': '85')
```

---

### 🔍 z_get

**Cel:** Wysyła zapytanie (query) i odbiera odpowiedzi.

**Wzorzec Query/Queryable:**
- **z_get** (querier) - zadaje pytanie
- **z_queryable** (odpowiada) - udziela odpowiedzi

**Kiedy używać:**
- Potrzebujesz danych "na żądanie" (nie ciągłe strumieniowanie)
- Chcesz pobrać aktualny stan (np. aktualna pozycja robota)
- Wykonujesz zapytanie do storage (historyczne dane)

**Typowe użycie:**

```bash
# Zapytanie o wszystkie dane demo
python3 z_get.py

# Zapytanie z własnym selektorem
python3 z_get.py -s 'demo/**'

# Z timeout
python3 z_get.py -s 'robot/state' --timeout 5.0
```

**Parametry:**
- `-s` / `--selector` - selector (podobny do key expression)
- `-t` / `--target` - cel zapytania:
  - `BEST_MATCHING` - najbardziej pasujące queryable (domyślnie)
  - `ALL` - wszystkie pasujące queryable
  - `ALL_COMPLETE` - wszystkie, czeka na komplet odpowiedzi
- `-p` / `--payload` - opcjonalne dane w zapytaniu
- `--timeout` - maksymalny czas oczekiwania (sekundy)

**Przykład z robotem:**
```bash
# Pobierz aktualną pozycję robota
python3 z_get.py -s 'robot/pose/current'

# Pobierz konfigurację
python3 z_get.py -s 'robot/config/**'

# Zapytanie z parametrem (np. get trajectory for arm)
python3 z_get.py -s 'robot/trajectory' -p 'joint:left_arm'
```

**Co zobaczysz:**
```
>> Received ('robot/pose/current': 'x:1.5,y:2.3,z:0.0,heading:90')
>> Received ('robot/battery/level': '78')
```

---

### 🔁 z_querier

**Cel:** Tworzy querier, który cyklicznie wysyła zapytania.

**Różnica z z_get:**
- `z_get` - pojedyncze zapytanie (one-shot)
- `z_querier` - ciągłe zapytania (continuous)

**Kiedy używać:**
- Potrzebujesz regularnie aktualizowanego stanu
- Monitorujesz zmiany w czasie
- Polling (odpytywanie) zamiast push

**Typowe użycie:**

```bash
# Regularne zapytania
python3 z_querier.py

# Z własnym selektorem
python3 z_querier.py -s 'robot/state/**'
```

**Przykład - monitoring robota:**
```bash
# Co sekundę pytaj o stan
python3 z_querier.py -s 'robot/health/**'
```

---

### 💬 z_queryable

**Cel:** Tworzy queryable - funkcję odpowiadającą na zapytania.

**Jak to działa:**
1. Otwiera sesję
2. Deklaruje queryable na kluczu
3. Czeka na zapytania z [z_get](#z_get) lub [z_querier](#z_querier)
4. Wywołuje callback i wysyła odpowiedź

**Typowe użycie:**

```bash
# Domyślny queryable
python3 z_queryable.py

# Z własnymi parametrami
python3 z_queryable.py -k demo/example/queryable -p 'This is the result'
```

**Parametry:**
- `-k` / `--key` - klucz queryable
- `-p` / `--payload` - odpowiedź do wysłania

**Test działania:**

Terminal 1 (queryable - odpowiada):
```bash
python3 z_queryable.py -k robot/status -p 'OPERATIONAL'
```

Terminal 2 (querier - pyta):
```bash
python3 z_get.py -s robot/status
```

**Przykład dla robota:**
```bash
# Serwis zwracający aktualną pozycję
python3 z_queryable.py -k robot/pose/current -p 'x:0,y:0,z:0'

# Serwis zwracający konfigurację
python3 z_queryable.py -k robot/config/joints -p 'count:12,dof:6'
```

**Praktyczne zastosowanie:**
- Udostępnianie stanu robota na żądanie
- RPC (Remote Procedure Call) - wywoływanie funkcji zdalnie
- Serwisy konfiguracyjne

---

### 💾 z_storage

**Cel:** Prosta implementacja storage w pamięci.

**Co robi:**
1. **Subscriber** - przechowuje wszystkie otrzymane klucz/wartość w HashMap
2. **Queryable** - odpowiada na zapytania danymi z HashMap

**Wzorzec Storage:**
```
Publisher → Storage (subscriber) → HashMap
                ↓
Query → Storage (queryable) → odpowiedź z HashMap
```

**Typowe użycie:**

```bash
# Storage dla wszystkiego pod demo
python3 z_storage.py

# Storage dla danych robota
python3 z_storage.py -k 'robot/**'
```

**Scenariusz użycia:**

Terminal 1 - Storage:
```bash
python3 z_storage.py -k 'robot/**'
```

Terminal 2 - Publikuj dane:
```bash
python3 z_put.py -k robot/battery/level -p '95'
python3 z_put.py -k robot/temperature -p '42.5'
```

Terminal 3 - Odpytuj storage:
```bash
python3 z_get.py -s 'robot/**'
```

**Przykładowe wyjście:**
```
>> Received ('robot/battery/level': '95')
>> Received ('robot/temperature': '42.5')
```

**Praktyczne zastosowania:**
- Cache ostatnich wartości
- Historyczne dane (rozszerz o timestamp)
- State management dla robota
- Debugowanie - podgląd wszystkich published wartości

**Uwaga:** To jest prosty przykład w pamięci. Dane znikają po zamknięciu programu.

---

### 🚀 z_pub_thr & z_sub_thr

**Cel:** Test wydajności (throughput) pub/sub.

**Throughput** - przepustowość, ile danych można przesłać w jednostce czasu.

**Dlaczego ważne w robotyce:**
- Kamera 1080p @ 30fps = ~180 MB/s
- Lidar point cloud = dziesiątki MB/s
- Real-time control wymaga niskiej latencji i wysokiej przepustowości

**Jak używać:**

Terminal 1 - Subscriber (odbiera i mierzy):
```bash
python3 z_sub_thr.py
```

Terminal 2 - Publisher (wysyła z maksymalną prędkością):
```bash
python3 z_pub_thr.py 1024
```

**Parametr:** rozmiar wiadomości w bajtach (1024 = 1 KB)

**Co zobaczysz:**
```
Throughput: 1234.56 msg/s, 1234.56 MB/s
```

**Eksperymenty:**
```bash
# Małe wiadomości (sensor data)
python3 z_pub_thr.py 64

# Średnie wiadomości (compressed image)
python3 z_pub_thr.py 10240

# Duże wiadomości (raw image)
python3 z_pub_thr.py 1048576
```

**Analiza wyników:**
- Jak zmienia się throughput ze wzrostem rozmiaru?
- Jaki jest overhead dla małych wiadomości?
- Gdzie jest bottleneck (sieć/CPU)?

---

### 🔄 z_ping & z_pong

**Cel:** Test latencji (roundtrip time).

**Latencja** - czas od wysłania do otrzymania odpowiedzi.

**Wzorzec:**
```
z_ping → wysyła → z_pong
   ↑                ↓
   ←───── odpowiada ←
```

**Jak używać:**

Terminal 1 - Pong (odpowiada):
```bash
python3 z_pong.py
```

Terminal 2 - Ping (mierzy):
```bash
python3 z_ping.py
```

**Co zobaczysz:**
```
Roundtrip time: 1.234 ms
Roundtrip time: 1.156 ms
Roundtrip time: 1.298 ms
```

**Dlaczego ważne w robotyce:**
- Sterowanie real-time wymaga <10ms latencji
- Teleoperation (zdalnie sterowanie) - człowiek nie toleruje >100ms
- Koordynacja multi-robot - latencja wpływa na synchronizację

**Analiza:**
- Minimum - best case (sieć bez obciążenia)
- Średnia - typowa latencja
- Maximum - worst case (jitter, opóźnienia)

---

### 🗑️ z_delete

**Cel:** Wysyła wiadomość DELETE (usunięcie danych).

**Zenoh Sample Kinds:**
- `PUT` - dodanie/aktualizacja wartości
- `DELETE` - usunięcie wartości

**Kiedy używać:**
- Usunięcie danych ze storage
- Sygnalizacja, że zasób nie jest już dostępny
- Cleanup (czyszczenie) przestarzałych danych

**Typowe użycie:**

```bash
python3 z_delete.py -k demo/example/test
```

**Scenariusz:**

```bash
# 1. Ustaw wartość
python3 z_put.py -k robot/active -p 'true'

# 2. Usuń wartość
python3 z_delete.py -k robot/active
```

**Subscriber zobaczczy:**
```
>> [Subscriber] Received DELETE ('robot/active')
```

---

### 🌐 z_liveliness, z_get_liveliness, z_sub_liveliness

**Liveness** - informacja o tym, czy node/aplikacja jest aktywna.

#### z_liveliness

**Cel:** Deklaruje token "jestem żywy".

```bash
python3 z_liveliness.py -k robot/arm/controller
```

**Dopóki program działa, token jest aktywny.**

#### z_get_liveliness

**Cel:** Sprawdza, które tokeny są aktywne (one-shot query).

```bash
python3 z_get_liveliness.py -k 'robot/**'
```

**Wynik:** lista aktywnych tokenów.

#### z_sub_liveliness

**Cel:** Subskrybuje zmiany liveness (ciągłe monitorowanie).

```bash
python3 z_sub_liveliness.py -k 'robot/**'
```

**Zobaczysz:**
```
>> Alive: robot/arm/controller
>> Dead: robot/arm/controller
```

**Zastosowanie w robotyce:**
- Health monitoring - czy moduły robota działają
- Failover - wykrywanie awarii i przełączanie na backup
- Fleet management - monitoring wielu robotów

---

### 📦 z_bytes

**Cel:** Demonstracja serializacji różnych typów danych.

**Problem:** Zenoh przesyła bajty. Jak zakodować struktury danych?

**Przykład pokrywa:**
- String
- Liczby (int, float)
- Listy
- Słowniki (JSON)
- Binarne dane (np. obrazy)

```bash
python3 z_bytes.py
```

**Nauczysz się:**
- Jak serializować dane do wysłania
- Jak deserializować otrzymane dane
- Jak radzić sobie z różnymi typami

**Praktyczne dla robotyki:**
- Wysyłanie joint positions (lista floats)
- Wysyłanie konfiguracji (JSON)
- Wysyłanie obrazów (binary)

---

### 🔒 z_pull

**Cel:** Demonstracja pull mode dla subscriber.

**Push vs Pull:**
- **Push (domyślnie):** Dane są dostarczane automatycznie (callback)
- **Pull:** Aplikacja jawnie pobiera dane, gdy jest gotowa

**Kiedy używać Pull:**
- Przetwarzanie jest wolniejsze niż publikowanie
- Chcesz kontrolować tempo odbierania
- Backpressure - zapobieganie przeciążeniu

```bash
python3 z_pull.py
```

**Praktyczne zastosowanie:**
- Przetwarzanie obrazu - pobierz następną klatkę gdy poprzednia jest przetworzona
- Expensive operations - kontrola obciążenia CPU

---

### 🧠 z_advanced_pub & z_advanced_sub

**Cel:** Zaawansowane funkcje pub/sub.

**Funkcje:**
- **Congestion control** - kontrola przeciążenia
- **Priority** - priorytetyzacja wiadomości
- **Reliability** - gwarancje dostarczenia
- **Express** - optymalizacja latencji

```bash
python3 z_advanced_pub.py
python3 z_advanced_sub.py
```

**Szczególnie ważne dla krytycznych systemów robotycznych.**

---

### 🚄 z_pub_shm & z_sub_shm

**Shared Memory (SHM)** - pamięć współdzielona.

**Dlaczego:**
- Obrazy z kamery robota = MB danych
- Kopiowanie = kosztowne
- SHM = zero-copy transfer

**Wymaga:** kompilacja z feature `shared-memory`

```bash
python3 z_pub_shm.py
python3 z_sub_shm.py
```

**Kiedy używać:**
- Duże dane (>1MB)
- Wysoka częstotliwość
- Komunikacja lokalna (ten sam host)

**Uwaga:** SHM działa tylko między procesami na tym samym komputerze.

---

## Wzorce komunikacji - podsumowanie

### 1. Pub/Sub (z_pub, z_sub)
**Kiedy:** Strumieniowanie danych, wielu odbiorców
**Przykład:** Telemetria robota, sensor data

### 2. Query/Queryable (z_get, z_queryable)
**Kiedy:** Request-response, dane na żądanie
**Przykład:** Pobierz aktualny stan, RPC

### 3. Storage (z_storage)
**Kiedy:** Przechowywanie historii, cache
**Przykład:** Ostatnie wartości sensorów, state backup

### 4. Liveness (z_liveliness)
**Kiedy:** Monitoring dostępności
**Przykład:** Health check, failover detection

---

## Najczęstsze pułapki

### 1. Zapomnienie uruchomienia receivera przed senderem

```bash
# ❌ Źle - sub uruchomiony za późno, może stracić dane
python3 z_pub.py &
sleep 5
python3 z_sub.py

# ✅ Dobrze - sub gotowy przed pub
python3 z_sub.py &
sleep 1
python3 z_pub.py
```

### 2. Nieodpowiednie key expressions

```bash
# ❌ Zbyt ogólne - dostaniesz wszystko
python3 z_sub.py -k '**'

# ✅ Konkretne - tylko to co potrzebne
python3 z_sub.py -k 'robot/sensors/**'
```

### 3. Brak timeoutów w z_get

```bash
# ❌ Może czekać w nieskończoność
python3 z_get.py -s 'robot/state'

# ✅ Z timeout
python3 z_get.py -s 'robot/state' --timeout 5.0
```

---

## Kolejne kroki

1. ✅ Uruchom podstawowe przykłady (z_info, z_pub, z_sub)
2. 🧪 Eksperymentuj z key expressions
3. 📊 Zmierz throughput i latencję
4. 🤖 Zobacz [UNITREE_G1_GUIDE.pl.md](../UNITREE_G1_GUIDE.pl.md)
5. 💻 Stwórz własną aplikację!

---

## Pomoc

Jeśli coś nie działa:
1. Sprawdź, czy zenoh-python jest zainstalowany: `pip list | grep zenoh`
2. Uruchom `z_scout.py` - czy widać router/peers?
3. Sprawdź firewall - czy porty są otwarte?
4. Zobacz logi: ustaw zmienną `RUST_LOG=debug`

```bash
RUST_LOG=debug python3 z_pub.py
```

---

**Powodzenia w nauce Zenoh! 🚀**
