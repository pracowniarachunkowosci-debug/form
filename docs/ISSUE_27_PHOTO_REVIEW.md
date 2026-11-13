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

## Pytania blokujące przypisanie do SKU

1. Czy 004, 008, 014 oraz 232/238 przedstawiają ten sam wariant? Jeśli tak, czy jest to `full-soft` / Marble?
2. Czy 243 jest wariantem White, czy oddzielną geometrią poza aktualną ofertą?
3. Czy 244/245 są ofertowym kolorem? Obecny katalog nie ma zatwierdzonego beżu.
4. Czy 248/255 to ten sam wariant Dual i który kadr ma być `main`? Czy 250 jest jego detalem?
5. Czy 257/258 są wariantem `red-matte` VASE?
6. Czy 259/260/263 przedstawiają jedną geometrię KNITTED STAR? Który wariant to White, a który Marble? Czy 083 jest tylko lifestyle dla tej samej sztuki?
7. Jaki model, wariant i materiał przedstawia 261?

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

