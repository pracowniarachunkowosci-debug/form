# Issue #27 — WINTER 26 / przegląd pakietu fotografii

Stan: **oczekuje na identyfikację wariantów przez właściciela**.

## Co zostało sprawdzone

Pakiet `08_PRODUCT_WEB_HANDOFF` został zweryfikowany razem z `START_TUTAJ.md`, manifestem, mapą produktu, CSV pytań identyfikacyjnych, katalogiem referencyjnym i contact sheetem.

- 26 plików webowych: 11 `main`, 11 `gallery`, 4 `detail`.
- 23 unikalne źródła zdjęciowe.
- 21 eksportów oznaczonych jako Codex i 5 jako Claude lifestyle.
- kopie w handoffie są zgodne bajt w bajt ze źródłami eksportu.
- `automatic_assignment_allowed: false`.
- wszystkie 26 pozycji mają `product_name`, SKU, materiał i `product_slug` do potwierdzenia.
- wszystkie pozycje mają `ready_for_auto_assignment: false` i nie mogą trafić do `variants[].photoAsset` bez decyzji właściciela.
- VASE zachowuje slug `full-soft`; nie tworzę nowego sluga ani nowego SKU.
- zdjęcia lifestyle nie zastępują neutralnych ujęć `main`.
- właściciel doprecyzował docelową paletę 5 kolorów: Czerwony, Biały, Biały nakrapiany (Marble), Czarno-czerwony (Black / Red) oraz rekomendowane Cappuccino; istniejące dane katalogowe mają obecnie tylko cztery `colorId`/SKU.

## Inwentaryzacja źródeł

| Źródła | Widoczny kierunek | Rola w handoffie |
| --- | --- | --- |
| 004, 238 | ta sama jasna, nakrapiana geometria VASE — potwierdzone | main / detail |
| 008, 014, 232 | jasne spiralne ujęcia; kandydaci do rodziny VASE, bez potwierdzonej relacji z 004/238 | gallery |
| 243 | odrębna, gładsza odmiana spiralna; kandydat VASE, bez automatycznego scalania | main |
| 244 | spłaszczona forma rozetowa; poza obecnym katalogiem 3 modeli | gallery |
| 245 | pełna beżowa forma spiralna; kandydat VASE, kolor poza zatwierdzoną paletą | main |
| 248, 255 | podobna rodzina wizualna Dual; kandydaci VASE | main |
| 250 | odrębna forma rozetowa; poza obecnym katalogiem | gallery / detail |
| 257 | czerwona forma rozetowa; poza obecnym katalogiem | gallery |
| 258 | czerwona forma spiralna; kandydat VASE / red-matte | main |
| 259, 260, 262, 263 | geometria KNITTED STAR — potwierdzona; kolory i role katalogowe nie w pełni ustalone | main / detail |
| 261 | geometria KNITTED MEDALLION — potwierdzona; kolor i materiał nieustalone | main |
| 045 | lifestyle z pełną jasną spiralną formą; kandydat VASE, ale niepotwierdzona relacja z 004/238 | gallery |
| 171, 213, 083, 146 | lifestyle; tylko dodatkowa galeria po akceptacji; `146` rekomendowane poza katalogiem | gallery |
| 171, 213, 083, 146 | aranżacje lifestyle | wyłącznie dodatkowa galeria po akceptacji; nie używać jako `main` |

## Potwierdzone rozpoznanie wizualne

Na podstawie odpowiedzi właściciela potwierdzone są poniższe geometrie i relacje zdjęć. Potwierdzenie nie rozstrzyga jeszcze koloru, materiału, SKU ani gotowości do publikacji:

- `004` i `238` — ta sama jasna, nakrapiana geometria VASE;
- `243` — podobna spiralna forma, ale gładsza powierzchnia; odrębna odmiana/egzemplarz, bez łączenia z `004/238`;
- `248` i `255` — podobieństwo w rodzinie wizualnej Dual; dokładna rola kadru i wariant pozostają otwarte;
- `250` — osobna forma rozetowa, nie przypisywać do spiralnej VASE;
- `257` i `258` — różne geometrie; `258` wygląda jak spiralna VASE, `257` jak forma rozetowa; nie scalać;
- `045` — po ponownym porównaniu wygląda jak pełna jasna spiralna ozdoba zgodna wizualnie z VASE, nie jak oczywista rozeta; dokładna relacja z `004/238` i kolor pozostają otwarte;
- `259`, `260`, `262`, `263` — geometria KNITTED STAR rozpoznana; faktura i kolor różnią się między zdjęciami;
- `261` — geometria KNITTED MEDALLION rozpoznana; kolor i materiał pozostają do potwierdzenia.

## Pięć decyzji dla właściciela

