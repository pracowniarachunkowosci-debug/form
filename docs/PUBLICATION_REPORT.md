# Raport przygotowania publikacji — hybrydowy R04 / LH Orange

3 listopada 2026. **Draft do przeglądu, bez wdrożenia.** Realizacja fazy A z [PR #10](https://github.com/pracowniarachunkowosci-debug/form/pull/10#issuecomment-6606701517). [Audyt DNS/LH, migracja, rollback i warunki wdrożenia](LH_ORANGE_MIGRATION.md).

## Zakres zmiany

- Osobna gałąź `codex/lh-orange-hybrid-publication` z aktualnego `main` (`38e0bd9`). Inne gałęzie PR pozostają bez zmian.
- Zatwierdzona hybryda: ciemny hero/header/intro R04, neutralne karty na porcelain/stone, ciemne CTA, ciemne zestawy i stopka. Bez nowych wariantów projektu.
- Integracja produkcyjnego HTML i wspólnego `script.js`: nie przeniesiono testowego `noindex`, CSP blokującego formularze, pustego identyfikatora GA ani mocków z `previews/lean-pilot`.
- Warstwa R04 i zoptymalizowane grafiki pochodzą z przygotowania PR #5 (`f97fcd6`); zatwierdzone style kart i neutralna paleta z PR #10 (`1ade238`). Te PR nie zostały zmodyfikowane ani scalone. Kod połączono na nowej gałęzi na bazie `main`.
- Hero to podpisany editorial AI bez produktów. Cztery karty mają jawne miejsca na fotografie, jeden status na kartę, CTA do rzeczywistej listy, informację o dostawie przed CTA i rozwijane informacje o identyfikacji/bezpieczeństwie. Bez cen, koszyka, wyboru wariantu, checkoutu i płatności.
- `index.html`: doprecyzowanie zapowiedzi WINTER i braku zobowiązania zakupowego; link do prywatności przy formularzu. **Cały element `<form>` Brevo jest identyczny jak w main po normalizacji końców linii.** Endpoint, pola, wymagane zgody i zewnętrzny skrypt nie zostały zastąpione.
- Naprawione nieistniejące kotwice `#manifest`/`#wykonczenia` → istniejące `#pracownia`/`#materialy`; mobilne menu kontaktu, prywatności i zasad premiery podłączone do istniejącego JS. Usunięto pozorny odnośnik Instagram „Wkrótce” i odwołania do nieistniejących faviconów; zachowano SVG.
- W prywatności poprawiono kontakt `.com`, fakty o już używanym Brevo i analityce po zgodzie oraz dane administratora wskazanego przez właściciela (ALEO, porównane z API KRS). Te same dane identyfikują sprzedawcę w WINTER. Nie dodano rachunku bankowego ani danych osób z zarządu.
- Wspólne `script.js`, `styles.css`, `robots.txt`, `sitemap.xml` nie zmieniły zachowania ani treści. Kontrola porównuje je z bazą. Niezmienione linie starszych HTML zachowują oryginalne zakończenia wierszy.

## Wyniki weryfikacji

| Kontrola | Wynik / granice |
|---|---|
| `python scripts/check_publication.py` | PASS: 10 HTML, 258 lokalnych odnośników/zasobów, kotwice, unikalne ID, jeden H1, alt, JSON-LD, zachowanie formularza/runtime/GA/cookies, brak blokad testowych i płatności WINTER |
| `node scripts/check_consent.cjs` | PASS: domyślna odmowa, odrzucenie i zapamiętana odmowa, akceptacja i zapamiętana akceptacja, brak podwójnego ładowania; wykonanie w VM bez sieci |
| HTTP lokalnego wydania | PASS: wszystkie 55 plików paczki odpowiadają 200; nie jest to test konfiguracji LH |
| Desktop 1440×1000 | Hero AVIF ładuje się, przejście do kolekcji działa, neutralne karty i kontrastowe CTA; podglądy niżej |
| Mobile 390×844 i 320×740 | Bez poziomego overflow; jedna kolumna kart; czytelne CTA. Test WINTER menu open/close/Escape; Enter otwiera i zamyka szczegóły |
| Menu kontakt/prywatność | PASS w przeglądarce: `aria-expanded` false→true→false po Escape. Zasady premiery objęte kontrolą ID/odsyłaczy, bez osobnego pełnego testu ekranowego |
| Newsletter | CTA karty prowadzi do `index.html#preorder`; wymagane e-mail i zgoda, nieprawidłowy e-mail rozpoznawany, wybór zainteresowania zapisuje ukryte pole. Test bez POST; publiczny endpoint Brevo dostępny. Double opt-in i dostarczenie wymagają kontrolowanego testu właściciela |
| SEO | WINTER ma canonical domeny docelowej, index/follow, OG/Twitter, CollectionPage/BreadcrumbList, bez fikcyjnych Product/Offer. Istniejący noindex stron potwierdzenia zapisu pozostaje celowy |
| Dostępność | Semantyka/alt/H1/ID sprawdzone automatycznie; menu i details klawiaturą. Tekst charcoal/porcelain 13,84:1; muted/stone 5,39:1; muted/porcelain 6,31:1. PF w placeholderze jest dekoracyjne i aria-hidden. Nie wykonano pełnego audytu WCAG ani testów czytnikiem ekranu |
| `git -c core.whitespace=cr-at-eol diff --check` | PASS; repozytorium zawiera starsze pliki CRLF |

Testy wykonane lokalnie w Chrome. Nie symulowano słabej sieci ani nie mierzono terenowych Core Web Vitals; brak deklaracji wyniku Lighthouse. Wydajność hero potwierdzono przez dobór źródła AVIF i rozmiary plików.

## Hero i paczka

| Szerokość | AVIF, bajty | WebP, bajty |
|---|---:|---:|
| 480 | 11 776 | 19 912 |
| 768 | 24 798 | 43 390 |
| 1024 | 39 536 | 68 020 |
| 1536 | 69 746 | 123 402 |

Social JPG 1200×800: 136 804 bajty. `<picture>` preferuje AVIF, ma WebP fallback, `srcset`, `sizes`, wymiary i `fetchpriority="high"`; bez lazy loading hero. Rozmiar 1024 AVIF został zaobserwowany przy desktop 1440. Jedno źródło obrazu, bez generowania nowej kompozycji.

`python scripts/build_release.py` tworzy tylko lokalne `.artifacts/pracownia-form-lh.zip` i manifest ścieżek, rozmiarów oraz SHA-256. Około **7,6 MB nieskompresowanych danych**, daleko poniżej przydziału WWW 1000 MB. W paczce znajdują się również dotychczasowe zasoby pozostałych kolekcji. `.artifacts` nie trafia do Git; brak automatyzacji uploadu, DNS lub deploy. Przed rzeczywistym wdrożeniem zbudować paczkę ponownie z zatwierdzonego commitu i zapisać jej hash.

## Podglądy

Desktop — hero:

![Desktop hero 1440](previews/desktop-hero.jpg)

Desktop — przejście do neutralnych kart:

![Desktop karty 1440](previews/desktop-cards.jpg)

Mobile — hero oraz karta:

![Mobile hero 390](previews/mobile-hero.jpg)
![Mobile karta 390](previews/mobile-cards.jpg)

Formularz — lokalny test bez wysyłki:

![Mobile newsletter](previews/mobile-newsletter.jpg)

## Pozostałe warunki

To kandydat do publikacji **zapowiedzi**, nie gotowy sklep. Polityka prywatności nadal wymaga zatwierdzenia treści i daty; przegląd odbiorców/retencji/transferów i wycofania zgody znajduje się w checkliście. Stare treści o pre-orderze pozostałych kolekcji wymagają akceptacji właściciela. Pełna strefa DNS/DKIM, zewnętrzna poczta LH, plan ciągłości SSL i test double opt-in pozostają otwarte. Dane produktów, fotografie, SKU, terminy, dokumenty sprzedaży i GPSR muszą zostać zatwierdzone przed włączeniem zakupów.

Nie wykonano merge, zakupów, zmian hostingu/DNS/poczty, uploadu, publikacji ani aktywacji płatności. Brak sekretów i zrzutów prywatnego panelu w repozytorium.
