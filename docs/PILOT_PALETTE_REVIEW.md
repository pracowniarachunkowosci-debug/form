# PR #10 — zatwierdzona hybryda R04 + neutralne karty

## Aktualna decyzja i wykonanie — 03.11.2026

[Decyzja właściciela, 11:26 UTC](https://github.com/pracowniarachunkowosci-debug/form/pull/10#issuecomment-6602576344): **zatwierdzony kierunek wizualny to ciemne otwarcie R04 i neutralne karty zapowiedzi**. Nie jest to zgoda na publikację ani uruchomienie sprzedaży. Podgląd aktualny: `previews/lean-pilot/winter-26.html`; `hybrid.css` jest jedyną nową warstwą stylów. Wcześniejsze R04 i pełny wariant neutralny zachowano jako archiwum porównania.

- Nagłówek, pasek pilota, całe otwarcie (hero, nawigacja kolekcji, intro), zestawy i stopka zachowują paletę R04. Hero odzyskuje oryginalny kolor, gradient i cień; pliki AVIF/WebP, kadr i alt są niezmienione.
- KNITTED i SCULPTURAL: porcelain `#F7F6F2`, placeholder stone `#E8E4DD`, charcoal `#272725` dla tekstów i CTA; tekst pomocniczy `#5B5B56`. Champagne `#B7A58B` wyłącznie w dekoracyjnym znaku PF.
- Jasne sekcje realizacji, informacji przed zakupem, premiery i archiwum mają tę samą neutralną typografię kolorystyczną. CTA końcowego zapisu jest grafitowe. To dopasowanie kolorów, bez nowych sekcji, układu, odstępów i treści.
- Cztery modele nadal mają pojedynczy status „W przygotowaniu” oraz „Zapisz się na premierę”. Brak zakupu, cen, wariantów i formularza zamówienia. Model kosztów i plan lean MVP bez zmian.

### Podglądy aktualnej hybrydy

[Galeria: hybryda oraz archiwum porównania](../previews/lean-pilot/comparison.html). Kadry przejścia pokazują granicę ciemnego otwarcia i jasnej sekcji KNITTED; osobne kadry hero i kart pokazują skrajne części tej sekwencji bez zmiany długości strony.

| Kadr | Desktop 1440 | Mobile 390 |
|---|---|---|
| Hero R04 | [Zrzut](previews/hybrid-desktop-hero.jpg) | [Zrzut](previews/hybrid-mobile-hero.jpg) |
| Przejście do kart | [Zrzut](previews/hybrid-desktop-transition.jpg) | [Zrzut](previews/hybrid-mobile-transition.jpg) |
| Karty i CTA | [Zrzut](previews/hybrid-desktop-cards.jpg) | [Zrzut](previews/hybrid-mobile-card.jpg) |

### Walidacja hybrydy

Kontrola DOM porównuje podgląd z R04/d60640f przy 1440 i 390 px. Treści i geometria sekcji/kart pozostają identyczne; brak poziomego overflow. Porównanie wynikowych kolorów, teł, gradientów, obramowań, filtrów i cieni ciemnych sekcji potwierdza zgodność z R04. HTML po odjęciu klasy `hybrid-pilot` i linku do `hybrid.css` jest identyczny z d60640f (normalizacja końców linii).

| Para kolorów hybrydy | Kontrast |
|---|---:|
| Tekst / CTA charcoal–porcelain | 13,84:1 |
| Tekst pomocniczy / porcelain | 6,31:1 |
| Tekst pomocniczy / stone | 5,39:1 |
| Porcelain / hover grafitowego CTA | 9,48:1 |
| Fokus charcoal / porcelain | 13,84:1 |
| Tekst pomocniczy R04 `#CDC6BA` / najjaśniejszy punkt gradientu `#29251C` | 9,00:1 |
| Akcent tekstowy i fokus R04 `#D1B889` / ten sam punkt gradientu | 7,94:1 |
| Ciemny tekst / champagne CTA w hero | 9,82:1 |
| Tekst pomocniczy zestawów / forest | 8,74:1 |

W jasnych sekcjach sprawdzono 78 renderowanych elementów z tekstem: minimum 5,39:1, zero wyników poniżej 4,5:1. Dekoracyjne PF wyłączono; zamkniętych treści details nie zaliczono do tego skanu. Kontrast akapitu po otwarciu szczegółów to 6,31:1 (ta sama para pomocniczego tekstu i porcelain). Gradient R04 oceniono konserwatywnie względem jego najjaśniejszego koloru, bez pomiaru tekstu na fotografii — fotografia nie ma nakładki tekstowej. Progi WCAG i źródła znajdują się w archiwalnej części poniżej.

Sprawdzono klawiaturą menu oraz otwieranie/zamykanie szczegółów produktu. Fokus w ciemnym menu pozostaje champagne, w jasnej karcie charcoal (3 px). Wysokość CTA mobile: 55 px, summary: 54,39 px. Hero jest załadowany bez filtra grayscale. Brak błędów/ostrzeżeń konsoli w sprawdzonym przebiegu. Lokalne linki zweryfikowane. [Skrócony zapis wyników](previews/hybrid-checks.json).

To kontrola kontrastu i regresji podglądu, nie pełny audyt WCAG. Wyłącznie draft PR #10; pozostałe PR-y, main i pliki produkcyjne bez zmian. Bez merge, publikacji, zakupu usług, zmian DNS i aktywacji płatności. Blokady preview nie są ustawieniami do przyszłej produkcji.

---

# Archiwum — pełny neutralny wariant z e230d9a

Poniższa część dokumentuje porównanie poprzedzające decyzję hybrydową. Opis pełnej neutralizacji i monochromatycznego hero dotyczy teraz wyłącznie `winter-26-neutral.html`, nie aktualnej strony `winter-26.html`.

03.11.2026. Odpowiedź na [komentarz projektowy właściciela](https://github.com/pracowniarachunkowosci-debug/form/pull/10#issuecomment-6601928883). Punkt odniesienia: `d60640fd8d9e9754de08d22548bea62251e3682f`. To wariant do oceny, nie nowy zatwierdzony brandbook ani zgoda na publikację.

## Zmiana

| Rola | Kolor | Zastosowanie |
|---|---|---|
| Porcelain | `#F7F6F2` | Tło, hero, nagłówek i stopka |
| Stone | `#E8E4DD` | Placeholdery, pasek pilota, sekcja zestawów |
| Charcoal | `#272725` | Nagłówki, główny tekst, CTA, numeracja, fokus |
| Champagne | `#B7A58B` | Cienka dekoracyjna linia nagłówka i znaki PF w placeholderach (`aria-hidden`) |
| Tekst pomocniczy | `#5B5B56` | Opisy, statusy, podpisy fotografii |
| Hover CTA | `#41413D` | Ciemnoszary stan przycisków |

Usunięto z tego wariantu burgundowe i oliwkowe powierzchnie, gradient hero oraz ciężki cień zdjęcia. Jasna stopka i hero dają bardziej jednolite tło całej marce. Stone wydziela tylko wybrane pola, zamiast pokrywać stronę beżem. Champagne nie służy do oznaczania znaczących stanów ani do tekstów i przycisków.

Hero wykorzystuje **ten sam plik AVIF/WebP i kadr**, wyświetlany przez CSS `grayscale(1)`. Dzięki temu również wstążka i igliwie nie wprowadzają bordo/zieleni. Nie wygenerowano nowego obiektu ani produktu; pliki obrazów są niezmienione. Zdjęcie pozostaje sezonowym editorialem AI. Zachowano copy, w tym istniejący alt opisujący kolor oryginalnej wstążki; przed ewentualnym przyjęciem monochromatycznego wariantu do produkcji alt należy dopasować do finalnej fotografii. Obecna makieta nie rozstrzyga przyszłego kierunku zdjęć innych kolekcji.

Nowy `neutral.css` zmienia wyłącznie kolory, dekoracje, filtr zdjęcia i podkreślenie hover linku. Bez zmian krojów pisma, wymiarów, siatek i odstępów. HTML różni się od d60640f tylko dołączeniem tego CSS, klasą zakresu i kolorem interfejsu przeglądarki (`theme-color`). R04 pozostaje osobnym podglądem; wspólnego CSS i skryptu nie edytowano.

## Porównanie stare / nowe

[Galeria porównawcza HTML](../previews/lean-pilot/comparison.html) działa po uruchomieniu lokalnego serwera opisanego w [README](../previews/lean-pilot/README.md). Zawiera linki do obu kompletnych, interaktywnych stron. Poniższe obrazy to zrzuty widocznego obszaru; szerokość viewportu obejmuje pasek przewijania.

| Widok | R04 — d60640f | Neutralny |
|---|---|---|
| Desktop, viewport 1440 px | [Zrzut](previews/r04-desktop.jpg) | [Zrzut](previews/neutral-desktop.jpg) |
| Mobile, viewport 390 px — hero | [Zrzut](previews/r04-mobile.jpg) | [Zrzut](previews/neutral-mobile.jpg) |
| Mobile, viewport 390 px — karta | [Zrzut](previews/r04-mobile-card.jpg) | [Zrzut](previews/neutral-mobile-card.jpg) |

R04 buduje sezonową, wieczorną atmosferę. Neutralny wariant daje spokojniejszą podstawę dla różnych kategorii Pracowni Form, a ciemne CTA nadal jest łatwe do rozpoznania. **Rekomendacja projektowa:** neutralna paleta jest spójnym kandydatem na bazę marki; ostateczny odbiór powinien uwzględnić prawdziwe zdjęcia produktów. Sama zmiana kolorów nie oznacza zatwierdzenia publikacji.

## Kontrast i kontrola regresji

Obliczenia sRGB dla kolorów wynikowych CSS. WCAG 2.2 AA wymaga minimum 4,5:1 dla zwykłego tekstu i 3:1 dla dużego tekstu; kryterium nie obejmuje czysto dekoracyjnych znaków. Źródło: [W3C — Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Znaczące elementy i stany interfejsu oceniono względem progu 3:1: [W3C — Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

| Para / element | Kontrast | Ocena |
|---|---:|---|
| Charcoal / porcelain; tekst CTA w odwrotnej kolejności | 13,84:1 | AA tekst |
| Charcoal / stone; numeracja zestawów | 11,81:1 | AA tekst |
| Tekst pomocniczy / porcelain | 6,31:1 | AA tekst |
| Tekst pomocniczy / stone; podpisy placeholderów | 5,39:1 | AA tekst |
| Porcelain / hover CTA `#41413D` | 9,48:1 | AA tekst |
| Nawigacja z odziedziczoną opacity 0,9 / porcelain | ok. 10,2:1 | AA tekst, uwzględnione mieszanie |
| Fokus charcoal / porcelain lub stone | 13,84:1 / 11,81:1 | Powyżej 3:1 |
| Champagne / porcelain lub stone | 2,21:1 / 1,89:1 | Wyłącznie dekoracja, nie nadaje się do tekstu ani fokusu |

Przeprowadzona kontrola:

- Porównanie HTML z d60640f po normalizacji końców linii: treść i elementy interaktywne identyczne poza trzema zmianami prezentacyjnymi wskazanymi wyżej.
- Desktop 1440 px: identyczne teksty oraz prostokąty nagłówka, sekcji i czterech kart w obu wariantach. Mobile 390 px: identyczne teksty i geometria sekcji/kart. Brak poziomego overflow w obu wariantach.
- Skan 134 widocznych elementów zawierających tekst w neutralnym desktopie: żadna sprawdzona para poniżej 4,5:1; minimum 5,39:1. Uwzględniono opacity nawigacji, pominięto dekoracje `aria-hidden`. Nie badano kolorów pikseli fotografii jako tekstu. [Zapis wyników](previews/palette-checks.json).
- Na mobile: menu otwiera się i zamyka klawiszem Enter, aktualizuje `aria-expanded`; szczegóły karty otwierają się i zamykają klawiszem Enter. Fokus obu elementów ma charcoal i 3 px. CTA karty: 55 px wysokości, summary: 54,39 px.
- Hero załadowany, filtr monochromatyczny działa. Brak gradientów w tłach elementów neutralnej strony; brak błędów i ostrzeżeń konsoli w sprawdzonym przebiegu.
- Cztery karty nadal mają po jednym statusie „W przygotowaniu” i zapis na premierę. Brak formularzy, selektorów, przycisków zakupu i linków płatniczych. Nie wysyłano danych do listy premierowej.

To kontrola kontrastu i regresji zmienionego podglądu, **nie pełny audyt zgodności WCAG**. Nie zmienia wcześniejszych blokad uruchomienia sprzedaży, dokumentów prawnych ani planu kosztowego.

## Granice zmian

Wyłącznie dokumentacja i `previews/lean-pilot` w draft PR #10. Root produkcji, PR #4/#5/#7/#8 oraz main pozostają bez zmian. Nie kupowano hostingu, nie zmieniano DNS, nie aktywowano płatności, nie wykonywano merge ani publikacji. Ustawienia `noindex`, wyłączonej analityki i blokującego CSP pozostają tylko w podglądzie; nie są konfiguracją do przyszłego wdrożenia.
