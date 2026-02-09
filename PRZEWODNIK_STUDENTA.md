# 🎓 Materiały dla Studentów Politechniki Rzeszowskiej

## 📚 Przewodnik po polskich zasobach

To repozytorium zostało rozszerzone o polskojęzyczne materiały edukacyjne dla studentów pracujących z robotem **Unitree G1 EDU-U6**.

---

## 🗺️ Mapa zasobów

### 1. Główna dokumentacja

📖 **[README.pl.md](README.pl.md)**
- Tłumaczenie głównego README na język polski
- Instrukcje instalacji i konfiguracji
- Wprowadzenie do Zenoh
- FAQ i rozwiązywanie problemów

### 2. Przewodnik po przykładach

📚 **[examples/README.pl.md](examples/README.pl.md)**
- Szczegółowy opis wszystkich przykładów Zenoh
- Instrukcje uruchamiania
- Wyjaśnienie wzorców komunikacji (Pub/Sub, Query/Queryable)
- Zadania i ćwiczenia dla studentów

### 3. Przewodnik dla robota Unitree G1

🤖 **[UNITREE_G1_GUIDE.pl.md](UNITREE_G1_GUIDE.pl.md)**
- Zastosowanie Zenoh w robotyce humanoidalnej
- Architektura systemu dla Unitree G1
- Hierarchia kluczy (key expressions)
- Praktyczne przykłady kodu
- Optymalizacje i dobre praktyki

### 4. Przykłady z komentarzami edukacyjnymi

