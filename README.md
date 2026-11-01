# Pracownia Form — WINTER 26 / review

Wersja robocza do [issue #3](https://github.com/pracowniarachunkowosci-debug/form/issues/3). **Bez sprzedaży, płatności i publikacji. Nie wdrażać tej gałęzi.**

Statyczne HTML/CSS/JS, bez migracji platformy i bez zależności npm. Python 3 służy wyłącznie do generowania stron i kontroli.

```powershell
python scripts/build.py
python scripts/check.py
node --check script.js
python -m http.server 8763 --bind 127.0.0.1
```

Otwórz lokalnie `http://127.0.0.1:8763/winter-26.html`. Zatrzymaj serwer przez Ctrl+C. Nie uruchamiaj serwera na publicznym interfejsie. Podgląd nie wymaga kluczy, bazy danych ani kont dostawców.

Gdy lokalny serwer działa, `python scripts/check.py --http` dodatkowo sprawdza odpowiedzi HTTP wszystkich używanych lokalnych stron i zasobów.

- [R04 WINTER AFTER DARK — podglądy i porównanie z homepage](docs/R04_REVIEW.md)
- [Raport zmian i weryfikacji](docs/REPORT.md)
- [Audyt przed zmianami](docs/AUDIT.md)
- [Podglądy desktop/mobile](docs/PREVIEWS.md)
- [BLOCKERS BEFORE LAUNCH](docs/BLOCKERS_BEFORE_LAUNCH.md)
- [Podstawy prawne i stan prac legislacyjnych](docs/LEGAL_RESEARCH.md)
- [Dane wariantów i plan funkcji odstąpienia](docs/DATA_AND_WITHDRAWAL.md)

## Edycja

Treść sześciu dokumentów znajduje się w `content/*.html`; wspólna nawigacja, stopka, metadane i szablon WINTER w `scripts/build.py`. Dane kolekcji: `data/winter-26.json`. Po zmianie źródeł uruchom build i dołącz wygenerowane HTML do commita. Strona główna i strony przyszłych kolekcji zachowują swój HTML; generator normalizuje ich wspólną oprawę. Kolejne uruchomienie generatora nie zmienia wyniku.

`review.css` zawiera wspólny layout i dokumenty, `winter-26.css` kolekcję, istniejący `styles.css` pozostałe widoki. `script.js` obsługuje jedynie lokalne interakcje. Zrzuty są dowodem ręcznej kontroli przeglądarkowej, nie są odtwarzane przez `check.py`.

Wszystkie strony mają `noindex, nofollow`; `sitemap.xml` jest celowo pusty. `docs/sitemap-after-approval.xml` jest kandydatem do osobnego wdrożenia po zatwierdzeniu. Canonical i OG wskazują docelowe adresy `.com`, lecz nie oznacza to publikacji. Generator wymaga flag review; zmiana samej flagi nie uruchamia sklepu.

Hosting produkcyjny pozostaje GitHub Pages z `main`. Nie dodano workflow wdrożeniowego ani projektu w innym hostingu. Nie łączyć tego PR bez osobnej decyzji o publikacji i rozstrzygnięcia blokerów.
