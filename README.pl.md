# Eclipse Zenoh - Python API

<img src="https://raw.githubusercontent.com/eclipse-zenoh/zenoh/main/zenoh-dragon.png" height="150">

[![CI](https://github.com/eclipse-zenoh/zenoh-python/workflows/CI/badge.svg)](https://github.com/eclipse-zenoh/zenoh-python/actions?query=workflow%3A%22CI%22)
[![Documentation Status](https://readthedocs.org/projects/zenoh-python/badge/?version=latest)](https://zenoh-python.readthedocs.io/en/latest/?badge=latest)
[![Discussion](https://img.shields.io/badge/discussion-on%20github-blue)](https://github.com/eclipse-zenoh/roadmap/discussions)
[![Discord](https://img.shields.io/badge/chat-on%20discord-blue)](https://discord.gg/2GJ958VuHs)
[![License](https://img.shields.io/badge/License-EPL%202.0-blue)](https://choosealicense.com/licenses/epl-2.0/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Co to jest Eclipse Zenoh?

Eclipse Zenoh to nowoczesny protokół komunikacyjny typu "Zero Overhead" łączący w sobie:
- **Pub/Sub** (Publisher/Subscriber) - wzorzec publikuj/subskrybuj
- **Store/Query** - przechowywanie i odpytywanie danych
- **Compute** - obliczenia rozproszone

### Dlaczego Zenoh?

Zenoh (wymawiane _/zeno/_) unifikuje:
- **Dane w ruchu** (data in motion) - strumieniowanie danych w czasie rzeczywistym
- **Dane w spoczynku** (data at rest) - przechowywanie danych
- **Obliczenia** (computations) - przetwarzanie rozproszone

Zenoh łączy tradycyjny model pub/sub z geograficznie rozproszonymi magazynami danych, zapytaniami i obliczeniami, zachowując jednocześnie wydajność czasową i przestrzenną znacznie przewyższającą inne popularne rozwiązania.

**Więcej informacji:**
- Strona projektu: [zenoh.io](http://zenoh.io)
- Plan rozwoju: [roadmap](https://github.com/eclipse-zenoh/roadmap)

---

## Python API

To repozytorium zawiera wiązania Pythona (Python bindings) oparte na głównej [implementacji Zenoh napisanej w języku Rust](https://github.com/eclipse-zenoh/zenoh).

**Dla czego Python?**
Python jest popularnym językiem w robotyce i IoT ze względu na:
- Prostotę składni i łatwość nauki
- Bogaty ekosystem bibliotek (NumPy, OpenCV, TensorFlow)
- Szybkie prototypowanie i testowanie
- Doskonałą integrację z systemami embedded

---

## Jak zainstalować

### Instalacja ze źródła PyPI (zalecana dla użytkowników)

Biblioteka Eclipse zenoh-python jest dostępna na [Pypi.org](https://pypi.org/project/eclipse-zenoh/).
Zainstaluj najnowszą wersję używając `pip` w [środowisku wirtualnym](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/):

```bash
pip install eclipse-zenoh
```

#### ⚠️ UWAGA: Wymagania dla kompilacji ze źródeł

zenoh-python jest rozwijany w języku Rust. Na Pypi.org udostępniamy:
- **Prekompilowane pakiety** (binary wheels) dla najpopularniejszych platform:
  - Linux x86_64, i686, ARM
  - MacOS universal2
  - Windows amd64
- **Pakiet źródłowy** (source distribution) dla innych platform

Aby `pip` mógł zbudować pakiet ze źródeł, wymagane są:

1. **pip w wersji 19.3.1 lub nowszej** (dla pełnego wsparcia PEP 517)
   ```bash
   sudo pip install --upgrade pip
   ```

2. **Zainstalowany Rust toolchain** (instrukcje na [rustup.rs](https://rustup.rs/))
   - Rust to nowoczesny język systemowy gwarantujący bezpieczeństwo pamięci
   - Toolchain zawiera kompilator i narzędzia budowania

### Wspierane wersje Pythona i platformy

zenoh-python został przetestowany z wersjami Python:
- 3.8, 3.9, 3.10, 3.11, 3.12

Biblioteka opiera się na [zenoh Rust API](https://github.com/eclipse-zenoh/zenoh/tree/main/zenoh), który wymaga pełnej biblioteki standardowej `std`. 

Zobacz listę wspieranych platform: [Rust Platform Support](https://doc.rust-lang.org/nightly/rustc/platform-support.html)

### Włączanie dodatkowych funkcji Zenoh

Niektóre funkcje biblioteki Rust są domyślnie wyłączone. Aby je włączyć (np. `shared-memory` dla pamięci współdzielonej), wykonaj:

```bash
pip install eclipse-zenoh --no-binary :all: --config-settings build-args="--features=zenoh/shared-memory"
```

**Shared Memory** to zaawansowana funkcja pozwalająca na:
- Wymianę danych bez kopiowania między procesami
- Znaczne zwiększenie wydajności dla dużych obiektów (np. obrazy z kamer)
- Krytyczna dla aplikacji czasu rzeczywistego w robotyce

---

## Jak zbudować ze źródeł

### Wymagania:

- **Python >= 3.8**
- **pip >= 19.3.1**
- **[Rust i Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html)**

Jeśli Rust jest już zainstalowany, upewnij się, że jest aktualny:

```bash
rustup update
```

### Zalecane: Budowanie w środowisku wirtualnym

**Dlaczego środowisko wirtualne?**
- Izolacja projektu od systemowych pakietów Pythona
- Unikanie konfliktów wersji bibliotek
- Łatwe zarządzanie zależnościami projektu
- Możliwość pracy nad wieloma projektami z różnymi wymaganiami

#### Krok 1: Utworzenie i aktywacja środowiska wirtualnego

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# lub
.venv\Scripts\activate     # Windows
```

**Co się dzieje:**
- `python3 -m venv .venv` - tworzy nowe środowisko w katalogu `.venv`
- `source .venv/bin/activate` - aktywuje środowisko (zmienia PATH)

#### Krok 2: Instalacja wymagań deweloperskich

```bash
pip install -r requirements-dev.txt
```

**Co zawiera requirements-dev.txt:**
- `maturin` - narzędzie do budowania pakietów Rust dla Pythona
- Narzędzia do testowania i formatowania kodu

#### Krok 3: Budowanie i instalacja w trybie deweloperskim

```bash
maturin develop --release
```

**Co robi `maturin develop`:**
- Kompiluje kod Rust w trybie release (zoptymalizowany)
- Instaluje pakiet w trybie "editable" (zmiany w kodzie są od razu widoczne)
- Łączy kod Rust z Pythonem

**Flaga `--release`:**
- Włącza optymalizacje kompilatora
- Kod jest szybszy, ale kompilacja trwa dłużej
- Używaj dla testów wydajnościowych

#### Krok 4: Uruchomienie przykładów

```bash
python examples/z_info.py
```

#### Dezaktywacja środowiska

```bash
deactivate
```

### Alternatywnie: Budowanie bez środowiska wirtualnego

**UWAGA:** Ta metoda nie jest zalecana i może prowadzić do konfliktów z systemowymi pakietami.

#### Krok 1: Instalacja wymagań deweloperskich

```bash
pip install -r requirements-dev.txt
```

#### Krok 2: Konfiguracja PATH

Upewnij się, że `maturin` jest dostępny w PATH (na Ubuntu 20.04 domyślnie: `$HOME/.local/bin/maturin`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

#### Krok 3: Budowanie pakietu wheel

```bash
maturin build --release
```

**Pakiet wheel:**
- Format dystrybucji pakietów Pythona (.whl)
- Zawiera prekompilowany kod
- Szybka instalacja bez kompilacji

#### Krok 4: Instalacja zbudowanego pakietu

```bash
pip install ./target/wheels/*.whl --break-system-packages
```

**Flaga `--break-system-packages`:**
- Pozwala instalować pakiety poza środowiskiem wirtualnym
- Używaj ostrożnie - może nadpisać systemowe pakiety
- Zalecamy sprawdzenie wersji pip i python:

```bash
pip --version      # Pokazuje którą wersję Pythona używa pip
python3 --version  # Pokazuje wersję python3
```

Jeśli wersje się różnią, użyj:
```bash
python3 -m pip install ./target/wheels/*.whl
```

#### Krok 5: Uruchomienie przykładów

```bash
python3 examples/z_info.py
```

---

## Budowanie dokumentacji

### Po co dokumentacja lokalna?
- Przeglądanie offline
- Szybkie odniesienia podczas kodowania
- Zrozumienie API bez połączenia z internetem

### Kroki budowania:

#### 1. Upewnij się, że zenoh-python jest zainstalowany

Postępuj zgodnie z instrukcjami budowania powyżej.

#### 2. Zainstaluj wymagania dla dokumentacji

```bash
pip install -r docs/requirements.txt
```

#### 3. Zbuduj dokumentację HTML

```bash
cd docs
make html
```

**Co robi `make html`:**
- Parsuje docstringi z kodu Pythona
- Generuje strony HTML ze strukturą nawigacji
- Tworzy indeks wyszukiwania

#### 4. Otwórz dokumentację

```bash
# macOS
open _build/html/index.html

# Linux
xdg-open _build/html/index.html

# lub ręcznie w przeglądarce:
# docs/_build/html/index.html
```

**Dokumentacja online:** [zenoh-python.readthedocs.io](https://zenoh-python.readthedocs.io/)

---

## Uruchamianie przykładów

### Opcjonalnie: Instalacja Zenoh Router

Zenoh Router to centralny punkt komunikacji (opcjonalny):
- **Bez routera:** komunikacja peer-to-peer przez multicast UDP
- **Z routerem:** 
  - Centralizacja komunikacji
  - Lepsza wydajność w dużych sieciach
  - Możliwość połączeń przez WAN
  - Zaawansowane funkcje (storage, query routing)

Instrukcje instalacji: [zenoh installation guide](https://github.com/eclipse-zenoh/zenoh/?tab=readme-ov-file#how-to-install-it)

### Uruchomienie przykładów

Szczegółowe instrukcje znajdują się w: [examples/README.pl.md](examples/README.pl.md)

```bash
# Przykład podstawowy - informacje o sesji
python examples/z_info.py

# Przykład publisher - publikowanie danych
python examples/z_pub.py -k demo/example/test -p 'Hello World'

# Przykład subscriber - odbieranie danych
python examples/z_sub.py -k 'demo/example/**'
```

**Uwaga dla Docker:**
Jeśli Zenoh Router działa w kontenerze Docker, dodaj parametr `-e tcp/localhost:7447`:
- Docker nie wspiera multicast UDP
- Wymusza komunikację TCP z konkretnym adresem
- Wyłącza automatyczne odkrywanie (scouting)

```bash
python examples/z_pub.py -e tcp/localhost:7447
```

---

## Zastosowanie w robotyce - Unitree G1 EDU-U6

Zenoh jest idealnym rozwiązaniem dla komunikacji w systemach robotycznych, szczególnie dla robotów humanoidalnych takich jak Unitree G1 EDU-U6.

### Dlaczego Zenoh w robotyce?

1. **Niska latencja** - krytyczna dla sterowania w czasie rzeczywistym
2. **Elastyczne topologie** - peer-to-peer lub z routerem
3. **Efektywność** - minimalne zużycie zasobów
4. **Skalowalność** - od pojedynczego robota do floty
5. **Geo-distributed** - komunikacja przez WAN

### Przykłady zastosowań z robotem Unitree G1:

- **Telemetria robota:** Publikowanie pozycji stawów, czujników IMU, stanu baterii
- **Sterowanie:** Wysyłanie komend ruchu do robota
- **Przetwarzanie obrazu:** Strumieniowanie obrazu z kamer robota
- **Koordynacja:** Komunikacja między wieloma robotami lub stacjami kontrolnymi

**Zobacz:** [UNITREE_G1_GUIDE.pl.md](UNITREE_G1_GUIDE.pl.md) dla szczegółowego przewodnika zastosowania Zenoh z robotem Unitree G1.

---

## Następne kroki

1. ✅ Zainstaluj zenoh-python
2. 📖 Przeczytaj [examples/README.pl.md](examples/README.pl.md)
3. 🚀 Uruchom przykłady (z_pub.py, z_sub.py)
4. 🤖 Zapoznaj się z [przewodnikiem Unitree G1](UNITREE_G1_GUIDE.pl.md)
5. 💻 Rozpocznij własny projekt!

---

## Wsparcie i społeczność

- 📚 **Dokumentacja:** [zenoh-python.readthedocs.io](https://zenoh-python.readthedocs.io/)
- 💬 **Discord:** [discord.gg/2GJ958VuHs](https://discord.gg/2GJ958VuHs)
- 🐛 **Issues:** [GitHub Issues](https://github.com/eclipse-zenoh/zenoh-python/issues)
- 🗺️ **Roadmap:** [GitHub Discussions](https://github.com/eclipse-zenoh/roadmap/discussions)

---

## Licencja

Eclipse zenoh-python jest dostępny na podwójnej licencji:
- Eclipse Public License 2.0
- Apache License 2.0

Możesz wybrać licencję, która lepiej odpowiada Twoim potrzebom.
