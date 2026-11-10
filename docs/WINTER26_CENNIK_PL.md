# WINTER 26 — polski cennik ozdób i zestawów i kod WINTER10

Decyzja handlowa z 10.11.2026, przed uruchomieniem sklepu. Ceny w PLN brutto. Ten dokument zastępuje wcześniejsze propozycje cen i progów dostawy dla Polski.

| Wybrany produkt | Bez kodu | Z WINTER10 | Rabat na wybrany produkt | Kurier krajowy przy takim zamówieniu |
| --- | ---: | ---: | ---: | --- |
| Pojedyncza ozdoba | 50 zł | 40 zł | 10 zł | płatny osobno |
| Zestaw 2 | 84 zł | 74 zł | 10 zł | płatny osobno |
| Zestaw 4 | 150 zł | 140 zł | 10 zł | płatny osobno |
| **Zestaw 6 — wyróżniony** | **220 zł** | **210 zł** | **10 zł** | **w cenie** |
| Zestaw 8 — opcjonalny | 290 zł | 280 zł | 10 zł | w cenie |

- Kod odejmuje 10 zł **od każdej ozdoby kupionej pojedynczo i od każdego kompletnego zestawu**. W obrębie zestawu rabat nalicza się raz, bez względu na liczbę ozdób. Kod wystarczy wpisać raz; nie obejmuje kosztu dostawy. Zestaw to produkt wybrany przez klienta: nie grupujemy samodzielnych sztuk w pakiety bez jego wyboru.
- Jedna cena obejmuje dowolną kombinację i powtórzenia trzech modeli: VASE (w katalogu: FULL SOFT, identyfikator `full-soft`), KNITTED STAR i jednostronny KNITTED MEDALLION. HELIX OPEN nie ma ceny w tej ofercie.
- Pokazujemy przede wszystkim zestaw sześciu do własnej kompozycji; zdjęcie może przedstawiać po dwie sztuki każdego wzoru. Płaskie modele nie są tańsze. Ósemka nie ma dodatkowego rabatu ilościowego.
- Kurier InPost w Polsce jest w cenie od **6 ozdób łącznie** w zamówieniu, również bez kodu. Dla 1–5 sztuk stawka dla klienta nie została jeszcze ustalona. Nie podstawiamy tu kosztu własnego przesyłki ani 0 zł.
- Przykłady: zestaw 4 + zestaw 2: 234 zł bez kodu, **214 zł z kodem, kurier w cenie**. Zestaw 6 + pojedyncza ozdoba: 270 zł bez kodu, **250 zł z kodem, kurier w cenie**. Dwie ozdoby kupione pojedynczo kosztują 100 zł bez kodu lub 80 zł z kodem; duet 84 zł bez kodu, a 74 zł z kodem.

## Cena bez kodu i historia obniżek

Cena bez kodu jest planowaną ceną sprzedaży. Nie stanowi dowodu ceny historycznej, a wpis w repozytorium nie rozpoczyna okresu oferowania. Publiczny kod na wskazane ozdoby i zestawy to komunikowanie obniżki: obok ceny z kodem należy pokazać najniższą cenę danego produktu (pojedynczej ozdoby albo zestawu) z 30 dni przed obniżką (przy krótszym okresie oferowania — od początku oferowania do obniżki). Komunikowana oszczędność musi wynikać z tego porównania. Nie ogłaszamy fikcyjnego „było / jest”. Przed akcją sprawdzamy faktyczną, udokumentowaną historię cen pojedynczych ozdób i zestawów w danym kanale. Bez wcześniejszej oferty startujemy z jedną rzeczywistą ceną bez sugerowania obniżki.

Źródła: [UOKiK — informacje o obniżkach cen](https://prawakonsumenta.uokik.gov.pl/prawo-do-informacji/informacje-o-obnizkach-cen/) i [wyjaśnienia Prezesa UOKiK dotyczące m.in. publicznych kodów](https://uokik.gov.pl/Download/95).

## Zastosowanie w sklepie

Źródło kwot i kodu: [data/winter26-pricing-pl.json](../data/winter26-pricing-pl.json). [Kalkulator](../scripts/winter26_pricing.py) zwraca kwoty brutto w groszach i zachowuje granice wybranych zestawów. Nie publikuje cen ani nie pobiera opłat.

Przy wdrożeniu serwer ma sam sprawdzić SKU i zarezerwować skład, zweryfikować okres aktywnej promocji, wycenić wybrane single, pełne zestawy oraz dostawę, a następnie przekazać ostateczne kwoty do Stripe. Nie stosować dodatkowo kuponu do już pomniejszonej kwoty. Nieznana stawka kuriera w małym zamówieniu blokuje wyliczenie kwoty do zapłaty. Przed uruchomieniem sprawdzić w Sandbox m.in. koszyk z dwoma zestawami i zestaw z singlem. Sam zapis cennika nie aktywuje przedsprzedaży, rabatu publicznego ani Stripe Live.