📝 **[examples/*.pl.py](examples/)**
- `z_pub.pl.py` - Publisher z rozbudowanymi komentarzami po polsku
- `z_sub.pl.py` - Subscriber z wyjaśnieniami krok po kroku
- `z_queryable.pl.py` - Queryable z przykładami użycia

Każdy plik zawiera:
- Szczegółowe komentarze wyjaśniające każdy krok
- Przykłady użycia
- Zadania dla studentów
- FAQ i wzorce projektowe

### 5. Kompletne przykłady dla robota

🤖 **[examples/robot_unitree_g1/](examples/robot_unitree_g1/)**

Gotowe do uruchomienia przykłady symulujące system robota:

| Plik | Opis | Wzorzec Zenoh |
|------|------|---------------|
| `robot_telemetry_publisher.py` | Publikowanie telemetrii robota | Publisher |
| `robot_motion_controller.py` | Kontroler ruchu | Subscriber |
| `operator_station.py` | Stacja operatorska | Put (komendy) |
| `robot_config_service.py` | Serwis konfiguracji | Queryable |
| `health_monitor.py` | Monitor zdrowia systemu | Liveness |

Zobacz **[examples/robot_unitree_g1/README.md](examples/robot_unitree_g1/README.md)** dla instrukcji.

---

## 🚀 Szybki start dla studentów

### Krok 1: Instalacja

```bash
# Zainstaluj zenoh-python (w środowisku wirtualnym)
python3 -m venv .venv
source .venv/bin/activate
pip install eclipse-zenoh
```

### Krok 2: Podstawy Zenoh

1. **Przeczytaj wprowadzenie:** [README.pl.md](README.pl.md)
2. **Zapoznaj się z przykładami:** [examples/README.pl.md](examples/README.pl.md)
3. **Uruchom pierwszy przykład:**
   ```bash
   # Terminal 1 - Subscriber
   cd examples
   python3 z_sub.pl.py
   
   # Terminal 2 - Publisher
   python3 z_pub.pl.py
   ```

### Krok 3: Robot Unitree G1

1. **Przeczytaj przewodnik:** [UNITREE_G1_GUIDE.pl.md](UNITREE_G1_GUIDE.pl.md)
2. **Uruchom symulację systemu robota:**
   ```bash
   cd examples/robot_unitree_g1
   
   # Terminal 1 - Monitor
   python3 health_monitor.py
   
   # Terminal 2 - Kontroler
   python3 robot_motion_controller.py
   
   # Terminal 3 - Telemetria
   python3 robot_telemetry_publisher.py
   
   # Terminal 4 - Stacja operatorska
   python3 operator_station.py
   ```

### Krok 4: Eksperymenty

- Modyfikuj przykłady
- Twórz własne aplikacje
- Integruj z prawdziwym robotem

---

## 📖 Kolejność nauki (zalecana)

### Tydzień 1: Podstawy Zenoh

1. ✅ Instalacja i konfiguracja
2. ✅ Przeczytanie [README.pl.md](README.pl.md)
3. ✅ Uruchomienie `z_info.py` i `z_scout.py`
4. ✅ Przeczytanie i uruchomienie `z_pub.pl.py` i `z_sub.pl.py`

**Cel:** Zrozumienie podstawowego wzorca Pub/Sub

### Tydzień 2: Zaawansowane wzorce

1. ✅ Przeczytanie [examples/README.pl.md](examples/README.pl.md)
2. ✅ Query/Queryable: `z_get.py` + `z_queryable.pl.py`
3. ✅ Storage: `z_storage.py`
4. ✅ Liveness: `z_liveliness.py`, `z_get_liveliness.py`

**Cel:** Poznanie wszystkich wzorców komunikacji

### Tydzień 3: Robot Unitree G1

1. ✅ Przeczytanie [UNITREE_G1_GUIDE.pl.md](UNITREE_G1_GUIDE.pl.md)
2. ✅ Uruchomienie wszystkich przykładów z `robot_unitree_g1/`
3. ✅ Zrozumienie architektury systemu
4. ✅ Modyfikacja przykładów (dodanie własnych funkcji)

**Cel:** Praktyczne zastosowanie Zenoh w robotyce

### Tydzień 4: Własny projekt

1. ✅ Zaprojektowanie własnej aplikacji
2. ✅ Implementacja z wykorzystaniem poznanych wzorców
3. ✅ Testowanie i debugowanie
4. ✅ (Opcjonalnie) Integracja z prawdziwym robotem

**Cel:** Samodzielne tworzenie aplikacji z Zenoh

---

## 🎯 Zadania projektowe (propozycje)

### Projekt 1: Wizualizacja w czasie rzeczywistym
**Poziom:** Średni

Stwórz aplikację wizualizującą pozycję robota w czasie rzeczywistym:
- Odbieraj telemetrię z `robot/g1/state/pose`
- Rysuj pozycję na wykresie 2D (matplotlib lub pygame)
- Wyświetlaj trajektorię (historię pozycji)
- Dodaj wskaźniki baterii, prędkości

**Wykorzystane wzorce:** Subscriber

### Projekt 2: Sterowanie z joysticka
**Poziom:** Średni-Zaawansowany

Zaimplementuj sterowanie robotem przez joystick:
- Odczyt danych z joysticka (pygame lub inputs)
- Mapowanie osi joysticka na komendy ruchu
- Publikowanie komend do `robot/g1/commands/motion/walk`
- Dodanie przycisków bezpieczeństwa (dead man's switch)

**Wykorzystane wzorce:** Publisher

### Projekt 3: System logowania i playback
**Poziom:** Zaawansowany

Stwórz system do nagrywania i odtwarzania sesji:
- Subskrybuj wszystkie dane (`robot/g1/**`)
- Zapisuj do pliku (CSV, JSON, lub SQLite)
- Implementuj playback (odtwarzanie nagrania)
- Dodaj GUI do przeglądania nagrań

**Wykorzystane wzorce:** Subscriber, Publisher, Storage

### Projekt 4: Dashboard webowy
**Poziom:** Zaawansowany

Webowy panel kontrolny dla robota:
- Backend: Flask + Zenoh Python
- Frontend: HTML/CSS/JavaScript
- Real-time updates (WebSockets lub Server-Sent Events)
- Wyświetlanie telemetrii, wysyłanie komend, monitoring

**Wykorzystane wzorce:** Wszystkie

### Projekt 5: Multi-robot coordination
**Poziom:** Bardzo zaawansowany

Koordynacja wielu robotów:
- System dla 2+ robotów (symulowanych)
- Każdy robot ma własną hierarchię kluczy
- Centralny koordynator planuje zadania
- Wykrywanie i unikanie kolizji

**Wykorzystane wzorce:** Pub/Sub, Query/Queryable, Liveness

---

## 🆘 Pomoc i wsparcie

### Gdzie szukać pomocy?

1. **W tym repozytorium:**
   - README i przewodniki zawierają FAQ
   - Przykłady zawierają rozbudowane komentarze
   - Issues na GitHubie dla problemów

2. **Społeczność Zenoh:**
   - Discord: https://discord.gg/2GJ958VuHs
   - Discussions: https://github.com/eclipse-zenoh/roadmap/discussions
   - Dokumentacja: https://zenoh.io/docs/

3. **Prowadzący zajęcia:**
   - Pytania dot. robota Unitree G1
   - Pomoc z projektami
   - Konsultacje

### Najczęstsze problemy

**Problem:** Przykłady się nie widzą (subscriber nie otrzymuje danych)
- **Rozwiązanie:** Sprawdź firewall, uruchom z_scout.py, zobacz [README.pl.md](README.pl.md) sekcja troubleshooting

**Problem:** Import error: No module named 'zenoh'
- **Rozwiązanie:** Zainstaluj zenoh-python: `pip install eclipse-zenoh`

**Problem:** Wysokie opóźnienia
- **Rozwiązanie:** Zobacz [UNITREE_G1_GUIDE.pl.md](UNITREE_G1_GUIDE.pl.md) sekcja optymalizacje

---

## 📝 Notki

### Oryginalne przykłady vs. Polskie wersje

- **Oryginalne (`z_pub.py`, `z_sub.py`, etc.):** Kod produkcyjny, bez komentarzy
- **Polskie (`z_pub.pl.py`, `z_sub.pl.py`, etc.):** Wersje edukacyjne z rozbudowanymi komentarzami

Oba zestawy są funkcjonalnie identyczne. Używaj polskich wersji do nauki, oryginalnych jako referencję.

### Struktura komentarzy

Przykłady z rozszerzonymi komentarzami zawierają:
- 📘 **Docstringi** - opis funkcji i modułów
- 💡 **Komentarze inline** - wyjaśnienia linijka po linijce  
- 📚 **Sekcje edukacyjne** - zadania, FAQ, wzorce projektowe
- ⚠️ **Ostrzeżenia** - częste pułapki i jak ich unikać

---

## ✅ Checklist dla studentów

Przed zakończeniem kursu powinieneś umieć:

- [ ] Wyjaśnić czym jest Zenoh i kiedy go używać
- [ ] Zainstalować i skonfigurować zenoh-python
- [ ] Uruchomić i zmodyfikować przykłady Pub/Sub
- [ ] Zaimplementować Query/Queryable
- [ ] Używać Liveness dla monitoringu
- [ ] Zaprojektować hierarchię kluczy dla aplikacji
- [ ] Zbudować kompletny system komunikacyjny dla robota
- [ ] Debugować problemy z komunikacją Zenoh
- [ ] Zoptymalizować wydajność (throughput, latencja)
- [ ] Stworzyć własny projekt wykorzystujący Zenoh

---

## 🎓 Dodatkowe zasoby

### Dokumentacja techniczna

- **Zenoh Concepts:** https://zenoh.io/docs/manual/abstractions/
- **Python API Reference:** https://zenoh-python.readthedocs.io/
- **Zenoh Protocol:** https://zenoh.io/docs/overview/protocol/

### Tutoriale wideo

- **Zenoh YouTube:** https://www.youtube.com/@ZenohProject
- **Getting Started with Zenoh:** Szukaj na YouTube

### Artykuły naukowe

- Zenoh white papers: https://zenoh.io/resources/
- Research publications używające Zenoh

### Inne projekty

- **zenoh-pico:** Zenoh dla embedded (C)
- **zenoh-c:** Zenoh bindings dla C
- **ROS 2 DDS Bridge:** Integracja Zenoh z ROS 2

---

**Powodzenia w nauce! 🚀🤖**

*Materiały przygotowane dla studentów Politechniki Rzeszowskiej w ramach kursu robotyki z robotem Unitree G1 EDU-U6.*
