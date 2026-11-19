# WINTER 26: finalne wydanie 19.11.2026

Wydanie `PF-W26-FINAL-20261119-145544-CET` opublikowano na Uberspace 19.11.2026, 14:55:44–14:55:46 CET (Europe/Warsaw). Ten zapis aktualizuje wcześniejsze informacje o blokadzie SSH i oczekiwaniu na publikację. Źródłem były aktualne pliki produkcyjne; dokumenty z `docs/legal-draft/` nie były publikowane. GitHub pozostaje dokumentacją, nie źródłem tego wdrożenia. PR #29 pozostaje bez merge.

## Decyzje właściciela

- Wyłącznie Paczkomat InPost: od 1 do 5 ozdób 18,49 zł, od 6 łącznie bezpłatnie, także przy łączeniu zestawów. Bez zmiany cen zestawów.
- Realizacja na bieżąco. Zazwyczaj nadanie w 3 dni robocze, maksymalnie w 7 od potwierdzenia płatności. Dotyczy nadania, nie doręczenia.
- Gotowe produkty po przygotowaniu; wykonywane na zamówienie drukowane po zakupie. Zamówienia mieszane dopuszczalne, bez obietnicy jednej lub osobnych przesyłek. Bez fizycznych przydziałów.
- Ustawowe odstąpienie 14 dni. Zwykły koszt odesłania po stronie kupującego po poinformowaniu przed zakupem. Reklamacja z tytułu niezgodności: koszty po stronie sprzedawcy. Standardowa produkcja po zakupie nie wyłącza odstąpienia.
- Właściciel zatwierdził kompletne wdrożenie dokumentów i SEO po kontroli, bez ponownej zgody projektowej.

## Wdrożenie

Zmieniono 10 HTML i 2 PDF. Usunięto stare 3/7/7 i przydziały z regulaminu/dostawy, także stare terminy z HELIX, zestawu 2 i zasad premiery. Wdrożono trzy bajtowo niezmienione pliki zatwierdzonego pakietu `shipping-returns-20261119`: Organization strony głównej, STAR i MEDALLION.

Publiczne zwroty i reklamacje były prawidłowe i pozostały bez zmian. Zachowano wszystkie inne poprawne treści, prawa konsumenta, ceny, SKU, warianty, zdjęcia, JS/CSS i API. .htaccess, DNS/SSL, poczta, Stripe, analityka i staging bez zmian. Prywatny approvedReleaseSha256 zmieniono wyłącznie z powodu nowej wersji dokumentów. Archiwa sześciu PDF przed i po mają osobne acceptedRelease. Nie zmieniono danych zamówień.

Manifest całego publicznego wydania SHA-256: `b5047c5fdd51a24908726428b046a073ddd5ee6ab1ae62dee5d3e9b12ba7da00`.

## Walidacja po publikacji

- HTTP GET 17 zasobów: 200 po istniejących przekierowaniach; treść zgodna z lokalnym candidate i plikami serwera.
- [Google STAR](https://search.google.com/test/rich-results/result?id=RLVVAYOI7BNPoWAUrTzjbA): 4 prawidłowe elementy, Merchant listings bez ostrzeżeń.
- [Google MEDALLION](https://search.google.com/test/rich-results/result?id=EuXYyzATfF8OqAbs_xLnNw): 4 prawidłowe elementy, Merchant listings bez ostrzeżeń.
- [Google Organization](https://search.google.com/test/rich-results/result?id=Sae1yCOcnk0shwDAOvLAUA): 4 prawidłowe elementy, w tym zwroty i dostawa.
- Product snippets: jedynie opcjonalne `review`/`aggregateRating`; polityka zwrotów strony głównej: opcjonalne `refundType`. Nie dodawano fikcyjnych danych.
- Schema.org dla dwóch kart i strony głównej: 0 błędów, 0 ostrzeżeń.
- 96 lokalnych asercji PASS. PDF: 5 stron sprawdzonych, wszystkie akapity zachowane. Izolowane potwierdzenia sześciu PDF i odrzucenie niezgodnej wersji PASS; bez wysyłki.
- Bazy i staging niezmienione, prywatne endpointy chronione. Pełny backup 460 plików poza webroot i rollback `--check` zweryfikowane.
- NOT RUN: rzeczywiste transakcje; faktyczny rollback produkcji; ponowne sprawdzenie w zalogowanym Search Console; nowy test mobilny (narzędzie nie zastosowało rozmiaru, nie zgłaszamy PASS).

## Pliki

| Plik | SHA-256 po |
|---|---|
| `dostawa-i-platnosci.html` | `cdf36bc86dfa11fcc94bac4c393fdfe23905f3856273ba12a431dfbb15c4b013` |
| `index.html` | `93fdd70d75afd7bdbf956f197bd1b38497a5435f14927bda89607466d23a44c0` |
| `legal-pdf/dostawa-i-platnosci.pdf` | `72e82f79ea0a179bfd66bf889ea39ac39c4cda1eaa9273bbc67e6696e0fa8c08` |
| `legal-pdf/regulamin-sklepu.pdf` | `3f14ba60777ccbfbd3a29ab6a5e802cb5f0f154f87b80bf176ca6e9c3bc50bcf` |
| `regulamin-sklepu.html` | `fd670448e4e38a66dbbc4d6d0ea593d165a2c23e86f9b6f9f997b364a685bca8` |
| `sklep/winter-helix.html` | `9529191ab0ab15f1d2bd500cf58ae1c201f2adfb69fe9ec1f5a3668d8896c84b` |
| `sklep/winter-knitted-medallion.html` | `c4c7153e9930ebec3ad8e209429111a03e3ef80a8a5445ac58c94aba338b121a` |
| `sklep/winter-knitted-star.html` | `2b3e76ab6d071e5043799f00508a188edc3af670dc72fc8ff755cc65a00adee9` |
| `sklep/winter-zestaw-2.html` | `5a1cfd76f64f6b86ca27f4a2663fb27ffe083b3db6289c214df4307f80231c34` |
| `winter-helix.html` | `9529191ab0ab15f1d2bd500cf58ae1c201f2adfb69fe9ec1f5a3668d8896c84b` |
| `winter-zestaw-2.html` | `5a1cfd76f64f6b86ca27f4a2663fb27ffe083b3db6289c214df4307f80231c34` |
| `zasady-premiery.html` | `df1c43311f6fe4c05904227ab46f009cfdf81a4e273eb18c167cc67cfda9f3a7` |

Pełne oryginały, candidate, diff, manifest przed/po, dowody HTTP i walidatorów oraz instrukcja rollbacku znajdują się w lokalnym pakiecie odbiorczym właściciela. Sekretów i danych klientów nie dołączono.
