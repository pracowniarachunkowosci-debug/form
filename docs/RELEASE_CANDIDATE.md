# PR #11 — lokalny kandydat do przeglądu

**Aktualny odbiór 04.11.2026:** [wydanie #14 — 16 stron, paczka, G1–G8 i rollback](LH_RELEASE_14.md). Poniżej zachowano historyczny stan PR #11.

**ARCHIWALNE po podmianie hero:** identyfikatory poniżej dotyczą poprzedniego stanu bez bombki. Nie obejmują [nowego tymczasowego preview](HERO_CONCEPT_PREVIEW.md) i nie mogą identyfikować bieżącej strony. Nie zbudowano ani nie zatwierdzono nowej paczki publikacyjnej w iteracji koncepcyjnej.

Zbudowano 03.11.2026 z czystego drzewa. **NO-GO dla publikacji**: otwarte warunki w [RELEASE_READINESS](RELEASE_READINESS.md). Paczka zawiera projekty dokumentów i obecny editorial bez produktu. Po otrzymaniu fotografii, akceptacji dokumentów lub innej zmianie strony powstanie nowe wydanie do odbioru.

| Pole | Wartość |
|---|---|
| Gałąź | `codex/lh-orange-hybrid-publication` |
| Commit źródłowy plików strony | `e3eba159198d238716784ba3529e1d0cbeda9260` |
| Stan drzewa podczas budowy | czysty (`source_dirty: false`) |
| Lokalny ZIP | `.artifacts/pracownia-form-lh.zip` |
| Rozmiar ZIP | 7 375 844 bajty |
| Pliki / suma rozmiarów przed kompresją | 55 / 7 589 135 bajtów |
| SHA-256 ZIP | `2132002db84be5bae747e731e2a25527df88c74f5b24a466f66fc2e5694a3f08` |
| SHA-256 manifestu | `995bf75d64843dfaf345a06d43484aecfbd3f9171edeabe48ee04e445397f852` |
| Zgoda na wdrożenie | brak (`deployment_authorized: false`) |

`manifest.json` zawiera ścieżkę, rozmiar i SHA-256 każdego pliku. `release.json` identyfikuje źródła i archiwum. Wszystkie trzy pliki znajdują się lokalnie w ignorowanym `.artifacts`; nie wgrano ich na hosting ani nie utworzono GitHub Release. Dokumentacja i obrazy podglądowe nie należą do zawartości ZIP.

Budowa sprawdza HTML, CRC archiwum, zestaw ścieżek oraz bajty każdego pliku względem manifestu. Dwie kolejne budowy tego samego zestawu plików (przed i po zapisaniu commitu) dały identyczny SHA-256 ZIP; finalna metryka pochodzi z czystego commitu wskazanego powyżej. Kontroler cookies i składnia JS także przeszły testy opisane w [raporcie recenzji](PR11_REVIEW_RESPONSE.md).

Osobna próba odczytu wszystkich plików przez lokalny HTTP nie została zaliczona: transfer starszego, niezmienionego `assets/hero-form.webp` zakończył się timeoutem/resetem mimo statusu 200. Integralność ZIP nie zastępuje kontroli pełnego transferu; przed publikacją wymagany jest odbiór technicznego hostingu i wszystkich zasobów. Nie przypisujemy nieustalonej przyczyny tego błędu konfiguracji LH, której jeszcze nie wdrożono.

Ta metryka jest dodana w późniejszym commicie **wyłącznie dokumentacyjnym**, aby uniknąć odwołania commitu do własnego hasha. Do odtworzenia użyć wskazanego commitu źródłowego, zachować bajty repozytorium (checkout bez konwersji `core.autocrlf`, bez formatowania HTML/JS), uruchomić `python scripts/build_release.py` i porównać hash. Rozbieżność hasha wymaga wyjaśnienia oraz ponownego odbioru, nigdy automatycznego uploadu.

Właściciel zatwierdza ostateczną wersję tekstów/zdjęć oraz **konkretny nowy commit i hash ZIP**, a dopiero osobno wykonanie fazy B. Ten zapis nie upoważnia do merge, transferu plików, DNS/SSL, rzeczywistych zapisów Brevo ani płatności.
