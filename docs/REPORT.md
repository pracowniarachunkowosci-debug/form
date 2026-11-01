# Raport zmian — GitHub #3

Data: 01.11.2026. Baza: `38e0bd9`, branch: `codex/issue-3-winter26-draft`. Wynik: projekt do akceptacji, bez merge, wdrożenia, sprzedaży i płatności.

## Aktualnie: R04 — WINTER AFTER DARK

Nowy feedback właściciela zastępuje kierunek Warm Minimal. Zachowano architekturę i zakres, a WINTER otrzymał ciemne otwarcie, światło champagne, editorial AI bez produktów i dark forest w zestawach. Jasne karty produktów kontrastują z częścią narracyjną. [Raport R04, kontrast, porównanie z produkcyjnym homepage i granice przyszłych PR-ów](R04_REVIEW.md).

Nowe screenshoty: desktop 1440 i mobile 390; dodatkowa kontrola 320/768. Nie zmieniono produkcyjnej strony głównej, dokumentów prawnych ani danych produktów w tej rewizji. Asset i prompt: [IMAGE_R04.md](IMAGE_R04.md).

## Historia: wersja 02 — Warm Minimal (niezaakceptowana wizualnie)

Po akceptacji układu i struktury zmieniono wyłącznie oprawę wizualną oraz zawartość pola hero. Tło paper `#faf8f3`, powierzchnie `#f2eee6`, ciemny tekst `#25231f` i burgund `#632d3b` jako oszczędny akcent. Sekcja zestawów, baner roboczy, stopka i dokumenty są jasne; na stronie głównej rozjaśniono tekstowe sekcje pracowni i procesu. Siatki, kolejność sekcji, fonty i breakpointy pozostały zachowane.

Zdjęcie z bombkami usunięto z hero WINTER 26. Zastępuje je neutralna typograficzna kompozycja HTML/CSS ze światłem na papierze — bez przedstawienia produktu i bez nowych zasobów zewnętrznych. Dotychczasowy plik grafiki pozostaje w historii/zasobach repo, ale nie jest ładowany przez stronę WINTER 26. Nie podmieniono go na niezweryfikowane zdjęcie modelu.

Zaktualizowano screenshoty desktop/mobile i plansze dokumentów. Ponowna kontrola 320/390/768/1440 px nie wykazała przepełnień. Zmiana nie dotyczy treści prawnych, danych produktów ani działania formularzy. PR pozostaje draft; bez publikacji.

## Co zmieniono

| Wymaganie | Wynik |
| --- | --- |
| Audyt obecnej strony | [AUDIT.md](AUDIT.md): repo, hosting, produkcja, niespójności, GA4/Brevo, KRS i kontakt; audyt zapisano przed implementacją |
| WINTER 26 | Nowy hero, KNITTED / SCULPTURAL, cztery karty: KNITTED STAR, KNITTED MEDALLION, HELIX, FULL SOFT; miejsca na zatwierdzone fotografie i dane; brak przycisku kupna |
| Język graficzny | Ivory/czerń/burgund, typografia editorial, numeracja kart, dużo światła i czytelne statusy; źródłowe karty R03A nie były dostępne w repo, więc układ jest propozycją do porównania z nimi |
| Dane i realizacja | Szkielet SKU z trzema statusami i osobnymi czasami magazyn/druk; nieznane wartości `null`; zestawy 2/4 jako projekt UI |
| Archiwum / marka | SOLIS, VINE WAVE CAST, SOLIS DISH na `koncepty.html`; NORD/STONE/KINTSUGI jako przyszłe koncepty; usunięta obietnica pierwszego preorderu i sprzeczność z sezonowością |
| Dokumenty | Sześć osobnych projektów HTML: regulamin, zwroty/reklamacje, dostawa/płatności, formularz odstąpienia, prywatność, lista premierowa |
| Dane spółki | Wspólne stopki i kontakt z nazwą, adresem, NIP, KRS/sądem, REGON i kapitałem. `.com` ujednolicone. Skrzynka, telefon i adres zwrotów jawnie do potwierdzenia |
| Odstąpienie | Standardowy druk katalogowy zachowuje 14-dniowe prawo; osobno rzeczywista personalizacja. Wzór do wydruku oraz bezpieczne lokalne demo dwóch kroków; [plan backendu](DATA_AND_WITHDRAWAL.md) |
| Stan prawny | [Źródła i wnioski](LEGAL_RESEARCH.md), w tym nowszy UC169 / odpowiedź MF z 29.09.2026; rozdzielono harmonogram projektu od obowiązującej ustawy; brak starego odnośnika ODR |
| GPSR | Miejsca na producenta, kontakt, identyfikację i bezpieczeństwo; bez niepotwierdzonych deklaracji materiałowych; QR jedynie uzupełniający |
| Prywatność | Rozdzielony stan zastanej produkcji, lokalnego draftu i przyszłego sklepu; cele, podstawy, okresy, odbiorcy/transfery i prawa; brak fikcyjnych integracji |
| SEO | Tytuły, opisy, canonical, OG; usunięte nieadekwatne schema, bez Product/Offer. `noindex, nofollow` dla draftu; pusty sitemap i osobny kandydat do akceptacji |
| Technologia | Zachowane statyczne HTML/CSS/JS. Mały generator Python stdlib ujednolica strony; brak zmiany platformy i dodanych zależności runtime |