Pełne obrazy są obok siebie w HTML/PDF. Poniższe pytania nie powtarzają potwierdzonego rozpoznania geometrii:

1. **VASE / wybór zdjęć katalogowych:** czy do aktualnego VASE (`full-soft`) włączamy `004/238`, osobny kandydat `243`, kandydata `245` i lifestyle `045`? Rekomendacja: `004/238` jako jedyny wysoki poziom pewności; `243/245` pozostawić jako decyzję właściciela, a `045` traktować wyłącznie jako VASE-compatible lifestyle do czasu potwierdzenia relacji.
2. **VASE / kolory i role:** czy `248/255` przyjmujemy jako parę Czarno-czerwony (Black / Red), `258` jako Czerwony, `004/238` jako Biały nakrapiany (Marble), `243` jako Biały, a `245` jako kandydat Cappuccino? Rekomendacja: traktować wszystkie jako kandydatów wizualnych — niezatwierdzonych; wybrać `main/gallery/detail` i potwierdzić kolory na podstawie fizycznych próbek, nie zdjęcia.
3. **Poza aktualnym katalogiem:** czy utrzymujemy poza ofertą `244`, `250/WEB021`, `257` i `146`? Rekomendacja: tak — ich geometria rozetowa/spłaszczona nie pasuje bezpiecznie do VASE, KNITTED STAR ani KNITTED MEDALLION. `045` nie należy do tej grupy; pozostaje kandydatem VASE lifestyle.
4. **KNITTED STAR / paleta:** czy `262` zostawić jako kandydata Czerwonego, `259` jako kandydata Białego, a `263` jako kandydata Białego nakrapianego (Marble)? Rekomendacja: wszystkie trzy oznaczyć jako kandydatów wizualnych — niezatwierdzonych; `260` pozostaje detalem bez koloru, `083` tylko lifestyle, a Cappuccino/Dual wymagają nowych zdjęć.
5. **KNITTED MEDALLION / kolor nierozpoznany:** jaki kolor i materiał ma `261`? Rekomendacja: nie przypisywać go do White; pozostawić osobny slot `Kolor nierozpoznany`. Wszystkie pięć kolorystycznych SKU Medallion wymagają osobnych potwierdzonych zdjęć.

## Rekomendowane mapowanie wszystkich 26 assetów

To jest propozycja analityczna, nie zapis katalogu. Kolor jest oznaczony jako kandydat tylko wtedy, gdy wynika z widocznego wyglądu; nie jest dowodem materiału ani konkretnego filamentu.

