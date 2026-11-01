# Źródła i decyzje prawne — projekt, 01.11.2026

Dokumenty w tym PR są materiałem do recenzji prawnej, nie zatwierdzonym regulaminem działającego sklepu. Źródła odczytano 1 listopada 2026. Status ustaw i dostawców należy sprawdzić ponownie bezpośrednio przed publikacją.

## Sprzedawca

[Odpis aktualny KRS](https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/0000997294?rejestr=P&format=json) potwierdza dane spółki; stan rejestru w odpowiedzi: 07.07.2026, wpis 11. Nazwę sądu ustalono na podstawie wpisów 1 i 6 [odpisu pełnego](https://api-krs.ms.gov.pl/api/krs/OdpisPelny/0000997294?rejestr=P&format=json), gdyż nagłówek najnowszego wpisu RDF wskazuje `SYSTEM`. Sąd: Sąd Rejonowy dla Wrocławia-Fabrycznej we Wrocławiu, VI Wydział Gospodarczy KRS. Dane w stopce obejmują firmę, siedzibę/adres, KRS/sąd, NIP i kapitał zakładowy (art. 206 KSH). REGON podmiotu: 523408785; API zwraca także rozszerzony zapis 52340878500000. [Rejestr.io](https://rejestr.io/krs/997294/pracownia-rachunkowosci) i [strona spółki](https://pracowniarachunkowosci.pl/) są źródłami pomocniczymi.

MX domeny kieruje do OVH; nie dowodzi istnienia konkretnej skrzynki. E-mail marki pochodzi ze specyfikacji i pozostaje do testu. Nie wysłano e-maili ani nie wykorzystano numeru biura rachunkowego jako telefonu sklepu.

## Prawa konsumenta

| Zakres | Podstawa / źródło | Zastosowanie w projekcie |
| --- | --- | --- |
| Odstąpienie | [UOKiK: prawo odstąpienia](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/) i [ustawa o prawach konsumenta](https://eli.gov.pl/api/acts/DU/2024/1796/text.html), art. 27–34 | 14 dni, zasady liczenia i przedłużenia, oświadczenie, odesłanie i refundacja; brak wymogu oryginalnego opakowania/paragonu |
| Personalizacja | [UOKiK: wyłączenia](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/), art. 38 ust. 1 pkt 3 | Sam druk standardowego wariantu po zamówieniu nie oznacza rzeczy indywidualnie spersonalizowanej; wyjątek wymaga rzeczywistych przesłanek |
| Reklamacje | [UOKiK: niezgodność z umową](https://prawakonsumenta.uokik.gov.pl/reklamacja/niezgodnosc/), art. 43a i nast. | Odpowiedzialność co do zasady 2 lata, naprawa/wymiana, przesłanki obniżenia ceny/odstąpienia, koszty sprzedawcy; odpowiedź w 14 dni |
| Informacja przed zakupem | [UOKiK: prawo do informacji](https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/prawo-do-informacji/) | Pełna cena i koszty, kontakt, terminy, tryb płatności i zawarcia umowy przed wiążącym zakupem; tu wyłącznie projekt |
| Konto | [PARP: konta w sklepach](https://www.parp.gov.pl/component/content/article/91265:zakladanie-konta-przez-uzytkownikow-w-sklepach-internetowych-miedzy-wygoda-biznesowa-a-ochrona-praw-konsumenta) | Propozycja zakupów i odstąpienia bez wymuszonego konta; brak fikcyjnego systemu logowania |
| GPSR | [UOKiK: bezpieczeństwo produktów](https://uokik.gov.pl/bezpieczenstwo-produktow-pytania-i-odpowiedzi), rozporządzenie UE 2023/988, art. 19 i 21 | Miejsca na producenta/kontakt, identyfikację i informacje bezpieczeństwa; QR nie zastępuje wymaganych informacji fizycznych; nie przypisano spółce niezweryfikowanej roli producenta |
| ODR | [Rozporządzenie UE 2024/3228](https://eur-lex.europa.eu/legal-content/pl/TXT/?uri=CELEX:32024R3228), [informacja Komisji](https://consumer-redress.ec.europa.eu/site-relocation_en?etrans=de&prefLang=de) | Platforma zamknięta 20.07.2025; brak starego linku ODR. ADR opisano osobno, bez fikcyjnego zobowiązania do udziału |

## Elektroniczne odstąpienie: rozdzielenie UE i Polski

[Dyrektywa UE 2023/2673](https://eur-lex.europa.eu/eli/dir/2023/2673/oj/eng) dodaje art. 11a do dyrektywy 2011/83/UE. Przewiduje łatwo dostępną funkcję odstąpienia, identyfikację konsumenta i umowy, osobne potwierdzenie zamiaru oraz potwierdzenie na trwałym nośniku z treścią, datą i godziną. Termin transpozycji to 19.12.2025, stosowania przepisów krajowych — 19.06.2026. Sam termin dyrektywy nie jest dowodem zakończenia polskiej implementacji.

W starszych materiałach widnieje UC82 / projekt nowej ustawy o kredycie konsumenckim, m.in. [strona UOKiK](https://uokik.gov.pl/bip/projekt-ustawy-o-kredycie-konsumenckim) i [omówienie PARP](https://www.parp.gov.pl/component/content/article/91021:one-click-return-czyli-zwroty-w-e-commerce-po-nowemu). Nie potraktowano tych materiałów jako dowodu obowiązującej już polskiej ustawy.

Nowszy dowód urzędowy: [odpowiedź MF na interpelację 19620 z 29.09.2026](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDYFJB7/i19620-o1.pdf), zachowana także jako [lokalna kopia PDF](sources/i19620-o1.pdf). Wskazuje projekt **UC169**, prowadzenie przez Ministra Finansów i Gospodarki we współpracy z Ministerstwem Sprawiedliwości oraz etap konsultacji. Harmonogram przewiduje Radę Ministrów w styczniu 2027, parlament w marcu–kwietniu, podpis w maju i wejście w życie w czerwcu 2027. To harmonogram projektu, nie gwarantowana data ani ogłoszona ustawa.

[Wykaz prac Rady Ministrów — UC169](https://redakcja.www.gov.pl/web/premier/projekt-ustawy-o-zmianie-ustawy-o-prawach-konsumenta-oraz-ustawy-o-konsumenckiej-pozyczce-lombardowej), pierwsza publikacja 09.09.2026, opisuje funkcję elektronicznego odstąpienia w tym projekcie.

Wniosek roboczy: zbadane źródła wskazują trwającą implementację; nie dają podstaw do bezwarunkowego twierdzenia, że wszystkie obowiązki krajowe już obowiązują albo że ich nie ma. Przed startem trzeba sprawdzić finalny tekst w Dzienniku Ustaw, przebieg UC169 i ewentualne późniejsze akty. Przygotowany dwustopniowy interfejs jest demonstracją; [plan backendu i odbioru](DATA_AND_WITHDRAWAL.md) pozostaje odrębnym zadaniem wdrożeniowym.

## Prywatność i marketing

Projekt odwołuje się do art. 6 ust. 1 lit. a/b/c/f RODO zależnie od celu, prawa do skargi do Prezesa UODO i właściwych praw osoby. Marketing elektroniczny wymaga osobnego uwzględnienia art. 398 Prawa komunikacji elektronicznej. Okresy księgowe podano z zastrzeżeniem właściwych reguł liczenia i przedłużenia; retencja sporów i procesorzy wymagają decyzji przed wdrożeniem.

Kod zastany zawiera GA4 i Brevo; nie potwierdzono umów, konfiguracji kont ani transferów. Projekt uczciwie odróżnia zastaną produkcję, izolowany podgląd i planowany sklep. Nie wpisano fikcyjnego operatora płatności ani aktywnego przewoźnika. Szczegóły audytu skryptów i jego ograniczenia: [AUDIT.md](AUDIT.md).
