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
2. **VASE / kolory i role:** czy `248/255` przyjmujemy jako parę Dual, a `258` jako red-matte? Rekomendacja: tak jako kandydaci; wybrać `main/gallery/detail` i potwierdzić kolor bez wnioskowania o materiale. `171/213` zostawić jako lifestyle.
3. **Poza aktualnym katalogiem:** czy utrzymujemy poza ofertą `244`, `250/WEB021`, `257` i `146`? Rekomendacja: tak — ich geometria rozetowa/spłaszczona nie pasuje bezpiecznie do VASE, KNITTED STAR ani KNITTED MEDALLION. `045` nie należy do tej grupy; pozostaje kandydatem VASE lifestyle.
4. **KNITTED STAR / paleta:** jak rozdzielić `259`, `262` i `263` między White/Marble/red-matte? Rekomendacja: `262` jest kandydatem red-matte, `259/263` tworzą jasną pulę White/Marble, `260` pozostaje detalem; `083` tylko lifestyle.
5. **KNITTED MEDALLION / jedyne zdjęcie:** który z kolorów katalogu reprezentuje `261` i jaki materiał ma być wpisany? Rekomendacja: zachować `261` jako jedyny kandydat modelu, bez przypisania koloru/materiału; pozostałe trzy kolory wymagają zdjęć.

## Rekomendowane mapowanie wszystkich 26 assetów

To jest propozycja analityczna, nie zapis katalogu. Kolor jest oznaczony jako kandydat tylko wtedy, gdy wynika z widocznego wyglądu; nie jest dowodem materiału ani konkretnego filamentu.

| Źródło | WEB | Rola | Model | Kolor | Pewność | Status | Uzasadnienie |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 004 | WEB001 | main | VASE | nierozpoznany | wysoka | confirmed geometry | Właściciel potwierdził geometrię 004 = 238; kolor/materiał otwarte. |
| 008 | WEB002 | gallery | VASE | nierozpoznany | średnia | candidate | Spiralny wygląd jest zgodny z rodziną VASE, ale relacja z 004/238 niepotwierdzona. |
| 014 | WEB003 | gallery | VASE | nierozpoznany | średnia | candidate | Spiralny wygląd zgodny z VASE; brak potwierdzenia relacji z 004/238. |
| 232 | WEB004 | gallery | VASE | nierozpoznany | średnia | candidate | Jasna, nakrapiana forma spiralna; relacja do potwierdzonej pary pozostaje otwarta. |
| 238 | WEB005 | main | VASE | nierozpoznany | wysoka | confirmed geometry | Ta sama jasna, nakrapiana geometria VASE co 004. |
| 243 | WEB006 | main | VASE | white | średnia | owner decision required | Odrębna, gładsza forma spiralna; White to tylko kandydat wizualny. |
| 244 | WEB007 | gallery | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Spłaszczona rozeta nie pasuje bezpiecznie do trzech modeli katalogu. |
| 245 | WEB008 | main | VASE | nierozpoznany | średnia | candidate | Pełna forma spiralna jest kompatybilna z VASE, ale kolor i relacja do 244 są otwarte. |
| 248 | WEB009 | main | VASE | dual | średnia | owner decision required | Potwierdzone podobieństwo wizualne do 255; Dual pozostaje kandydatem. |
| 250 | WEB010 | gallery | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Właściciel potwierdził osobną formę rozetową, nie detal VASE. |
| 255 | WEB011 | main | VASE | dual | średnia | owner decision required | Kandydat tej samej rodziny wizualnej co 248; brak finalnego SKU/koloru. |
| 257 | WEB012 | gallery | poza ofertą | red-matte | wysoka | unmatched/outside current assortment | Osobna czerwona geometria rozetowa; nie scalać z 258. |
| 258 | WEB013 | main | VASE | red-matte | średnia | owner decision required | Wygląda jak czerwona spiralna VASE; red-matte nie dowodzi materiału. |
| 259 | WEB014 | main | KNITTED STAR | nierozpoznany | wysoka | confirmed geometry | Geometria KNITTED STAR potwierdzona; kolor/SKU otwarte. |
| 260 | WEB015 | detail | KNITTED STAR | nierozpoznany | wysoka | confirmed geometry | Detal potwierdzonej geometrii KNITTED STAR. |
| 261 | WEB016 | main | KNITTED MEDALLION | nierozpoznany | wysoka | confirmed geometry | Geometria KNITTED MEDALLION potwierdzona; kolor/materiał otwarte. |
| 262 | WEB017 | main | KNITTED STAR | red-matte | wysoka | owner decision required | Geometria potwierdzona, czerwień widoczna; red-matte jest tylko kandydatem koloru. |
| 263 | WEB018 | main | KNITTED STAR | nierozpoznany | wysoka | confirmed geometry | Geometria potwierdzona; ciepły jasny wygląd nie dowodzi White/Marble. |
| 004 | WEB019 | detail | VASE | nierozpoznany | wysoka | confirmed geometry | Detal źródła 004, należącego do potwierdzonej pary 004/238. |
| 238 | WEB020 | detail | VASE | nierozpoznany | wysoka | confirmed geometry | Detal źródła 238, należącego do potwierdzonej pary 004/238. |
| 250 | WEB021 | detail | poza ofertą | nierozpoznany | wysoka | unmatched/outside current assortment | Detal rozetowej formy 250, bez pasującego SKU w obecnym katalogu. |
| 045 | WEB022 | gallery/lifestyle | VASE | nierozpoznany | średnia | candidate | Pełna jasna spiralna ozdoba zgodna wizualnie z VASE, ale bez potwierdzenia relacji z 004/238. |
| 171 | WEB023 | gallery/lifestyle | VASE | dual | średnia | owner decision required | Ciemna spiralna forma zgodna wizualnie z rodziną 248/255; Dual tylko kandydat. |
| 213 | WEB024 | gallery/lifestyle | VASE | nierozpoznany | średnia | owner decision required | Beżowa forma spiralna; beż nie jest zatwierdzonym kolorem katalogu. |
| 083 | WEB025 | gallery/lifestyle | KNITTED STAR | nierozpoznany | średnia | candidate | Widoczna geometria gwiazdy zgodna z KNITTED STAR; kolor/SKU otwarte. |
| 146 | WEB026 | gallery/lifestyle | poza ofertą | red-matte | średnia | unmatched/outside current assortment | Czerwona forma rozetowa; nie dopasowywać na siłę do VASE ani STAR. |

