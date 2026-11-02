# Hosting WooCommerce — shortlist do decyzji, 02.11.2026

Uzupełnienie [odebranej analizy PR #7](https://github.com/pracowniarachunkowosci-debug/form/pull/7#pullrequestreview-5738562410). **Nie wybrano ani nie kupiono hostingu.** Dwie oferty poniżej mają udokumentowany natywny cron. Dokumentacja nie jest testem Action Scheduler na zakupionym koncie: potwierdzenia zaznaczone jako brakujące są warunkami decyzji, nie domniemanymi funkcjami.

## Porównanie ofert

Ceny z publicznych stron; brutto z VAT 23%. Rozliczenie roczne, bez kodów partnerskich. Poczta i domena pozostają w OVH. Nie zamawiamy migracji poczty.

| Kryterium | LH.pl Apple | MyDevil MD2 |
| --- | --- | --- |
| Pierwszy rok netto / brutto | 100 / 123 zł — promocja | 325,20 / 400 zł — cena regularna |
| Roczne odnowienie netto / brutto | 599 / 736,77 zł | 325,20 / 400 zł przy obecnej taryfie; brak osobnej promocji pierwszego roku |
| Ekwiwalent odnowienia miesięcznie netto / brutto | 49,92 / 61,40 zł; faktura roczna | 27,10 / 33,33 zł; faktura roczna. Rozliczenie miesięczne kosztuje więcej: 32,52 / 40 zł |
| Zasoby | 100 GB SSD/NVMe, RAM 4 GB, normatywne CPU 200%, 40 połączeń MySQL, SSH/Redis | 50 GB SSD/NVMe, RAM 2 GB, 70 procesów, domyślnie 10 interpreterów PHP; brak liczbowej gwarancji CPU w sprawdzonym cenniku |
| PHP / baza | PHP 8.2–8.5, MySQL; **bieżąca wersja MySQL do potwierdzenia** | PHP m.in. 8.3/8.4, MySQL 8.0 w specyfikacji |
| Natywny cron | Panel: gotowy interwał **5 min**, zaawansowane wyrażenia cron; wykonanie pliku PHP lub cURL | Systemowy crontab, dokumentacja pokazuje **co 2 min**, SSH/CLI; można wykonywać lokalny PHP |
| Backup / odtworzenie | Codziennie; oferta mówi 30 dni. Instrukcja restore opisuje pobranie plików i SQL z serwera kopii; w jej części proceduralnej pozostało „14 kopii” — **potwierdzić rzeczywistą retencję** | Codziennie; kopie zdalne 14 dni; pliki dostępne użytkownikowi. Kopię bazy udostępnia pomoc po zgłoszeniu daty/nazwy bazy; brak potwierdzonego czasu obsługi |
| SSL | Let's Encrypt bez dopłaty; automatyczne odnowienie potwierdzić przy odbiorze | Let's Encrypt w panelu; zweryfikować odnowienie przy odbiorze |
| Action Scheduler | Udokumentowany cron PHP spełnia warunek uruchamiania bez wizyt. **Nie znaleziono deklaracji obsługi/monitorowania Action Scheduler dla Apple** | Udokumentowane cron i WP-CLI pozwalają uruchomić kolejkę lokalnie. **Nie znaleziono deklaracji zarządzania Action Scheduler przez operatora** |

Źródła LH: [oferta Woo](https://www.lh.pl/hosting-woocommerce), [pełne parametry i ceny](https://www.lh.pl/hosting-wordpress), [cron w panelu](https://www.lh.pl/pomoc/doc/jak-dodawac-lub-edytowac-zadania-cron/), [odtwarzanie](https://www.lh.pl/pomoc/doc/jak-przywrocic-strone-z-backupu-w-lh-pl/). Nie przenosimy parametrów Cloud Server na zwykły hosting.

Źródła MyDevil: [oferta i parametry](https://www.mydevil.net/nasza-oferta/), [cron](https://pomoc.mydevil.net/Cron/), [WP-CLI](https://pomoc.mydevil.net/WP-CLI/), [kopie](https://pomoc.mydevil.net/Backup/), [FAQ z wersją MySQL](https://www.mydevil.net/?mode=help). Przykład HTTP w dokumentacji cron wyłącza walidację TLS: **nie kopiować go**. Preferować lokalne wykonanie PHP/CLI, bez HTTP i bez przekazywania sekretów zewnętrznemu schedulerowi.

## Co oznacza udokumentowane wsparcie Action Scheduler

Woo dokumentuje [zależność zadań od WP-Cron](https://woocommerce.com/document/understanding-the-woocommerce-system-status-report/scheduled-actions/), a projekt Action Scheduler [mechanizm kolejki](https://github.com/woocommerce/action-scheduler/blob/trunk/docs/index.md). Zgodny PHP/MySQL i cron to przesłanki kompatybilności, **nie certyfikat ani SLA kolejki**. W obu ofertach brakuje pisemnego potwierdzenia konkretnej konfiguracji i zakresu pomocy. Żadna nie jest jeszcze bezwarunkowo zatwierdzona do zakupu.

Przed zakupem potrzebna odpowiedź operatora na jeden zestaw pytań (przygotowany, **nie wysłany**):

> Prosimy potwierdzić dla Apple / MD2: aktualne PHP i MySQL, pamięć PHP CLI, możliwość stałego zadania co 1–5 min uruchamiającego lokalny `wp-cron.php` albo WP-CLI, limity czasu/procesów oraz blokady równoległych wykonań. Czy obsługujecie WooCommerce Action Scheduler/HPOS i pomagacie diagnozować zaległą kolejkę oraz loopback? Jaka jest retencja kopii całej bazy (w tym HPOS/Action Scheduler), sposób i czas dostępu do restore? Czy można wykonywać własny godzinowy eksport do niezależnej lokalizacji? Prosimy o cenę odnowienia netto/brutto wraz z koniecznymi dodatkami, warunki SSL i zakres odpowiedzialności za kolejkę.

Przed sprzedażą: test 24 h bez wejść klientów, wykonanie akcji kontrolnej ≤5 min, restart/awaria schedulera, brak podwójnej realizacji, wygasanie rezerwacji i restore całej bazy. Nie wystarczy zielony status WP-Cron w panelu. Kopie dobowe nie realizują same celu RPO ≤1 h z raportu: potrzebny dodatkowy eksport i uzgodnienie zdarzeń płatniczych. Nie deklarujemy, że wykonano testy na tych hostingach.

## Wpływ na TCO i rekomendacja

Punkt porównawczy: 100 zam./mies. × 78 zł, P24 1,31 zł/transakcję, aktywacja 59 zł, rezerwa kopii 10 zł/mies.; reszta jak PR #7. Liczymy dokładne opłaty roczne, nie zaokrąglony ekwiwalent miesięczny.

| Hosting | Technologia/prowizje 12 mies. po cenie odnowienia | 36 mies. po cenie odnowienia | 12 / 36 mies. z dostępną promocją pierwszego roku |
| --- | ---: | ---: | ---: |
| OVH Pro — tylko benchmark | 2 262,08 zł | 6 668,24 zł | 1 852,88 / 6 259,04 zł |
| LH.pl Apple | 2 350,00 zł | 6 932,00 zł | 1 851,00 / 6 433,00 zł |
| MyDevil MD2 | 2 076,20 zł | 6 110,60 zł | identycznie — bez promocji |

Wzór: `lata × hosting_roczny + miesiące × (10 + 100 × 1,31) + 59`. Do porównania z pełnym referencyjnym TCO B dodać 24 000 zł za wycenę pracy w 12 mies. lub 34 800 zł w 36 mies.; to **nie zobowiązanie do faktur**. Różnice w obsłudze mogą zmienić godziny utrzymania; cena hostingu nie wycenia opieki nad aplikacją.

**Do pierwszego sprawdzenia rekomenduję LH.pl Apple**, ze względu na opisany cron co 5 min, większy limit zasobów i udokumentowaną ścieżkę pobrania bazy oraz plików. Warunki: potwierdzenie wersji MySQL, retencji i działania kolejki. **MyDevil MD2 jest tańszą alternatywą dla technicznego opiekuna**; wersja MySQL jest jawna, ale proces odzyskania bazy i utrzymanie CLI trzeba zaakceptować. Różnica ceny nie uzasadnia kupowania obu usług.

Sprawdzono też [HostingBiznesowy Woo](https://hostingbiznesowy.pl/hosting-woocommerce), który wprost opisuje konfigurację Action Scheduler przez cron co minutę. Nie dodaję go jako trzeciej zakwalifikowanej oferty: strona Woo podaje Biznes 2 388 zł netto/rok, a [cennik](https://hostingbiznesowy.pl/cennik) 414 zł netto/rok, bez kompletu liczbowych limitów CPU/RAM. Rozbieżność wymaga wyjaśnienia, nie wyboru wygodniejszej ceny. OVH Pro pozostaje benchmarkiem z cron maksymalnie godzinowym.

Nie wysyłano zapytań do operatorów, nie zakładano kont/testów i nie kupowano usług. Przegląd źródeł nie zastępuje odpowiedzi hostingu ani testu aplikacji.
