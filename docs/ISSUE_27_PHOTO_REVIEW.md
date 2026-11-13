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
| 004, 008, 014, 232, 238 | jasna, nakrapiana forma spiralna | main / gallery / detail; relacja między grupami niepotwierdzona |
| 243 | jasna, bardziej jednolita forma spiralna | main; nie scalać automatycznie z 004/238 |
| 244, 245 | beżowa forma spiralna/medalionowa | gallery / main; katalog nie ma zatwierdzonego koloru beżowego |
| 248, 250, 255 | ciemne, miedziane i wielobarwne refleksy | main / gallery / detail; wariant Dual jest tylko hipotezą |
| 257, 258 | czerwona forma spiralna | main / gallery; `red-matte` jest tylko hipotezą |
| 259, 260, 262, 263 | jasne i czerwone ażurowe gwiazdy | main / gallery; kolor oraz zgodność egzemplarza wymagają potwierdzenia |
| 261 | jasna ażurowa forma medalionowa | main; kolor i materiał wymagają potwierdzenia |
| 045, 171, 213, 083, 146 | aranżacje lifestyle | wyłącznie dodatkowa galeria po akceptacji; nie używać jako `main` |

## Potwierdzone rozpoznanie wizualne

Na podstawie odpowiedzi właściciela potwierdzone są poniższe geometrie i relacje zdjęć. Potwierdzenie nie rozstrzyga jeszcze koloru, materiału, SKU ani gotowości do publikacji:

- `004` i `238` — ta sama jasna, nakrapiana geometria VASE;
- `243` — podobna spiralna forma, ale gładsza powierzchnia; odrębna odmiana/egzemplarz, bez łączenia z `004/238`;
- `248` i `255` — podobieństwo w rodzinie wizualnej Dual; dokładna rola kadru i wariant pozostają otwarte;
- `250` — osobna forma rozetowa, nie przypisywać do spiralnej VASE;
- `257` i `258` — różne geometrie; `258` wygląda jak spiralna VASE, `257` jak forma rozetowa; nie scalać;
- `259`, `260`, `262`, `263` — geometria KNITTED STAR rozpoznana; faktura i kolor różnią się między zdjęciami;
- `261` — geometria KNITTED MEDALLION rozpoznana; kolor i materiał pozostają do potwierdzenia.

## Pozostałe decyzje blokujące przypisanie do SKU

1. Dla `004/238`: który kadr ma być `main`, które `gallery/detail`, oraz jaki kolor i materiał należy przypisać? Czy `008/014/232` należą do tej samej rodziny, czy są odrębnymi egzemplarzami?
2. Dla `243`: jaki jest docelowy kolor, materiał, SKU i rola kadru (`main/gallery/detail`)?
3. Dla `244/245`: czy beż jest zatwierdzonym kolorem ofertowym, jaki materiał i SKU mają reprezentować oraz który kadr jest główny?
4. Dla `248/255`: który kadr jest `main`, który `gallery/detail`, oraz czy można zatwierdzić wspólny wariant Dual i materiał?
5. Dla `250`: jaki model/SKU, kolor, materiał i rola kadru są właściwe dla osobnej formy rozetowej?
6. Dla `257` i `258`: jakie są osobne modele/SKU, kolory, materiały i role kadrów? Nie łączyć ich w jeden model.
7. Dla `259/260/262/263`: które zdjęcia odpowiadają kolorom White/Marble/red lub innym zatwierdzonym wariantom, jaki materiał i który kadr ma być `main`? Czy `083` pozostaje wyłącznie lifestyle?
8. Dla `261`: jaki kolor, materiał i SKU należy przypisać do KNITTED MEDALLION oraz który kadr jest główny?

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
- plansze JPG znajdują się w `docs/issue-27-photo-review/boards/`, a miniatury źródłowe w `docs/issue-27-photo-review/assets/`;
- pakiet pokazuje kandydatów i hipotezy manifestu, ale nie zmienia żadnego `photoAsset`, wariantu, ceny, stanu ani dostępności.