Hero R04 używa atmosferycznej kompozycji editorial AI z igliwiem, kamieniem i wstążką, bez produktów. Karty czterech modeli mają neutralne placeholdery. Nie stworzono fikcyjnych zdjęć, cen, kolorów, nakładów ani terminów.

## Weryfikacja

- `python scripts/check.py --http`: **PASS** — 15 stron, 458 odniesień HTML, zasoby CSS, metadane, CSP, dane produktów; 42 unikalne lokalne adresy stron/zasobów zwróciły HTTP 200. Brak uszkodzonych wewnętrznych linków i kotwic.
- `node --check script.js`: **PASS**. `git diff --check`: **PASS**. Powtórne generowanie: identyczne pliki wynikowe.
- Pierwotny odbiór wspólnego układu (przed R04): [browser-checks.json](browser-checks.json): 8 stron × desktop 1440/mobile 390. Brak przepełnienia całej strony, uszkodzonych obrazów, aktywnych formularzy i zewnętrznych skryptów; widoczny nagłówek i jeden H1.
- [breakpoint-checks.json](breakpoint-checks.json): 10 stron × 320/768 px. Brak poziomego przepełnienia całej strony. Tabela polityki przewija się we własnym kontenerze.
- Przegląd wizualny zapisanych pełnych układów i fragmentów desktop/mobile. Poprawiono hero 320 px i konflikt starego cyklu preload z widocznością nagłówka/hero.
- Interakcje: menu mobile, zamknięcie Escape, akordeon danych produktu; demo odstąpienia — walidacja pustych danych, wypełnienie testowe, podsumowanie, powrót do korekty, końcowy komunikat „nic nie wysłano” i reset. Brak błędów/ostrzeżeń konsoli w końcowym przebiegu demo.
- Podstawy dostępności: semantyczne nagłówki i regiony, skip link, focus-visible, etykiety pól, powiązane komunikaty błędów, aria-expanded, obsługa klawiatury, reduced motion; treści i nawigacja mają statyczny fallback. To nie jest certyfikacja WCAG ani pełny test czytnikiem ekranu/trybu bez JS.

[Podglądy desktop/mobile](PREVIEWS.md) obejmują WINTER 26, wszystkie sześć dokumentów i stronę główną.

## Granice i ryzyka przed uruchomieniem

W review nie działają GA4/Brevo, zapisy, koszyk ani płatności. CSP blokuje połączenia, ramki i wysyłkę formularzy; skrypty i zasoby są lokalne. Demo nie ma backendu i nie przyjmuje rzeczywistych oświadczeń. Nie wykonano prób płatności, wysyłek maili ani zgłoszeń do produkcyjnych formularzy.

Audyt produkcyjnej analityki objął kod oraz stan DOM przed decyzją i po odmowie zgody. Nie akceptowano analityki, nie sporządzono pełnego HAR i nie potwierdzono konfiguracji kont GA4/Brevo. Testy HTTP dotyczą lokalnych odnośników; nie stanowią gwarancji dostępności zewnętrznych stron w przyszłości. Publiczne dane KRS zweryfikowano, lecz adres zwrotów i obsługa skrzynki wymagają decyzji właściciela.

**Nie wdrażać draftu wprost na produkcję**: zawiera placeholdery, noindex, pusty sitemap oraz wyłączone integracje. [BLOCKERS BEFORE LAUNCH](BLOCKERS_BEFORE_LAUNCH.md) określa warunki osobnego PR wdrożeniowego. Dokumenty wymagają recenzji prawnej; stan UC169 należy ponownie sprawdzić przed startem.

Oba zapowiedziane pakiety (UI oraz dokumenty/informacje) są zebrane w jednym draft PR dla spójnej oceny. Produkcyjne pliki na `main` i ustawienia GitHub Pages nie są zmieniane przez to zadanie. Nie dodano workflow automatycznej publikacji.
