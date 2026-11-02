# Obliczenia TCO — wygenerowane z assumptions.json

Data źródeł: 2026-11-02. Wszystkie wyniki w PLN. Założenia, VAT, wyłączenia i źródła: [raport](../STORE_TCO_NEXT_VS_WOO.md).

## Prowizja od jednej opłaconej transakcji

| Koszyk brutto | A: BLIK | A: karta EOG standard | A: przelew P24 przez Stripe | B: BLIK/karta 3DS/przelew | A: średnia miksu* | B: średnia miksu |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 39,00 | 1,62 | 1,59 | 1,74 | 0,81 | 1,6260 | 0,8100 |
| 78,00 | 2,25 | 2,17 | 2,48 | 1,31 | 2,2570 | 1,3100 |
| 156,00 | 3,50 | 3,34 | 3,96 | 2,32 | 3,5140 | 2,3200 |

*Średnia ważona 70% BLIK / 20% standardowych kart EOG / 10% przelewów; nie zaokrąglamy średniej przed mnożeniem przez liczbę transakcji. Stripe: HALF_UP do grosza jako założenie. P24: część procentowa w górę do grosza, potem opłata stała; dla kart przyjęto tę samą zasadę do potwierdzenia. Źródło i korekta: [porównanie operatorów](../PAYMENTS_VERCEL_COMPARISON.md#3-koszty-bez-promocji).

## 12 miesięcy

| Zam./mies. | Koszyk brutto | A: technologia + prowizje | B: technologia + prowizje | A: z pracą i utrzymaniem | B: z pracą i utrzymaniem |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 39,00 | 2 430,24 | 884,48 | 47 430,24 | 24 884,48 |
| 20 | 78,00 | 2 581,68 | 1 004,48 | 47 581,68 | 25 004,48 |
| 20 | 156,00 | 2 883,36 | 1 246,88 | 47 883,36 | 25 246,88 |
| 100 | 39,00 | 3 991,20 | 1 662,08 | 48 991,20 | 25 662,08 |
| 100 | 78,00 | 4 748,40 | 2 262,08 | 49 748,40 | 26 262,08 |
| 100 | 156,00 | 6 256,80 | 3 474,08 | 51 256,80 | 27 474,08 |
| 300 | 39,00 | 7 893,60 | 3 606,08 | 52 893,60 | 27 606,08 |
| 300 | 78,00 | 10 165,20 | 5 406,08 | 55 165,20 | 29 406,08 |
| 300 | 156,00 | 14 690,40 | 9 042,08 | 59 690,40 | 33 042,08 |

## 36 miesięcy

| Zam./mies. | Koszyk brutto | A: technologia + prowizje | B: technologia + prowizje | A: z pracą i utrzymaniem | B: z pracą i utrzymaniem |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 39,00 | 7 290,72 | 2 535,44 | 66 690,72 | 37 335,44 |
| 20 | 78,00 | 7 745,04 | 2 895,44 | 67 145,04 | 37 695,44 |
| 20 | 156,00 | 8 650,08 | 3 622,64 | 68 050,08 | 38 422,64 |
| 100 | 39,00 | 11 973,60 | 4 868,24 | 71 373,60 | 39 668,24 |
| 100 | 78,00 | 14 245,20 | 6 668,24 | 73 645,20 | 41 468,24 |
| 100 | 156,00 | 18 770,40 | 10 304,24 | 78 170,40 | 45 104,24 |
| 300 | 39,00 | 23 680,80 | 10 700,24 | 83 080,80 | 45 500,24 |
| 300 | 78,00 | 30 495,60 | 16 100,24 | 89 895,60 | 50 900,24 |
| 300 | 156,00 | 44 071,20 | 27 008,24 | 103 471,20 | 61 808,24 |

## Zakres nakładu pracy — koszyk 78 zł, stawka nadal 150 zł/h

| Zam./mies. | Miesiące | A: niski–wysoki | B: niski–wysoki |
| ---: | ---: | ---: | ---: |
| 20 | 12 | 34 381,68–60 781,68 | 18 404,48–33 404,48 |
| 20 | 36 | 46 745,04–87 545,04 | 27 495,44–53 295,44 |
| 100 | 12 | 36 548,40–62 948,40 | 19 662,08–34 662,08 |
| 100 | 36 | 53 245,20–94 045,20 | 31 268,24–57 068,24 |
| 300 | 12 | 41 965,20–68 365,20 | 22 806,08–37 806,08 |
| 300 | 36 | 69 495,60–110 295,60 | 40 700,24–66 500,24 |

## Opcja: limitowany druk płatny od miesiąca 7

Przyrost względem odpowiedniej tabeli bazowej, bez zmiany wolumenu/prowizji; zawiera wdrożenie i dodatkowe 0,5 h utrzymania/mies. od miesiąca 7.

| Horyzont | A: dodatkowo | B: dodatkowo |
| ---: | ---: | ---: |
| 12 mies. | 7 050,00 | 5 850,00 |
| 36 mies. | 8 850,00 | 7 650,00 |

## Wrażliwość na stawkę pracy — 100 zam./mies., koszyk 78 zł

| Stawka planistyczna | A: 12 mies. | B: 12 mies. | A: 36 mies. | B: 36 mies. |
| ---: | ---: | ---: | ---: | ---: |
| 0 zł/h | 4 748,40 | 2 262,08 | 14 245,20 | 6 668,24 |
| 100 zł/h | 34 748,40 | 18 262,08 | 53 845,20 | 29 868,24 |
| 150 zł/h | 49 748,40 | 26 262,08 | 73 645,20 | 41 468,24 |
| 200 zł/h | 64 748,40 | 34 262,08 | 93 445,20 | 53 068,24 |

0 zł/h pokazuje własną pracę bez wyceny czasu, nie zerowy nakład pracy.

## Próg korzyści z automatyzacji w A

Hipoteza: dodatkowa oszczędność operacyjna względem B, wartość czasu 50 zł/h, odzyskanie różnicy referencyjnego TCO w 36 miesięcy; koszyk 78 zł. To wymagany próg, nie zmierzona przewaga A.

| Zam./mies. | Różnica TCO A−B, 36 mies. | Wymagana oszczędność minut/zamówienie |
| ---: | ---: | ---: |
| 20 | 29 449,60 | 49,08 |
| 100 | 32 176,96 | 10,73 |
| 300 | 38 995,36 | 4,33 |
