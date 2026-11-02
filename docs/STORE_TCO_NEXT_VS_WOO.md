# Pracownia Form: Next.js / Vercel / Stripe vs WordPress / WooCommerce / Przelewy24

**Raport do Issue #6 · data sprawdzenia źródeł: 2 listopada 2026 · analiza odebrana w recenzji; hosting i wdrożenie wymagają osobnej decyzji.**

Po [recenzji odbiorowej](https://github.com/pracowniarachunkowosci-debug/form/pull/7#pullrequestreview-5738562410) dodano [shortlistę LH.pl Apple / MyDevil MD2](WOO_HOSTING_SHORTLIST.md), ceny odnowienia oraz brakujące potwierdzenia Action Scheduler. Nie zmienia ona bazowych założeń kalkulatora ani nie zatwierdza zakupu usług.

## 1. Rekomendacja dla tej firmy

**Na pierwszą sprzedaż rekomenduję B: WooCommerce + własny motyw R04 + Przelewy24 + oficjalny InPost PL.** Bazowy punkt odniesienia cenowego to **nowy OVH Pro**, MySQL i Brevo. **Hosting i architektura schedulera pozostają do wyraźnego zatwierdzenia właściciela** po przeglądzie bezpieczeństwa i niezawodności; preferowany jest natywny cron co 1–5 min. OVH Pro z zewnętrznym triggerem nie jest zatwierdzonym wyborem. Zachować statyczne strony marki, a sklep uruchomić pod `/sklep/` na tym samym hostingu. Nie trzeba przenosić całej strony do WordPressa. [Aneks po recenzji](#12-aneks-po-recenzji--symetryczne-p24-wydatki-i-hosting) pokazuje także Next + bezpośrednie P24, mniejsze zużycie Neon i droższy hosting Woo.

Powody wynikają z zakresu i audytu: cztery modele, mały magazyn, krajowa sprzedaż z BLIK, potrzebny panel zamówień i brak gotowego backendu magazynowego w `dietologicznie`. Przy koszyku 78 zł i 100 zamówieniach/mies. technologia oraz prowizje kosztują w modelu **4 748,40 zł dla A vs 2 262,08 zł dla B w 12 miesięcy**. Z referencyjnym nakładem pracy i utrzymaniem: **49 748,40 vs 26 262,08 zł**, a w 36 miesięcy **73 645,20 vs 41 468,24 zł**. To model ekonomiczny, nie oferta wykonania ani wycena pracy Codexa. **Kwoty z wyceną pracy nie są wymaganą wpłatą z góry ani prognozą faktur przy pracy własnej z AI.** Pełne założenia, nieznane koszty i wszystkie scenariusze są poniżej.

**A pozostaje uzasadnione**, jeśli firma zapewni stałego opiekuna TypeScript i potrzebuje własnego konfiguratora/automatyzacji dającej zmierzone oszczędności albo wspólny, rzeczywiście kompletny backend dla kilku marek. Sam wzrost do 300 zamówień miesięcznie oraz sam wygląd R04 nie uzasadniają zmiany na A. Oba rozwiązania mogą zachować design i obsłużyć CZ/ES. W tej parze także operator płatności wpływa na wynik: Next.js nie wymusza Stripe, a Woo nie wyklucza Stripe.

Zakres prac tego PR to **wyłącznie analiza i powtarzalny kalkulator**. Nie zmienia PR #5, strony, DNS, usług, danych klientów ani aktywnych integracji. Nie kupiono hostingu, nie utworzono kont i nie uruchomiono płatności. Bazą jest `main` `38e0bd9bc8296b70ac68d92753d63f447d70df3e`; stan PR #5 przy audycie: draft, `f97fcd65f2625dcc4f18aabf65c3a8e467a5a947`.

## 2. Stan faktyczny i wynik audytu dietologicznie

Według [Issue #6](https://github.com/pracowniarachunkowosci-debug/form/issues/6) domena i poczta są w OVH, **bez aktywnego hostingu WWW**. Nie traktuję poczty, domeny ani istniejącego GitHub Pages jako opłaconego zaplecza sklepu. Nie logowano się do paneli OVH, Stripe czy Vercel: ich faktycznych planów, uprawnień, limitów i aktywowanych metod nie potwierdzono. Dokument z PR #5 był punktem odniesienia, nie rozstrzygnięciem tego porównania.

Audyt `dietologicznie`: statyczny odczyt `main` **`73dd4bbce6345b9371e020686389ed35e134c468`**. Przejrzano manifest, wszystkie trasy API, koszyk, produkty, dostawę, webhook, stronę sukcesu, middleware i zgody. Nie uruchamiano aplikacji ani nie wykonywano płatności. Repozytorium jest prywatne: linki dowodowe wymagają dostępu; raport nie kopiuje kodu, sekretów, klientów, identyfikatorów kont ani danych płatności.

| Element i dowód w kodzie | Faktyczny stan | Co można wykorzystać w Pracowni Form |
| --- | --- | --- |
| [package.json](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/package.json) | Next 16.3.3, React 19.2.4, Stripe SDK; brak klienta bazy i migracji w sprawdzonym drzewie | Sposób organizacji Next, nie kopiowanie całego manifestu. Dobrać aktualne, zgodne wersje i wyrównać tooling; brak testów aplikacji w skryptach manifestu |
| [lib/features.ts:4](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/lib/features.ts#L4), [middleware.ts:5](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/middleware.ts#L5) | `FEATURE_COOKIE_SHOP = false`; sklep przekierowywany, API checkout zwraca 503 | Wzorzec kontrolowanego wyłączania, nie dowód gotowości sprzedażowej |
| [CartContext.tsx:54](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/contexts/CartContext.tsx#L54) | Koszyk w localStorage, synchronizacja kart przeglądarki | Punkt wyjścia do UI koszyka. Nowe SKU/warianty, walidacja ilości i stan serwerowy; localStorage nie jest rezerwacją magazynu |
| [checkout/route.ts:77](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/app/api/checkout/route.ts#L77) | Ceny odczytywane z katalogu po stronie serwera, tworzenie sesji i metadata dostawy | Użyteczny szkielet adaptera Stripe. Dodać trwały numer zamówienia, transakcję rezerwacji, idempotency key, limity wejścia, obsługę przerwanej sesji i błędów |
| [webhooks/stripe/route.ts:24](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/app/api/webhooks/stripe/route.ts#L24) | Weryfikuje podpis na surowym body; następnie loguje zdarzenia | Zachować wzorzec weryfikacji. Do napisania trwałe przetwarzanie, deduplikacja, stany, retry, uzgadnianie płatności, zwroty i powiadomienia. Log nie zastępuje zamówienia |
| [sukces/page.tsx:10](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/app/sukces/page.tsx#L10) | Sprawdza sesję Stripe i `payment_status` po stronie serwera | Dobry wzorzec potwierdzenia w UI; realizacja zamówienia musi działać także bez powrotu klienta na tę stronę |
| [InpostGeowidget.tsx:33](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/components/InpostGeowidget.tsx#L33), [shipping.ts:78](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/lib/shipping.ts#L78) | Integracja web component z React, wybór kodu i etykiety punktu, obsługa ładowania | Najbardziej bezpośredni materiał do adaptacji A. Testować aktualną wersję widgetu, punkt i adres po stronie serwera. To **nie** ShipX, generowanie etykiet, śledzenie ani obsługa zagranicy |
| [shipping.ts:3](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/lib/shipping.ts#L3), [lib/promo.ts](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/lib/promo.ts) | Reguły dostawy i promocji właściwe sklepowi z ciastkami | Nie przenosić stawek, progu darmowej dostawy, promocji 5+1, katalogu, zdjęć i treści prawnych |
| [CookieConsent.tsx:10](https://github.com/pracowniarachunkowosci-debug/dietologicznie/blob/73dd4bbce6345b9371e020686389ed35e134c468/components/CookieConsent.tsx#L10) | Inny klucz zgód i wartości niż w Form, możliwość zmiany decyzji | Można wykorzystać koncepcję ustawień, ale konieczna jawna migracja `pf_cookie_consent` z Form. Nie kopiować konfiguracji analityki ani resetować zgody do „granted” |
| Całe `app/api`, `lib`, `contexts`, `scripts` | Nie znaleziono trwałej bazy zamówień/stanów, panelu sklepu, backendu ShipX, eksportu faktur, wysyłki transakcyjnej, rezerwacji produkcji ani testów E2E sklepu | Te obszary trzeba zbudować. Istnienie Payment Links dla usług na stronie głównej nie dowodzi kompletności sklepu fizycznego |

**Szacunek korzyści z ponownego użycia: 12–24 h w A**, głównie koszyk, Geowidget i szkielety Stripe. To ocena prac, nie zmierzony wynik ani deklarowany procent gotowości. Widełki wdrożenia niżej **już uwzględniają** tę oszczędność — nie odejmować jej drugi raz. W B komponenty React nie są potrzebne: przejmujemy wnioski i przypadki testowe, integracje zapewniają moduły. Przed faktycznym przenoszeniem kodu/zasobów potwierdzić prawa do nich; brak publicznej licencji nie daje samodzielnie prawa do dowolnego użycia.

## 3. Dwie konkretne architektury i zachowanie R04

### A — Next.js + Vercel Pro + Neon PostgreSQL + Stripe + InPost + Brevo

Konwersja zatwierdzonego HTML/CSS do komponentów Next; większość strony renderowana statycznie lub na serwerze, klientowy JS tylko dla koszyka, wyboru wariantu i mapy. Zachować hero AVIF/WebP, kadrowanie, typografię, kolorystykę i układ R04. Nie stosować designu `dietologicznie`. Publiczne trasy `.html` mogą zostać obsłużone statycznie/rewrites; nie zmieniać URL-i tylko dlatego, że zmienił się framework.

Neon **Launch**, PostgreSQL w regionie UE blisko funkcji Vercel, połączenie z poolingiem. W bazie: produkty/warianty/SKU, dostępność, zamówienie z ceną i terminem w chwili zakupu, pozycje, rezerwacje, zdarzenia płatnicze, przesyłki, zwroty i kolejka zadań. Zapisu nie opieramy na RAM funkcji, metadata Stripe ani logach. Panel pracowni z rolami i MFA, eksportem i historią operacji trzeba stworzyć. Do czterech modeli nie jest konieczny płatny CMS; zdjęcia można początkowo wersjonować, a edycję zdjęć przez panel/storage wycenić przy rozszerzaniu.

Checkout: serwer wylicza ceny, atomowo rezerwuje warianty, tworzy zamówienie oczekujące i sesję Stripe z kluczem idempotencji. Podpisany webhook zapisuje unikalne zdarzenie i zmienia stan; trwały outbox uruchamia e-mail i dalsze czynności, z retry i alertem. Cykl uzgadniania wyłapuje spóźnione/brakujące zdarzenia. Stripe opisuje konieczność webhooków niezależnie od strony sukcesu. [Realizacja Checkout][S8].

InPost: Geowidget + oddzielna integracja ShipX na serwerze do etykiet/statusów, z ponowieniem bez duplikowania paczek. Brevo API/SMTP wysyła transakcyjne wiadomości, bez automatycznego dopisywania do listy marketingowej. Własny panel nie powinien wymagać rutynowego szukania jednego zamówienia w Stripe, bazie i logach.

R04 można zachować na stronie i w koszyku. **Hostowany Stripe Checkout ma własny układ i ograniczone opcje brandingu**, więc nie obiecuję zgodności pikselowej całej płatności; logo i kolory są możliwe. Niestandardowy formularz płatności zwiększyłby zakres A. [Personalizacja Checkout][S9].

### B — WordPress + WooCommerce na OVH Pro + Przelewy24 + InPost PL + Brevo

Nowy OVH Pro: PHP/MySQL, własny lekki motyw bez abonamentowego page buildera. WordPress w `/sklep/`, istniejące pliki HTML/CSS/JS w katalogu głównym. Koszyk, checkout, zamówienia, edycja wariantów, role i powiadomienia pochodzą z Woo. Własna mała wtyczka zawiera wyłącznie logikę specyficzną dla Form; nie zmieniać kodu Woo ani modułów operatorów. Używać ich API, sprawdzić kompatybilność HPOS i wybranego typu checkoutu.

Kandydat OVH Pro ma 1 vCore, 2 GB RAM i bazy po 2 GB. Dokumentacja OVH opisuje PHP-FPM z limitem pamięci 512 MB; Woo zaleca m.in. MySQL ≥8.0/MariaDB ≥10.6 i pamięć WordPress ≥256 MB. **To weryfikacja dokumentacji, nie test niezakupionego serwera:** przed zakupem potwierdzić bieżącą wersję bazy/PHP w nowej ofercie i przed uruchomieniem sprawdzić raport systemowy Woo, limity połączeń, obciążenie checkoutu oraz odtwarzanie. Wersji wbudowanej bazy OVH nie można dowolnie zmienić. Nie wystarczy stwierdzenie „hosting ma instalator WordPress”. [OVH — parametry][S5], [Woo — wymagania][S6].

**Ograniczenie OVH:** jego panelowy cron wykonuje zadanie najwyżej raz na godzinę. WP-Cron zależny od wejść na stronę również nie gwarantuje punktualności przy 20 zamówieniach miesięcznie. Pierwotny model cenowy B zakładał bezpłatny trigger `cron-job.org` co 5 min i godzinowy fallback OVH. **Po recenzji to wyłącznie opcja wymagająca przeglądu, nie zatwierdzona architektura obsługi zamówień.** FAQ schedulera wskazuje brak walidacji certyfikatów TLS, timeout i brak gwarancji punktualności. Nie przekazywać mu PII, sekretów ani uprawnień administracyjnych. Nawet wywołanie publicznego WP-Cron może uruchomić wrażliwe zadania serwerowe: brak sekretu w URL nie jest dowodem bezpieczeństwa całej ścieżki. Preferować hosting z natywnym cron 1–5 min; jeśli pozostajemy przy OVH, przed zakupem potwierdzić bezpieczny scheduler, idempotencję, limity wykonania i testy bez ruchu. Szczegółowe warunki oraz wpływ droższego hostingu na TCO zawiera aneks. Nie zakładam, że droższy plan OVH automatycznie usuwa ograniczenie. [OVH cron][S7], [Woo Scheduled Actions][S10], [cron-job.org][S11].

Oficjalne moduły P24 i InPost są bezpłatne; integracja i testowanie wymagają pracy. Moduł P24 deklaruje obsługę Woo 9–11, co nie zwalnia ze sprawdzenia konkretnej wersji i checkoutu. InPost PL obejmuje ShipX i etykiety. [P24][S12], [InPost][S13]. Faktury/KSeF realizuje uzgodniony system księgowy, nie sam dokument PDF z dowolnej wtyczki.

### Czy cały frontend musi być WordPressem?

| Wariant | Konsekwencje | Ocena |
| --- | --- | --- |
| Statyczne strony i Woo `/sklep/` na jednym OVH | Jeden origin, jeden certyfikat, lokalne linki `.html`; wspólne źródło wyglądu, dwa renderery. Nawigację/stopkę i zgodę trzeba utrzymywać spójnie; koszyk poza sklepem najwyżej jako link na start | **Rekomendowany dla B**, najmniej zmian zatwierdzonej strony |
| Front na Vercel, Woo na `sklep.pracowniaform.com` | Dwa hostingi, drugi origin, osobny localStorage zgód, pomiar przejścia między serwisami. Checkout na subdomenie; poprawnie skonfigurować sesję i SSL | Technicznie możliwe, ale dodatkowy koszt i testy. Nie dziedziczy automatycznie zgód z głównej domeny |
| Front osobno, Woo pod `/sklep/` przez reverse proxy | DNS nie rozdziela ruchu po ścieżce. Potrzebny proxy/router; trzeba obsłużyć cookies, nagłówki hosta, przekierowania, cache i adresy zasobów | Nie rekomenduję na start |
| Next jako headless frontend do Woo | Osobne API koszyka, sesje, przebudowa checkoutu i zgodności wtyczek; dwa stosy | Nie jest „darmowym połączeniem zalet” A i B; poza modelem |

## 4. Cenniki i założenia kosztowe

Kwoty publiczne sprawdzone **02.11.2026**, nie odczytane z prywatnych umów. Promocja nie jest ceną odnowienia. Kurs **4,00 PLN/USD jest założeniem budżetowym**, nie kursem NBP ani gwarancją płatności kartą. Porównanie ekonomiczne używa kwot netto usług/pracy przy założeniu odliczalnego VAT; prowizje w kwotach podanych przez operatorów. Status VAT spółki i rozliczenie importu usług ustala księgowość.

| Pozycja | Wartość publiczna / przyjęty budżet | Traktowanie w TCO |
| --- | --- | --- |
| Vercel Pro | 20 USD/mies. przy jednym płatnym miejscu, 20 USD kredytu użycia; dodatkowe zasoby/miejsca płatne. Hobby jest niekomercyjne | A: 80 zł/mies. netto przy kursie modelu; **nie** 20 USD + kolejne 20 za ten sam wliczony kredyt. Zakładamy użycie w limicie; przekroczenia osobno [S1] [S2] |
| Neon Launch | 0,106 USD/CU-h + 0,35 USD/GB-mies.; historia 0,20 USD/GB-mies., do 7 dni. Obecny cennik mówi o braku minimum miesięcznego | A: **budżet 20 USD/mies.**, nie abonament: przykładowo 0,25 CU × 730 h × 0,106 + 1 GB × 0,35 + 1 GB historii × 0,20 = 19,895 USD. Snapshots/ponadlimity dodatkowo [S3] |
| Brevo transakcyjne | Free: 300 wysyłek/dzień, wspólny limit i branding; przekroczenie może opóźniać wiadomości | A i B: 0 zł przy założeniu dostępnego limitu, konfiguracji nadawcy i aktywnej usługi SMTP/API; nie zakładam, że samo posiadanie formularza to potwierdza [S4] |
| OVH Pro | Promocja 101,88 zł netto / pierwsze 12 mies.; odnowienie 42,59 zł netto/mies. = **511,08 zł netto/rok**, 628,63 zł brutto przy 23% VAT | B: 42,59 zł/mies. ekwiwalentu w całym TCO. Faktura roczna, nie deklaracja płatności miesięcznej; promocja pokazana oddzielnie [S5a] |
| Woo + własny motyw; P24; InPost PL | Core i wskazane oficjalne moduły bez abonamentu; motyw ma koszt wykonania | B: 0 zł licencji, robocizna oddzielnie [S12] [S13] [S14] |
| Scheduler B | cron-job.org 0 zł, z ograniczeniami; fallback OVH w hostingu | 0 zł, konfiguracja/monitorowanie w godzinach utrzymania [S11] |
| Kopia poza głównym kontem | **Rezerwa planistyczna 10 zł/mies.** na przechowywanie małych szyfrowanych kopii; nie cena konkretnego pakietu | A i B: 10 zł/mies. Dostawcę, retencję i faktyczną cenę potwierdzić; praca odzyskiwania jest osobno |
| Aktywacja P24 | 59 zł, zwrot po 10 transakcjach w pierwszych 2 miesiącach | B: konserwatywnie +59 zł jednorazowo; po spełnieniu warunków odjąć 59, nie mnożyć przez lata [S15] |
| Zestawy ze wspólnym stanem komponentów | Opcjonalny Woo Product Bundles 79 USD/rok, czyli 316 zł/rok przed podatkami przy kursie modelu | Niepotrzebny w prostym MVP; przy wyborze doliczyć 316/948 zł na 12/36 mies. i testy. Nie korzystamy z promocji dwuletniej [S16] |
| Wysyłka InPost | Publiczne Szybkie Nadania A/B/C: 16,49/18,49/20,49 zł **brutto**. Umowa firmowa, paliwo, gabaryty, odbiór i zagranica: **do wyceny** | Nie wliczamy przesyłek do opłaty integracji ani do tabeli technologicznej. Cennik detaliczny nie jest ofertą ShipX dla tej firmy [S17] |
| Księgowość/faktury, domena i istniejąca poczta OVH | Cena z umowy/wybranego systemu, brak dostępu do faktur | **Do wyceny** jako wspólny składnik U; nie przyjmujemy fikcyjnego „darmowego KSeF” ani nie kupujemy drugiej poczty |

Stały budżet technologiczny: **A 170 zł/mies.**, **B 52,59 zł/mies.** (hosting/baza + 10 zł kopii). Usługi porównywane na 12/36 miesięcy, bez inflacji i dyskonta. Gdy VAT nie podlega odliczeniu, trzeba doliczyć właściwe podatki do usług: sama analogia 23% daje odpowiednio 209,10 i 64,69 zł/mies.; nie wolno automatycznie pomnożyć całej tabeli TCO przez 1,23, szczególnie prowizji. Promocyjne OVH 101,88 zł netto odpowiada 125,31 zł brutto; przy jego rzeczywistej dostępności TCO B spada o **409,20 zł** w każdym horyzoncie.

**Ruch i poczta:** zamówienia nie wyznaczają kosztu Vercel ani bazy. Zakładamy niewielki ruch, statyczne strony, brak wideo i ciężkich zadań; przed startem wykonać test kampanii i ustawić alert kosztów. Neon Free jest tańszą możliwością, ale nie zastępuje przyjętej retencji/odzyskiwania. Budżet Launch należy zastąpić zmierzonym zużyciem. Przy 4 e-mailach na zamówienie 300 zam./mies. to 1 200 wiadomości, lecz 75 zamówień w dzień zużywa cały limit Brevo **przed** kampanią premierową. W takim dniu potrzebny płatny plan/liczba kredytów **do wyceny** albo oddzielenie transakcyjnej wysyłki. Przykład alternatywy dla obu: Resend Pro 20 USD/mies. / 50 tys. wiadomości bez limitu dziennego, czyli +960/+2 880 zł w modelu 12/36 miesięcy; nie jest konieczny równolegle z wystarczającym Brevo. [Resend][S18].

### Prowizje: BLIK, karta, przelew i zwrot

Stripe Polska: BLIK **1,6% + 1 zł**, standardowa karta EOG **1,5% + 1 zł**, przelew P24 przez Stripe **1,9% + 1 zł**. Bezpośrednie P24: BLIK/przelew/karta 3DS **1,29% + 0,30 zł**. To różne umowy — nie przypisujemy Stripe ceny bezpośredniego P24. [Stripe][S19], [P24][S15].

Miks bazowy to **założenie 70% BLIK / 20% standardowych kart EOG / 10% przelewów**, nie zmierzone zachowanie klientów. N oznacza liczbę opłaconych transakcji; nominalne 39/78/156 zł to **pełna kwota obciążenia klienta**, nie zatwierdzone ceny produktów. Jeśli to ceny samych produktów i pobieramy S zł za wysyłkę, prowizję należy liczyć od `koszyk + S`, mimo że koszt przewoźnika jest poza tą tabelą. Przy 100% BLIK należy użyć kolumny BLIK zamiast średniej.

P24 ma 4 darmowe wypłaty PLN/mies. na polski rachunek, następne po 0,99 zł. Model zakłada ≤4; 20 wypłat/mies. dodaje 15,84 zł/mies. (190,08/570,24 zł). Standardowa obsługa zwrotu P24 to 0 zł z wyjątkami w przypisie; nie oznacza to automatycznie oddania pierwotnej prowizji. Stripe nie zwraca pierwotnych opłat processingowych; dodatkowe koszty zależą od metody/umowy. Model nie obniża kosztu już opłaconej transakcji po zwrocie. Spory, chargebacki, FX i dodatkowe opłaty zwrotów pozostają oddzielną pozycją rzeczywistą, nie ukrytym zerem. [P24][S15], [zwroty Stripe][S20].

## 5. Nakład pracy i zakres porównywalnego MVP

Szacunki autora dla wdrożenia, integracji i odbioru; **nie oferta ani pomiar czasu pracy Codexa**. Dotyczą tego samego MVP: cztery modele i ograniczone warianty, PLN/PL, single i proste zestawy 2/4, gotowy magazyn, panel, wysyłka, zwrot częściowy, eksport księgowy i testy. Nie obejmują fotografii, modelowania produktów, tworzenia tekstów prawnych przez prawnika, zagranicznych tłumaczeń ani płatnego druku z kolejką — ten ma osobną wycenę przyrostu. Kwoty są jawne także przy stawce 0 zł/h, jeśli firma wykonuje pracę własnymi zasobami.

| Zadanie | A: godziny | B: godziny |
| --- | ---: | ---: |
| R04: komponenty Next / motyw sklepu Woo, mobile i dostępność | 20–32 | 20–32 |
| Katalog, warianty/SKU, baza, proste zestawy | 24–40 | 8–16 |
| Koszyk, Checkout, webhooki, błędy płatności | 24–40 | 8–12 |
| Rezerwacje, panel zamówień/magazynu, zwroty i częściowe zwroty | 48–80 | 12–20 |
| InPost, etykiety/statusy i ponawianie błędów | 16–28 | 6–10 |
| E-maile, podstawowy eksport do ustalonej księgowości | 16–28 | 10–18 |
| Hosting, role/MFA, backup/restore, kolejki, monitoring | 16–28 | 12–20 |
| Testy E2E, regresja SEO/zgód, przygotowanie migracji i instrukcja | 24–40 | 16–28 |
| **Razem; referencyjnie** | **188–316; 252** | **92–156; 124** |
| Utrzymanie techniczne miesięcznie; referencyjnie | **2–6; 4** | **2–5; 3** |

Utrzymanie A: zależności/security, webhooki, kolejki, koszty chmurowe, baza, restore i poprawki własnego kodu. B: aktualizacje WP/Woo/PHP/modułów najpierw na stagingu, zgodność checkoutu/HPOS, cron, backup i restore. Oba wymagają opiekuna; automatyczne aktualizacje nie są całym utrzymaniem. Widełki obejmują rutynową kontrolę, nie poważne incydenty, całodobowy dyżur i rozwój funkcji.

Referencyjna stawka planistyczna: **150 zł/h netto** dla obu. Nakład jednorazowy: A 37 800 zł, B 18 600 zł. Miesięczne utrzymanie: A 600 zł, B 450 zł. Własna praca może nie powodować faktury, ale zużywa czas; ceny zewnętrznego wykonawcy dopiero **do wyceny**. Osobno codzienna obsługa: pakowanie, reklamacje i księgowanie. Przykładowe 5 min administracji na zamówienie przy wartości czasu 50 zł/h dodaje obu wariantom 4,17 zł/zam.; to założenie, a nie przewaga którejkolwiek platformy.

## 6. TCO 12/36 miesięcy — wzory i pełne scenariusze

```text
fee(method, basket) = round_half_up(rate × pełna_kwota_brutto + flat, 0,01)
fee_mix = 0,70 × fee_BLIK + 0,20 × fee_karta_EOG + 0,10 × fee_przelew
technologia(M,N,V) = M × koszt_stały + M × N × fee_mix(V) + aktywacja
TCO_model = technologia + godziny_wdrożenia × stawka + M × godziny_utrzymania × stawka
TCO_do_budżetu_firmy = TCO_model + U + wybrane_dodatki + nieodliczalne_podatki
```

`U` = rzeczywiste koszty domeny/poczty, księgowości/fakturowania, przeglądu prawnego oraz codziennej obsługi, których nie potwierdzono. Koszty fizycznej produkcji, filamentu/energii, opakowań, przewoźnika i zwracanej wartości towaru są kosztami działalności, **nie opłatami silnika sklepu**; wymagają oddzielnej kalkulacji marży. Tabela nie jest całkowitym budżetem firmy. Oba warianty liczymy identycznie bez nieznanych pozycji; dla decyzji trzeba uzupełnić różnice `U_A−U_B`, jeśli wystąpią. Nie doliczamy drugi raz przeglądu technicznego uwzględnionego w godzinach.

Poniższe liczby generuje [kalkulator](../scripts/store_tco.py) z [jawnych założeń](store-tco/assumptions.json). Wyniki maszynowe: [results.json](store-tco/results.json). Model zaokrągla **każdą prowizję przed ważeniem**, a nie zaokrągloną średnią razy liczbę zamówień. Faktyczne zasady zaokrągleń potwierdzić w rozliczeniu operatora.

<!-- BEGIN GENERATED TCO -->

### Prowizja od jednej opłaconej transakcji

| Koszyk brutto | A: BLIK | A: karta EOG standard | A: przelew P24 przez Stripe | B: BLIK/karta 3DS/przelew | A: średnia miksu* | B: średnia miksu |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 39,00 | 1,62 | 1,59 | 1,74 | 0,80 | 1,6260 | 0,8000 |
| 78,00 | 2,25 | 2,17 | 2,48 | 1,31 | 2,2570 | 1,3100 |
| 156,00 | 3,50 | 3,34 | 3,96 | 2,31 | 3,5140 | 2,3100 |

*Średnia ważona 70% BLIK / 20% standardowych kart EOG / 10% przelewów; nie zaokrąglamy średniej przed mnożeniem przez liczbę transakcji. Każda pojedyncza prowizja zaokrąglana do grosza HALF_UP jako jawne założenie modelu.

### 12 miesięcy

| Zam./mies. | Koszyk brutto | A: technologia + prowizje | B: technologia + prowizje | A: z pracą i utrzymaniem | B: z pracą i utrzymaniem |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 39,00 | 2 430,24 | 882,08 | 47 430,24 | 24 882,08 |
| 20 | 78,00 | 2 581,68 | 1 004,48 | 47 581,68 | 25 004,48 |
| 20 | 156,00 | 2 883,36 | 1 244,48 | 47 883,36 | 25 244,48 |
| 100 | 39,00 | 3 991,20 | 1 650,08 | 48 991,20 | 25 650,08 |
| 100 | 78,00 | 4 748,40 | 2 262,08 | 49 748,40 | 26 262,08 |
| 100 | 156,00 | 6 256,80 | 3 462,08 | 51 256,80 | 27 462,08 |
| 300 | 39,00 | 7 893,60 | 3 570,08 | 52 893,60 | 27 570,08 |
| 300 | 78,00 | 10 165,20 | 5 406,08 | 55 165,20 | 29 406,08 |
| 300 | 156,00 | 14 690,40 | 9 006,08 | 59 690,40 | 33 006,08 |

### 36 miesięcy

| Zam./mies. | Koszyk brutto | A: technologia + prowizje | B: technologia + prowizje | A: z pracą i utrzymaniem | B: z pracą i utrzymaniem |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 39,00 | 7 290,72 | 2 528,24 | 66 690,72 | 37 328,24 |
| 20 | 78,00 | 7 745,04 | 2 895,44 | 67 145,04 | 37 695,44 |
| 20 | 156,00 | 8 650,08 | 3 615,44 | 68 050,08 | 38 415,44 |
| 100 | 39,00 | 11 973,60 | 4 832,24 | 71 373,60 | 39 632,24 |
| 100 | 78,00 | 14 245,20 | 6 668,24 | 73 645,20 | 41 468,24 |
| 100 | 156,00 | 18 770,40 | 10 268,24 | 78 170,40 | 45 068,24 |
| 300 | 39,00 | 23 680,80 | 10 592,24 | 83 080,80 | 45 392,24 |
| 300 | 78,00 | 30 495,60 | 16 100,24 | 89 895,60 | 50 900,24 |
| 300 | 156,00 | 44 071,20 | 26 900,24 | 103 471,20 | 61 700,24 |

### Zakres nakładu pracy — koszyk 78 zł, stawka nadal 150 zł/h

| Zam./mies. | Miesiące | A: niski–wysoki | B: niski–wysoki |
| ---: | ---: | ---: | ---: |
| 20 | 12 | 34 381,68–60 781,68 | 18 404,48–33 404,48 |
| 20 | 36 | 46 745,04–87 545,04 | 27 495,44–53 295,44 |
| 100 | 12 | 36 548,40–62 948,40 | 19 662,08–34 662,08 |
| 100 | 36 | 53 245,20–94 045,20 | 31 268,24–57 068,24 |
| 300 | 12 | 41 965,20–68 365,20 | 22 806,08–37 806,08 |
| 300 | 36 | 69 495,60–110 295,60 | 40 700,24–66 500,24 |

### Opcja: limitowany druk płatny od miesiąca 7

Przyrost względem odpowiedniej tabeli bazowej, bez zmiany wolumenu/prowizji; zawiera wdrożenie i dodatkowe 0,5 h utrzymania/mies. od miesiąca 7.

| Horyzont | A: dodatkowo | B: dodatkowo |
| ---: | ---: | ---: |
| 12 mies. | 7 050,00 | 5 850,00 |
| 36 mies. | 8 850,00 | 7 650,00 |

### Wrażliwość na stawkę pracy — 100 zam./mies., koszyk 78 zł

| Stawka planistyczna | A: 12 mies. | B: 12 mies. | A: 36 mies. | B: 36 mies. |
| ---: | ---: | ---: | ---: | ---: |
| 0 zł/h | 4 748,40 | 2 262,08 | 14 245,20 | 6 668,24 |
| 100 zł/h | 34 748,40 | 18 262,08 | 53 845,20 | 29 868,24 |
| 150 zł/h | 49 748,40 | 26 262,08 | 73 645,20 | 41 468,24 |
| 200 zł/h | 64 748,40 | 34 262,08 | 93 445,20 | 53 068,24 |

0 zł/h pokazuje własną pracę bez wyceny czasu, nie zerowy nakład pracy.

### Próg korzyści z automatyzacji w A

Hipoteza: dodatkowa oszczędność operacyjna względem B, wartość czasu 50 zł/h, odzyskanie różnicy referencyjnego TCO w 36 miesięcy; koszyk 78 zł. To wymagany próg, nie zmierzona przewaga A.

| Zam./mies. | Różnica TCO A−B, 36 mies. | Wymagana oszczędność minut/zamówienie |
| ---: | ---: | ---: |
| 20 | 29 449,60 | 49,08 |
| 100 | 32 176,96 | 10,73 |
| 300 | 38 995,36 | 4,33 |

<!-- END GENERATED TCO -->

## 7. Magazyn, zestawy, produkcja i niezawodność

| Wymaganie / sytuacja | A | B | Warunek odbioru |
| --- | --- | --- | --- |
| Ostatnia sztuka kupowana równolegle | Transakcja PostgreSQL, rezerwacje z terminem, atomowy warunek dostępności | Mechanizmy Woo, poprawne ustawienie stock i hold, przetestowana bramka | Jeden klient dostaje sztukę, drugi nie płaci za brakujący towar; brak ujemnego stanu |
| Powtórzony/spóźniony webhook | Unikalny identyfikator zdarzenia, idempotencja, uzgadnianie | Moduł P24 + historia zamówienia; test ponowień i statusów | Nie wysłać dwóch e-maili/paczek, nie odjąć stanu dwa razy; spóźniona wpłata po wygaśnięciu do obsługi |
| Klient nie wrócił z operatora | Realizacja z webhooka, nie success page | Analogicznie callback bramki | Zamówienie opłacone i widoczne w panelu bez przeglądarki klienta |
| Błąd mapy/nieaktywny Paczkomat | Własna walidacja i ścieżka poprawy | Moduł i procedura obsługi | Nie dopuścić pustego punktu; problem wysyłki nie usuwa zamówienia |
| Błąd ShipX po utworzeniu etykiety | Zapisać ID, sprawdzić wynik przed ponowieniem | Zweryfikować zachowanie modułu i panelu | Brak drugiej etykiety/opłaty przez ślepy retry |
| Zwrot częściowy | Stripe API/panel + synchronizacja zamówienia i księgowości | Woo + kompatybilność P24; ewentualnie panel operatora i uzgodnienie | Potwierdzić realny zwrot środków. Sama zmiana statusu Woo „refunded” nie zwraca pieniędzy [S21] |
| Awaria/restore | PostgreSQL, kopie, outbox, log operacji | MySQL + pliki + konfiguracja + kolejka | Odtworzenie na stagingu i uzgodnienie późniejszych płatności; rollback kodu ≠ cofnięcie bazy |

SKU jest identyfikatorem konkretnego sprzedawanego wariantu, partia wydruku osobną informacją. Nie nadawać ostatecznych kolorów, cen i SKU przed próbami. Stan gotowy, zarezerwowany i dostępny muszą być rozróżnione; filament i godziny drukarki nie są gotowym magazynem. W B natywne `hold stock` dotyczy określonych statusów oczekiwania, nie każdego `on-hold`; TTL i scheduler należy przetestować z rzeczywistą bramką. [Woo — magazyn][S22].

**Zestawy 2/4 w MVP:** ustalone wielokrotności tego samego wariantu jako ilość w koszyku, bez obiecanego rabatu. Alternatywnie fizycznie wydzielone gotowe zestawy z własnym stanem. Nie wolno tego samego zapasu niezależnie sprzedawać jako singli i zestawów. Dowolny miks modeli wymaga BOM i rozliczania komponentów. B może użyć Product Bundles, A potrzebuje tej logiki; jeżeli wybierzemy miks, zakres i koszty muszą być zwiększone w **obu** wariantach.

**Druk na zamówienie:** etap 1 sprzedaje gotowe sztuki, przy braku — lista zainteresowania bez pobrania płatności. Etap 2 przyjmuje płatne zamówienia tylko do skończonej pojemności partii produkcyjnej. Limit jest oddzielony od magazynu, rezerwowany atomowo, zwalniany po wygaśnięciu i utrwalany po płatności; terminy uwzględniają druk, obróbkę, kontrolę i bufor braków. Przerwanie drukarki zatrzymuje przyjmowanie nowych zleceń. W koszyku mieszanym jedna przesyłka po ukończeniu całości, z terminem pokazanym przed zapłatą. Nie udajemy, że natywne backorders rozwiązują planowanie.

Dodatek etap 2: **A 32–56 h, referencja 44; B 24–48 h, referencja 36**, plus 0,5 h/mies. utrzymania w obu. W tabeli przyrostu przyjęto start w miesiącu 7. Własna wtyczka B może stosować tabelę limitów i panel partii; A rozbudowuje istniejący model bazy. Nie potrzeba ERP ani mikrousług na start.

Cel operacyjny do przyjęcia: RPO zamówień ≤1 h oraz RTO ≤4 h w godzinach obsługi, z testem odtworzenia. To **cel projektu, nie SLA zakupionego hostingu**. A: PITR i niezależny export; B: kopie bazy częściej niż dobowe + pliki po zmianach. Sam backup dostawcy lub kopia na tym samym koncie nie wystarcza. Alarmy zaległych webhooków/queue i ręczna procedura uzgodnienia są częścią obu wariantów.

Bezpieczeństwo: MFA, minimalne role, sekrety wyłącznie serwerowe, podpisy callbacków, walidacja serwerowa ceny/ilości/dostawy, limity żądań, staging na danych syntetycznych, brak PII w logach i repo. A ma mniejszą powierzchnię wtyczek, ale więcej własnego krytycznego kodu; B więcej zależności, za to gotowe procesy sklepu. Nie przypisuję bezpieczeństwa samej nazwie frameworka. Cache omija koszyk, checkout, konto i webhooki.

## 8. Prawo, migracja i ekspansja PL → CZ/ES

Oba warianty wymagają dokończenia **polityki prywatności**: obecny `main` zawiera m.in. nieuzupełniony NIP. Dokumenty z roboczego PR #4 nie są zatwierdzonymi dokumentami sklepu. Potwierdzić spółkę jako sprzedawcę/administratora, nazwę, adres, NIP/KRS, kontakt oraz producenta; dane w katalogu, regulaminie, płatnościach i fakturach muszą się zgadzać. Nie używać danych osoby prowadzącej `dietologicznie`.

Przed checkoutem: RODO i role dostawców/umowy powierzenia, retencja danych, dostęp/usuwanie, wymagane podstawy transferów poza EOG. Region UE nie oznacza automatycznie pełnej zgodności. Zgoda marketingowa jest dobrowolna i oddzielona od obsługi zamówienia; wiadomości transakcyjne nie dopisują do Brevo newslettera. Zachować odmowę zgody GA, możliwość jej wycofania oraz pojedynczą instalację pomiaru; dopasować politykę do rzeczywistego sklepu i hostingu. [UODO][S23].

GPSR: pola identyfikacji produktu i producenta, kontakt, ostrzeżenia/instrukcje w wymaganym języku oraz powiązanie partii. Zestaw i druk po zamówieniu nie znoszą obowiązków produktu. Nie przyjmować automatycznie braku prawa odstąpienia tylko dlatego, że standardowy model drukuje się po zakupie. Warunki 14 dni, reklamacji, kosztu dostawy i terminu realizacji wymagają sprawdzenia prawnego. Dla funkcji odstąpienia online z dyrektywy 2023/2673 należy sprawdzić **aktualną implementację krajową przed startem**; plan przewiduje prosty proces z potwierdzeniem na trwałym nośniku, ale nie deklaruje, że dzisiejszy projekt lub gotowy Woo już spełnia wszystkie wymagania. [GPSR — Komisja][S24], [prawa przy sprzedaży na odległość][S25], [PARP — funkcja odstąpienia][S26].

Faktury: uzgodnić B2C/B2B, NIP nabywcy, korekty, zgodne stawki VAT i zakres KSeF spółki. Potwierdzenie Stripe albo e-mail Woo nie zastępuje automatycznie poprawnej faktury. Na start eksport do obecnej księgowości z trwałym ID zamówienia/płatności; integracja API i abonament wybranego systemu **do wyceny**, nie kolejny system kupowany bez rozpoznania. Obowiązki KSeF oceniać na poziomie całej spółki, nie wyłącznie obrotu tej witryny. [MF — zakres KSeF][S27].

**Migracja infrastruktury po odrębnej zgodzie:** komercyjny sklep nie powinien działać na GitHub Pages; zasady usługi wykluczają taki hosting e-commerce. A przechodzi na Vercel Pro, B na hosting WWW. Zachować OVH jako rejestratora i obsługę poczty; nie jest potrzebna zmiana nameserverów. Zmienić tylko zatwierdzone rekordy WWW po kopii strefy, nie ruszać MX/SPF/DKIM/DMARC bez osobnej potrzeby. Dodać rekordy nadawcy transakcyjnego bez tworzenia drugiego SPF. Ustalić apex/www, SSL i docelowe canonical. Zachować `.html`; jeżeli adres jednak zmieniany, mapa pojedynczych 301, bez łańcuchów, sitemap/hreflang i kontrola Search Console. Zachować formularze oraz istniejącą listę Brevo. Staging ma autoryzację i noindex; produkcja nie może odziedziczyć blokad. [GitHub Pages][S28].

| Obszar ekspansji | A | B |
| --- | --- | --- |
| PLN → CZK/EUR | Własny model cen/walut, Stripe obsługuje płatności zagraniczne; BLIK pozostaje dla klientów PL/PLN [S29] | Woo może sprzedawać za granicę; waluty/języki i moduły dobrać/testować. Warunki P24 dla walut obcych: do wyceny |
| Prowizje zagraniczne | Standardowe/premium karty EOG to inne stawki; Stripe publikuje też UK/poza EOG i +2% przy wymaganym FX [S19] | Nie przenosić krajowego 1,29% na każdą transakcję w EUR/CZK. Umowa i wypłaty walutowe osobno [S15] |
| Dostawy CZ/ES | Osobne usługi, punkty, zwroty i adaptery; Geowidget PL nie jest dowodem gotowości | Darmowy moduł PL nie gwarantuje całej zagranicy; sprawdzić ofertę przewoźnika/kraj i moduł |
| Prawo i treści | Tłumaczenia, waluta, ceny, GPSR, konsument, VAT/OSS | Te same obowiązki; ewentualna licencja wielojęzyczna i konfiguracja do wyceny |
| Lock-in | Next i PostgreSQL przenośne; Vercel-specific usługi i własny kod zwiększają koszt migracji | PHP/MySQL i hosting łatwo zmienić; zależność od wtyczek, schematów i nadpisań motywu |
| Automatyzacja produkcji | Bezpośredni dostęp do własnego modelu i API, wygodny przy niestandardowym procesie | REST API/hooki i wydzielona wtyczka mogą wystarczyć; nie wymagają od razu zmiany całego sklepu |

Dla sprzedaży unijnej ustalić zasady VAT/OSS z księgowością; unijny próg 10 000 EUR jest warunkowy i łączny dla właściwych sprzedaży transgranicznych, nie osobny dla każdego kraju. Nie doliczam fikcyjnego kosztu ekspansji do startu PL. Tłumaczenia, przewoźnik CZ/ES, zwroty zagraniczne, FX i integracje księgowe to osobny etap kosztowy. [VAT/OSS UE][S30].

## 9. Kiedy decyzja może się zmienić?

- **Praca własna:** przy 0 zł/h i bez wyceny czasu model nadal pokazuje niższe opłaty B. Nie oznacza to zerowej pracy w żadnym wariancie. Przedziały godzin częściowo się nakładają: sprawny opiekun Next i trudny motyw Woo mogą zmniejszyć różnicę; wiążąca oferta obu wykonawców ma pierwszeństwo przed szacunkiem.
- **Istniejący płatny Vercel:** nie potwierdzono planu `dietologicznie`. Jeśli odpowiedni Pro, miejsce i limity są już opłacone i współdzielenie jest dopuszczalne, przyrostowy koszt A może spaść o 80 zł/mies. = 960/2 880 zł. To alokacja wspólnej usługi, nie darmowa infrastruktura. Nie przenosić klientów ani kluczy między markami.
- **Baza i kurs:** +/−10% USD/PLN zmienia budżet A o +/−16 zł/mies. (192/576 zł), przy pozostałych założeniach bez zmian. Każde dodatkowe 10 USD/mies. zużycia to +480/+1 440 zł. Tańsza uśpiona baza może obniżyć rachunek; nie wolno oszczędzić poprzez pominięcie trwałości i odzyskiwania.
- **Koszt Woo:** potrzebne dodatkowe moduły/maintenance mogą zniwelować przewagę. Każde dodatkowe 1 h/mies. w B to +1 800/+5 400 zł. Same Core/P24/InPost nie wymagają płatnych licencji; dodatkowe abonamenty mają wynikać z konkretnej funkcji.
- **Wyższy wolumen:** w modelu bazowym dla 20/100/300 zam./mies. B wygrywa kosztowo przy tym miksie i tych kosztach hostingu; aneks pokazuje zmiany przy innych kosztach. Różnica prowizji rośnie z liczbą transakcji. A staje się ekonomicznie uzasadnione, jeśli daje dodatkową korzyść biznesową: przy 300 zam./mies. i koszyku 78 zł potrzeba ok. **4,33 min oszczędności na zamówieniu**, wycenionej na 50 zł/h, aby odzyskać referencyjną różnicę w 36 miesięcy. Nie stwierdzono dziś takiej przewagi; podobna automatyzacja w Woo może być tańsza.
- **Inny operator / zagranica:** można dołączyć Stripe do Woo lub P24 do Next. Zrównanie prowizji nie usuwa kosztu napisania panelu i magazynu w A, lecz musi być uwzględnione przy nowej umowie/ekspansji. Wybór platformy oraz operatora należy rozpatrywać oddzielnie.

Krótka alternatywa: Payment Links + ręczna obsługa mogą obniżyć pracę przy bardzo małym pilotażu. Nie spełniają jednak same pełnych wymagań Issue #6 dotyczących wspólnych stanów zestawów, automatycznej rezerwacji i limitu produkcji. To inny zakres, nie „tańszy gotowy odpowiednik” A/B. Headless Woo i dodatkowy ERP nie są potrzebne na start.

## 10. Plan wdrożenia rekomendowanego B — dopiero po zatwierdzeniu

1. **Decyzje i specyfikacja odbioru.** Przed zakupem potwierdzić hosting z natywnym cron 1–5 min albo uzyskać pozytywny przegląd alternatywnego schedulera OVH; warunki i wrażliwość kosztów w aneksie. Potwierdzić opiekuna, rzeczywiste warianty i sposób zestawów. Ustalić księgowość i dokumenty; zebrać dane spółki/producenta. Właściciel zatwierdza hosting i architekturę wyraźnie, PR #5 niezależnie. Wynik: zakres i budżet, bez uruchomienia sprzedaży.
2. **Chroniony staging.** Po zgodzie na zakup: nowy hosting, osobna baza i dane syntetyczne, aktualny zgodny WP/Woo, własny motyw, MFA i kopie. Test rzeczywistych wersji PHP/MySQL, pamięci, cron, eksportu i restore. Żadne produkcyjne klucze w preview; sama instalacja na testach nie upoważnia do publikacji.
3. **R04 i katalog.** Zachować zatwierdzone statyczne strony oraz AVIF/WebP, przygotować `/sklep/` i koszyk/checkout w tym samym języku wizualnym. Po próbach wpisać 4 modele, SKU, zdjęcia, ceny, masy/gabaryty, stany i bezpieczeństwo. Zestawy muszą korzystać z poprawnego magazynu. Porównanie desktop/mobile 320–1440 z podglądami PR #5.
4. **Integracje i operacje.** Sandbox P24 i InPost, konfiguracja Brevo i testy dostarczalności, eksport księgowy, zwrot częściowy, role pracowni, instrukcja przyjęcia partii, realizacji i reklamacji. Harmonogram i alarmy testowane również bez ruchu na stronie. Dokumentacja odpowiedzialności, SLA obsługi i procedury awarii.
5. **Odbiór E2E i migracji.** Ostatnia sztuka kupowana równolegle; ponowiony i spóźniony webhook; zamknięcie strony po zapłacie; odmowa/timeout; zwrot częściowy; niedostępny Paczkomat; przerwany ShipX; wyczerpany limit e-mail; brak cron; restore bez ponownej wysyłki paczek. Sprawdzić brak GA bez zgody, formularze Brevo, stare URL-e, canonical, SSL i pocztę OVH. Dokumenty prawne zatwierdzone przed włączeniem checkoutu.
6. **Osobna zgoda na uruchomienie.** Przedstawić wyniki, backup, mapę DNS i plan powrotu. Dopiero właściciel zatwierdza DNS, klucze produkcyjne i publikację. Po uruchomieniu monitorowanie kolejki i płatności; awaria pozwala zatrzymać nowe zakupy bez utraty opłaconych zamówień. Nie cofać bazy na ślepo podczas rollbacku motywu.
7. **Etap późniejszy: limitowany druk, potem CZ/ES.** Zmierzyć produkcję i popyt, wdrożyć skończone partie i zapowiedziane terminy z osobnym odbiorem; dopiero potem tłumaczenia, waluty, zagraniczna logistyka i rozliczenia. Nie uruchamiać nieograniczonego backorderu w międzyczasie.

Nakład MVP 92–156 h jest sumą z rozdziału 5, a nie dodatkowym kosztem tych kroków. Harmonogram kalendarzowy zależy od dostępności wykonawcy, wyników produkcji, KYC operatora i odbioru prawnego. Nie podaję niepotwierdzonej daty premiery.

### Pięć decyzji właściciela

1. **Budżet i opiekun:** praca własna czy wykonawca, stawka/przedział i osoba odpowiedzialna za aktualizacje oraz awarie?
2. **Hosting i niezawodność:** OVH Pro z opisanym uzupełnieniem cron czy hosting z natywnym częstym cron; akceptowane RPO/RTO i retencja kopii?
3. **Oferta/produkcja:** zatwierdzone warianty i stany po próbach, zestawy jednorodne czy mieszane, moment wejścia w płatny druk i limit partii?
4. **Księgowość i formalności:** obecny system faktur/KSeF, status VAT spółki, dane sprzedawcy/producenta, zatwierdzone regulaminy i obsługa zwrotów?
5. **Skala i zagranica:** spodziewany ruch/pik premierowy, miks płatności oraz kolejność i termin CZ/ES; potrzebny limit e-mail i oferta przewoźnika?

## 11. Źródła i kontrola kompletności

**Weryfikacja wykonana w tym PR:** `python scripts/store_tco.py --check` sprawdza 36 scenariuszy bazowych i 16 wyników aneksu, symetryczną aktywację P24, zaokrąglenia prowizji, sumowanie składników, jednorazowość wdrożenia/aktywacji i zgodność tabel w raporcie z JSON. Sprawdzono też odnośniki lokalne i definicje źródeł, sumy godzin oraz niezmienność plików strony względem bazy. Audyt `dietologicznie` był tylko odczytem. Testy sklepowe opisane w planie są **kryteriami przyszłego odbioru**, nie wykonanymi testami działającego sklepu. GitHub Pages wskazuje `main`; PR nie dodaje automatyzacji publikacji.

Linki poniżej prowadzą do źródeł pierwotnych, sprawdzonych 02.11.2026. Publiczny cennik nie zastępuje zamówienia ani umowy. Nie zamrażamy cen na 36 miesięcy; model zakłada ich niezmienność dla porównania.

- S1–S3: [Vercel cennik][S1], [Vercel Hobby][S2], [Neon cennik][S3].
- S4–S7: [Brevo limity][S4], [OVH cennik][S5a], [OVH techniczne][S5], [Woo wymagania][S6], [OVH cron][S7].
- S8–S11: [Stripe fulfillment][S8], [Stripe wygląd Checkout][S9], [Woo kolejki][S10], [cron-job.org][S11].
- S12–S18: [P24 Woo][S12], [InPost PL][S13], [Woo core][S14], [P24 opłaty][S15], [Product Bundles][S16], [InPost cenniki][S17], [Resend][S18].
- S19–S22: [Stripe Polska][S19], [Stripe zwroty][S20], [Woo zwroty][S21], [Woo magazyn][S22].
- S31–S32: [P24 REST][S31], [Neon scale to zero][S32].
- S23–S30: [UODO][S23], [GPSR][S24], [Your Europe — e-commerce][S25], [PARP — odstąpienie online][S26], [MF KSeF][S27], [GitHub Pages][S28], [Stripe BLIK][S29], [VAT UE][S30].

| Wymaganie Issue #6 | Miejsce odpowiedzi |
| --- | --- |
| Dwa konkretne wdrożenia, baza i e-mail, OVH, krótka alternatywa | 3, 4, 9 |
| Aktualne stawki, VAT, promocja/odnowienie, integracje | 4 |
| 20/100/300 zamówień; 39/78/156 zł; 12/36 miesięcy, wzory | 6 oraz kalkulator i JSON |
| Wdrożenie i utrzymanie, rzeczywisty reuse | 2, 5, 7 |
| Prawo, RODO/GPSR, spółka, DNS/poczta/SEO | 8, 10 |
| Front poza WordPressem, `/sklep/`, subdomena | 3 |
| Lock-in, CZ/ES, księgowość i produkcja | 7–9 |
| Jednoznaczna decyzja i warunki jej zmiany, maks. 5 wyborów | 1, 9, 10 |
| Osobny draft, PR #5 bez zmian, bez publikacji | Zakres PR i kontrola Git; żadne pliki strony nie są zmieniane |

## 12. Aneks po recenzji — symetryczne P24, wydatki i hosting

Uzupełnienie do [recenzji właściciela z 02.11.2026](https://github.com/pracowniarachunkowosci-debug/form/pull/7#pullrequestreview-5738329718). Bazowe 36 scenariuszy pozostaje bez zmian; poniżej 16 dodatkowych wyników przy **100 opłaconych zamówieniach/mies., pełnym koszyku 78 zł**, tym samym miksie i kursie. Założenia są w `review_annex` w JSON; kalkulator sprawdza obie części raportu.

### 12.1. Ta sama bramka w A i B

**A + bezpośrednie P24** używa tej samej tabeli prowizji co B, bez pośrednictwa Stripe. Roczne prowizje wynoszą 1 572 zł. Przy niezmienionej infrastrukturze A: `12 × 170 + 1 572 = 3 612 zł`, zgodnie z recenzją. To kwota **przed aktywacją**. Dla symetrii model dolicza 59 zł w obu wariantach P24: **A 3 671 zł vs B 2 262,08 zł**. Jeśli warunek zwrotu aktywacji zostanie spełniony, odjąć 59 zł od obu: 3 612 zł vs 2 203,08 zł. Koszt operatora nie jest różnicą technologii. [P24][S15].

Do A zakładamy **dodatkowe 16–32 h netto, referencja 24 h**, ponad pierwotne wdrożenie: zastąpienie adaptera Stripe bezpośrednią integracją P24, rejestracja i serwerowa weryfikacja transakcji, ponowienia/podpisy powiadomień, mapowanie stanów, zwroty częściowe oraz testy sandbox/E2E. To przyrost po zastąpieniu prac nad Stripe, nie drugi pełny koszyk. Ogólna suma A+P24: **204–348 h, referencja 276 h**; przy 150 zł/h przyrost 2 400–4 800 zł, referencja 3 600 zł. To szacunek do potwierdzenia po prototypie, nie cena od P24. Ponowne użycie koszyka/Geowidget pozostaje możliwe, adapter Stripe nie realizuje P24 REST. Utrzymanie referencyjnie nadal 4 h/mies. (widełki 2–6); dodatkowe potrzeby aktualizują ten budżet. [Dokumentacja P24][S31].

### 12.2. Neon 5 USD i brak potwierdzonego Pro

**20 USD nie jest minimum Neon.** Wariant 5 USD to warunkowy budżet małego zużycia Launch, z tą samą docelową retencją do 7 dni i osobną rezerwą 10 zł na kopie. Przykład: 40 CU-h × 0,106 + 1 GB × 0,35 + 1 GB historii × 0,20 = **4,79 USD/mies.**, bez dodatkowych zasobów. To około 160 h aktywności przy 0,25 CU, nie baza działająca stale. Obniża A o **60 zł/mies., 720/2 160 zł w 12/36 mies.** [Neon][S3].

Warunek: pomiar realnego ruchu, zadań i wybudzeń, ustawienie okna odzyskiwania i udany restore. Częste odpytywanie bazy przez scheduler może wykluczyć założenie 5 USD; nie wydłużać rezerwacji ani wyłączać kontroli płatności, by dopasować rachunek. Testować cold start i ponowienia webhooków. Alert kosztów nie zatrzymuje naliczania; limit powodujący zawieszenie bazy nie może bez planu przerwać obsługi opłaconych zamówień. [Scale to zero][S32], [Neon][S3].

Recenzja podaje zespół `pracownia-growthos` na **Hobby**; nie potwierdza Pro dla DietoLogicznie. Odczyt zespołów przez dostępny konektor w tej sesji nie powiódł się, więc nie przedstawiam tego jako własnej weryfikacji konta. **Żaden wynik aneksu nie odejmuje opłaty Pro.** Wcześniejsza oszczędność 80 zł/mies. pozostaje wyłącznie hipotezą wymagającą potwierdzenia konta, płatnego miejsca, limitów i zasad współdzielenia. Hobby nie zastępuje komercyjnego Pro.

<!-- BEGIN REVIEW ANNEX TCO -->

| Wariant; 100 zam./mies. × 78 zł | Technologia 12 mies. | Technologia 36 mies. | Z wyceną pracy 12 mies. | Z wyceną pracy 36 mies. |
| --- | ---: | ---: | ---: | ---: |
| A: Stripe, Neon 20 USD | 4 748,40 | 14 245,20 | 49 748,40 | 73 645,20 |
| B: P24, OVH baza | 2 262,08 | 6 668,24 | 26 262,08 | 41 468,24 |
| A: bezpośrednie P24, Neon 20 USD | 3 671,00 | 10 895,00 | 52 271,00 | 73 895,00 |
| A: Stripe, Neon 5 USD | 4 028,40 | 12 085,20 | 49 028,40 | 71 485,20 |
| A: bezpośrednie P24, Neon 5 USD | 2 951,00 | 8 735,00 | 51 551,00 | 71 735,00 |
| B: hosting 75,00 zł/mies. (budżet) | 2 651,00 | 7 835,00 | 26 651,00 | 42 635,00 |
| B: hosting 100,00 zł/mies. (budżet) | 2 951,00 | 8 735,00 | 26 951,00 | 43 535,00 |
| B: hosting 150,00 zł/mies. (budżet) | 3 551,00 | 10 535,00 | 27 551,00 | 45 335,00 |

<!-- END REVIEW ANNEX TCO -->

Technologia obejmuje aktywację i rezerwę kopii; kolumny z pracą używają 150 zł/h, a A+P24 dodatkowych 24 h. Budżety hostingu B 75/100/150 zł netto/mies. **nie są ofertami dostawców ani potwierdzeniem parametrów**. Pozostałe założenia, nieznane koszty `U`, VAT i wyłączenia jak w rozdziałach 4–6.

### 12.3. Zewnętrzne faktury, własny czas, ryzyka

| Kategoria | Właściciel pracuje z Codexem | Zlecenie wykonawcy |
| --- | --- | --- |
| Wydatki zewnętrzne | Opłaty za usługi i prowizje z kolumn „Technologia” + faktyczny koszt narzędzi AI, zakupionych modułów i usług `U`. Rezerwy Neon/kopii zastąpić rachunkami | To samo + uzgodnione faktury za wykonanie i utrzymanie; stawka 150 zł/h jest tylko modelem |
| Własny czas | Referencja nakładu projektu, nie pomiar czasu właściciela z AI. Bazowo A: 252 h wdrożenia + 4 h/mies.; B: 124 h + 3 h/mies. Razem 300/160 h w 12 mies., 396/232 h w 36 mies. Przy P24 w A dodatkowo referencyjne 24 h | Nadal potrzebne decyzje, dane produktów, odbiór i obsługa zamówień; nie znikają po zleceniu |
| Ryzyka i praca do potwierdzenia | AI może skrócić pisanie kodu, ale **nie stanowi darmowego, niezależnego odbioru bezpieczeństwa**. Budżet przeglądu płatności/rezerwacji, testów awarii i restore ustalić z odpowiedzialnym opiekunem | Zakres odpowiedzialności, testy i reakcję na awarie uzgodnić w ofercie; bez domniemanej gwarancji SLA |

Nie znamy rzeczywistej produktywności właściciela z Codexem, jego planu/limitów ani kosztu dodatkowego użycia AI. Nie mnożymy „godzin asystenta” przez 150 zł i nie obiecujemy określonej redukcji godzin. **49 748/26 262 zł to wycena zasobów projektu w czasie, nie wymagany przelew na start.** Faktyczny cash-out = opłaty usług/prowizje + rzeczywiście zlecone prace + narzędzia/dodatki; własny czas wykazywać osobno. Nie liczyć godzin odbioru dwa razy, jeżeli są już w ofercie lub bazowym nakładzie.

### 12.4. Hosting: warunek decyzji i wpływ na rekomendację

Preferencja przed zakupem: hosting PHP/MySQL z **natywnym cron 1–5 min**, znanymi limitami i procedurą restore. Jeżeli rozważamy OVH Pro z innym schedulerem, najpierw przegląd całej ścieżki Woo/Action Scheduler: uwierzytelnienie i poprawna walidacja TLS tam, gdzie przekazywane są uprawnienia; brak PII/sekretów w odpowiedzi i URL; blokady, idempotencja, ograniczenie wywołań oraz alarm zaległości. Sam trigger nie może autoryzować płatności lub zwrotów — rozstrzygają zweryfikowane zdarzenia i stan serwerowy. Nie opierać wrażliwych operacji na `cron-job.org` bez potwierdzenia tej architektury.

Przed zakupem przegląd dokumentacji/projektu; przed sprzedażą test na stagingu: **24 h bez wejść klientów**, terminowe zwalnianie rezerwacji i realizacja kolejki, 30 min niedostępności schedulera oraz odzyskanie pracy bez duplikatów, spóźniona płatność, timeout i równoległe uruchomienia. Wyniki i docelowe opóźnienia zatwierdza opiekun i właściciel. Nie wykonano tych testów w tym analitycznym PR.

Wpływ ceny hostingu: `ΔTCO_B = (nowa cena netto/mies. − 42,59) × 12 lub 36`, przy niezmienionej pracy. Każde dodatkowe 25 zł/mies. to +300/+900 zł. Zmiana zakresu obsługi hostingu może zmienić również godziny utrzymania — wymagane osobne potwierdzenie.

**Woo nadal rekomenduję jako praktyczne MVP ze względu na gotowy panel i procesy**, a nie bezwarunkowo najniższą opłatę za infrastrukturę. Przy hostingu B za **100 zł netto/mies.** technologia B kosztuje tyle samo co **A+P24 z Neon 5 USD**, ponieważ oba mają 110 zł/mies. stałych kosztów i te same prowizje/aktywację. Powyżej tego progu A w tym wariancie jest tańsze w samych opłatach; z referencyjną wyceną pracy B pozostaje tańsze w pokazanych scenariuszach. Progi obowiązują tylko przy osiągalnym niskim zużyciu Neon i podanym zakresie.

Zachowujemy cztery modele z SKU rzeczywistych wariantów, mały magazyn i późniejszy limitowany druk. Audyt DietoLogicznie nadal nie wykazał kompletnego sklepu fizycznego. **Wybór hostingu, architektury i budżetu wymaga wyraźnego zatwierdzenia właściciela; rekomendacja nie jest zgodą na zakup ani gwarancją SLA.** PR #5, kod sklepu i DNS pozostają bez zmian.

[S1]: https://vercel.com/pricing
[S2]: https://vercel.com/docs/plans/hobby
[S3]: https://neon.com/pricing
[S4]: https://help.brevo.com/hc/en-us/articles/208580669-FAQs-What-are-the-limits-of-the-Free-plan
[S5a]: https://www.ovhcloud.com/pl/web-hosting/
[S5]: https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/hosting-technical-specificities
[S6]: https://woocommerce.com/document/server-requirements/
[S7]: https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/cron-tasks
[S8]: https://docs.stripe.com/checkout/fulfillment.md?ui=full-page
[S9]: https://docs.stripe.com/payments/checkout/customization
[S10]: https://woocommerce.com/document/understanding-the-woocommerce-system-status-report/scheduled-actions/
[S11]: https://cron-job.org/en/faq/
[S12]: https://www.przelewy24.pl/do-pobrania/woocommerce
[S13]: https://inpost.pl/aktualnosci-integracja-inpost-z-woocommerce-jak-skonfigurowac-dostawe-geowidget-i-koszty-wysylki-w
[S14]: https://woocommerce.com/pricing/
[S15]: https://www.przelewy24.pl/oferta/tabela-prowizji-i-oplat
[S16]: https://woocommerce.com/products/product-bundles/
[S17]: https://inpost.pl/cenniki
[S18]: https://resend.com/pricing
[S19]: https://stripe.com/en-pl/pricing
[S20]: https://docs.stripe.com/refunds
[S21]: https://woocommerce.com/document/woocommerce-refunds/
[S22]: https://woocommerce.com/document/configuring-woocommerce-settings/products/
[S23]: https://www.uodo.gov.pl/pl/676/4258
[S24]: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A52025XC06233
[S25]: https://europa.eu/youreurope/business/selling-in-eu/selling-goods-services/ecommerce-distance-selling/index_en.htm
[S26]: https://www.parp.gov.pl/component/content/article/91021:one-click-return-czyli-zwroty-w-e-commerce-po-nowemu
[S27]: https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/zakres-obowiazkowego-ksef/
[S28]: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
[S29]: https://docs.stripe.com/payments/blik
[S30]: https://europa.eu/youreurope/business/finance-and-tax/vat/cross-border-vat/
[S31]: https://developers.przelewy24.pl/
[S32]: https://neon.com/docs/introduction/scale-to-zero