| Źródło | WEB | Rola | Model | Kolor | Pewność | Status | Uzasadnienie |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 004 | WEB001 | main | VASE | Biały nakrapiany (Marble) — kandydat wizualny — niezatwierdzony | wysoka | confirmed geometry | Właściciel potwierdził geometrię 004 = 238; Marble wynika wyłącznie z wyglądu, nie potwierdza materiału. |
| 008 | WEB002 | gallery | VASE | nierozpoznany | średnia | candidate | Spiralny wygląd jest zgodny z rodziną VASE, ale relacja z 004/238 niepotwierdzona. |
| 014 | WEB003 | gallery | VASE | nierozpoznany | średnia | candidate | Spiralny wygląd zgodny z VASE; brak potwierdzenia relacji z 004/238. |
| 232 | WEB004 | gallery | VASE | nierozpoznany | średnia | candidate | Jasna, nakrapiana forma spiralna; relacja do potwierdzonej pary pozostaje otwarta. |
| 238 | WEB005 | main | VASE | Biały nakrapiany (Marble) — kandydat wizualny — niezatwierdzony | wysoka | confirmed geometry | Ta sama jasna, nakrapiana geometria VASE co 004; Marble nie potwierdza materiału. |
| 243 | WEB006 | main | VASE | Biały — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Odrębna, gładsza forma spiralna; White jest tylko kandydatem wizualnym. |
| 244 | WEB007 | gallery | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Spłaszczona rozeta nie pasuje bezpiecznie do trzech modeli katalogu. |
| 245 | WEB008 | main | VASE | Cappuccino — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Pełna forma spiralna jest kompatybilna z VASE; ciepły beż sugeruje Cappuccino, ale wymaga próbki fizycznej i nowego ID/SKU. |
| 248 | WEB009 | main | VASE | Czarno-czerwony (Black / Red) — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Potwierdzone podobieństwo wizualne do 255; kolor i role pozostają otwarte. |
| 250 | WEB010 | gallery | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Właściciel potwierdził osobną formę rozetową, nie detal VASE. |
| 255 | WEB011 | main | VASE | dual | średnia | owner decision required | Kandydat tej samej rodziny wizualnej co 248; brak finalnego SKU/koloru. |
| 257 | WEB012 | gallery | poza ofertą | Czerwony — kandydat wizualny — niezatwierdzony | wysoka | unmatched/outside current assortment | Osobna czerwona geometria rozetowa; nie scalać z 258. |
| 258 | WEB013 | main | VASE | Czerwony — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Wygląda jak czerwona spiralna VASE; kolor nie dowodzi materiału. |
| 259 | WEB014 | main | KNITTED STAR | Biały — kandydat wizualny — niezatwierdzony | wysoka | owner decision required | Geometria KNITTED STAR potwierdzona; White wynika tylko z wyglądu, nie z materiału VASE. |
| 260 | WEB015 | detail | KNITTED STAR | nierozpoznany | wysoka | confirmed geometry | Detal potwierdzonej geometrii KNITTED STAR. |
| 261 | WEB016 | main | KNITTED MEDALLION | nierozpoznany | wysoka | confirmed geometry | Geometria KNITTED MEDALLION potwierdzona; kolor/materiał otwarte. |
| 262 | WEB017 | main | KNITTED STAR | Czerwony — kandydat wizualny — niezatwierdzony | wysoka | owner decision required | Geometria potwierdzona, czerwień widoczna; kolor nie dowodzi materiału. |
| 263 | WEB018 | main | KNITTED STAR | Biały nakrapiany (Marble) — kandydat wizualny — niezatwierdzony | wysoka | owner decision required | Geometria potwierdzona; Marble wynika tylko z wyglądu i nie jest kopiowany z VASE. |
| 004 | WEB019 | detail | VASE | Biały nakrapiany (Marble) — kandydat wizualny — niezatwierdzony | wysoka | confirmed geometry | Detal źródła 004, należącego do potwierdzonej pary 004/238. |
| 238 | WEB020 | detail | VASE | Biały nakrapiany (Marble) — kandydat wizualny — niezatwierdzony | wysoka | confirmed geometry | Detal źródła 238, należącego do potwierdzonej pary 004/238. |
| 250 | WEB021 | detail | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Detal rozetowej formy 250, bez pasującego SKU w obecnym katalogu. |
| 045 | WEB022 | gallery/lifestyle | VASE | nierozpoznany | średnia | candidate | Pełna jasna spiralna ozdoba zgodna wizualnie z VASE, ale bez potwierdzenia relacji z 004/238. |
| 171 | WEB023 | gallery/lifestyle | VASE | Czarno-czerwony (Black / Red) — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Ciemna spiralna forma zgodna wizualnie z rodziną 248/255; kolor pozostaje kandydatem. |
| 213 | WEB024 | gallery/lifestyle | VASE | Cappuccino — kandydat wizualny — niezatwierdzony | średnia | owner decision required | Beżowa forma spiralna; Cappuccino wymaga potwierdzenia fizycznego i nowego ID/SKU. |
| 083 | WEB025 | gallery/lifestyle | KNITTED STAR | nierozpoznany | średnia | candidate | Widoczna geometria gwiazdy zgodna z KNITTED STAR; kolor/SKU otwarte. |
| 146 | WEB026 | gallery/lifestyle | poza ofertą | red-matte | średnia | unmatched/outside current assortment | Czerwona forma rozetowa; nie dopasowywać na siłę do VASE ani STAR. |

Pełne nazwy plików, wymiary, metadane manifestu i uzasadnienia są także w [CSV](issue-27-photo-review/PHOTO_MAPPING_RECOMMENDATION.csv) oraz HTML.

## Propozycja katalogu 3 × 5

Docelowa paleta obejmuje pięć nazw kolorów: Czerwony, Biały, Biały nakrapiany (Marble), Czarno-czerwony (Black / Red) oraz rekomendowane Cappuccino. Obecne dane mają tylko cztery `colorId`/SKU (`dual`, `red-matte`, `white`, `marble`); Cappuccino wymaga osobnego przygotowania ID/SKU i akceptacji. Matryca nie aktywuje żadnego wariantu i nie ustawia `photoAsset`.

W tabeli mapowania `Rola` oznacza `source_role` z handoffu. `recommended_site_role` jest rozdzielone w CSV/HTML/PDF, aby np. WEB009/WEB011 mogły mieć oba `source_role=main`, ale rekomendowane role `main/gallery`, a WEB005/WEB001 odpowiednio `main/gallery`.