Pełne nazwy plików, wymiary, metadane manifestu i uzasadnienia są także w [CSV](issue-27-photo-review/PHOTO_MAPPING_RECOMMENDATION.csv) oraz HTML.

## Propozycja katalogu 3 × 4

Poniższa matryca zachowuje istniejące slug/SKU i pokazuje najlepszy obecnie kandydat. Nie aktywuje żadnego wariantu i nie ustawia `photoAsset`.

| Model / slug | Kolor | Main | Galeria | Detale | Braki / warunek |
| --- | --- | --- | --- | --- | --- |
| VASE / `full-soft` | dual | WEB009 | WEB011 | brak | potwierdzić Dual i role |
| VASE / `full-soft` | red-matte | WEB013 | brak | brak | potwierdzić model/kolor; brak galerii/detalu |
| VASE / `full-soft` | white | WEB006 | brak | brak | zaakceptować odrębną gładką odmianę jako VASE |
| VASE / `full-soft` | marble | WEB005 | WEB001 | WEB019, WEB020 | potwierdzić kolor/materiał; geometria ma wysoką pewność |
| KNITTED STAR / `knitted-star` | dual | brak | brak | brak | brak fotografii |
| KNITTED STAR / `knitted-star` | red-matte | WEB017 | brak | brak | kolor tylko kandydat; brak galerii/detalu |
| KNITTED STAR / `knitted-star` | white | WEB014 | WEB025 lifestyle | WEB015 | rozstrzygnąć White vs Marble |
| KNITTED STAR / `knitted-star` | marble | WEB018 | brak | brak | rozstrzygnąć kolor; brak galerii/detalu |
| KNITTED MEDALLION / `knitted-medallion` | dual | brak | brak | brak | brak fotografii; WEB016 ma nierozpoznany kolor |
| KNITTED MEDALLION / `knitted-medallion` | red-matte | brak | brak | brak | brak czerwonego kandydata |
| KNITTED MEDALLION / `knitted-medallion` | white | WEB016 | brak | brak | tylko prowizoryczny slot; kolor/materiał do potwierdzenia |
| KNITTED MEDALLION / `knitted-medallion` | marble | brak | brak | brak | WEB016 nie może być powielony przed decyzją kolorystyczną |

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