| Model / slug | Kolor docelowy | Main | Galeria | Detale | Braki / warunek |
| --- | --- | --- | --- | --- | --- |
| VASE / `full-soft` | Czarno-czerwony (Black / Red) | WEB009 | WEB011 | brak | kandydat wizualny — niezatwierdzony; WEB009/WEB011 mają source_role `main`, sklep: `main/gallery` |
| VASE / `full-soft` | Czerwony | WEB013 | brak | brak | kandydat wizualny — niezatwierdzony; galeria/detal brak |
| VASE / `full-soft` | Biały | WEB006 | brak | brak | kandydat wizualny — niezatwierdzony; odrębna gładka geometria do akceptacji jako VASE |
| VASE / `full-soft` | Biały nakrapiany (Marble) | WEB005 | WEB001 | WEB019, WEB020 | kandydat wizualny — niezatwierdzony; WEB005/WEB001 source_role `main`, sklep: `main/gallery` |
| VASE / `full-soft` | Cappuccino — ID/SKU do przygotowania | WEB008 | brak | brak | kandydat wizualny — niezatwierdzony; piąty kolor bez istniejącego `colorId`/SKU |
| KNITTED STAR / `knitted-star` | Czarno-czerwony (Black / Red) | brak | brak | brak | brak fotografii; nie kopiować koloru z VASE |
| KNITTED STAR / `knitted-star` | Czerwony | WEB017 | brak | brak | kandydat wizualny — niezatwierdzony; galeria/detal brak |
| KNITTED STAR / `knitted-star` | Biały | WEB014 | brak | WEB015 | kandydat wizualny — niezatwierdzony; WEB015 ma kolor nierozpoznany |
| KNITTED STAR / `knitted-star` | Biały nakrapiany (Marble) | WEB018 | brak | brak | kandydat wizualny — niezatwierdzony; galeria/detal brak |
| KNITTED STAR / `knitted-star` | Cappuccino — ID/SKU do przygotowania | brak | brak | brak | brak fotografii; nie kopiować koloru z VASE |
| KNITTED MEDALLION / `knitted-medallion` | Czarno-czerwony (Black / Red) | brak | brak | brak | brak fotografii; nie kopiować koloru z VASE |
| KNITTED MEDALLION / `knitted-medallion` | Czerwony | brak | brak | brak | brak fotografii; brak potwierdzonego czerwonego medallionu |
| KNITTED MEDALLION / `knitted-medallion` | Biały | brak | brak | brak | WEB016 nie ma rozpoznanego koloru |
| KNITTED MEDALLION / `knitted-medallion` | Biały nakrapiany (Marble) | brak | brak | brak | WEB016 nie ma rozpoznanego koloru |
| KNITTED MEDALLION / `knitted-medallion` | Cappuccino — ID/SKU do przygotowania | brak | brak | brak | brak fotografii i brak istniejącego `colorId`/SKU |
| KNITTED MEDALLION / `knitted-medallion` | Kolor nierozpoznany | WEB016 | — | — | osobny slot evidence modelu; nie przypisywać do White ani innego koloru |

## Bezpieczny stan wdrożenia

Do czasu odpowiedzi:

- obecne wizualizacje pozostają w katalogu i nie są mieszane z niezatwierdzonymi fotografiami;
- nie kopiuję 6112 px masterów bezpośrednio do miniaturek;
- nie zmieniam `data/winter26-products.json`, `data/store-media.json` ani `variants[].photoAsset` na podstawie podobieństwa wizualnego;
- po potwierdzeniu przygotuję dla każdego zaakceptowanego SKU: `main`, galerię, detal, `srcset` WebP/AVIF, alt, `colorId`, rodzaj `fotografia`, hash źródła i podgląd desktop/mobile;
- dopiero po akceptacji zdjęć podmienię `picture`, podpisy, alt oraz obraz OG/Twitter.

## Karty produktowe

Na tym etapie karta wysyłkowa może być wyłącznie proofem układu. Nie wpisuję jako faktu niepotwierdzonego SKU, koloru, materiału, producenta, ostrzeżeń ani adresu. Finalna karta A6/A7 zostanie zasilona tym samym potwierdzonym źródłem katalogowym co sklep i będzie zawierać: nazwę modelu, kolor, zweryfikowany materiał i użytkowanie, pielęgnację, informacje producenta/bezpieczeństwa, identyfikację zamówienia, QR do strony produktu oraz oznaczenie edycji WINTER 26.

## Pakiet decyzyjny z rzeczywistymi zdjęciami

- [HTML z planszą kontaktową, porównaniami i pełnymi metadanymi](issue-27-photo-review/index.html)
- [PDF do pobrania / przekazania właścicielowi](issue-27-photo-review/issue-27-photo-decision-pack.pdf)
- [CSV z pełną tabelą rekomendowanego mapowania 26 assetów](issue-27-photo-review/PHOTO_MAPPING_RECOMMENDATION.csv)
- plansze JPG znajdują się w `docs/issue-27-photo-review/boards/`, a miniatury źródłowe w `docs/issue-27-photo-review/assets/`;
- pakiet zawiera pięć plansz decyzji właściciela, pokazuje kandydatów i hipotezy manifestu, ale nie zmienia żadnego `photoAsset`, wariantu, ceny, stanu ani dostępności.

