# LH staging: opcje MySQL i GitHub Actions do akceptacji

Stan analizy: 14.11.2026, kontynuacja PR #28. Odczyt lokalnej gałęzi `codex/issue-27-winter26-photo-store`, HEAD `70c1fd0d729d62bddc6de38171b63c973f548ce9`. Dokument jest propozycją zakresu, nie zgodą na wykonanie. Analiza MySQL/Actions opiera się na kodzie; nie wykonano adaptera, jego testów, migracji ani inicjalizacji DB. Rzeczywiste pomiary infrastruktury są opisane oddzielnie w [raporcie DNS-01/PHP-FPM](LH_DNS01_PRIVATE_20261114.md).

## 1. Decyzja w skrócie

**MySQL wymaga adaptera transakcyjnego i testów współbieżności, nie tylko zmiany DSN. GitHub Actions może sprawdzać i pakować repozytorium, ale samo nie zapewnia dostępu do środowiska PHP-FPM na LH.**

Aktualny stan potwierdzony w oddzielnej diagnostyce: staging `test.pracowniaform.com`, brak działającego SSL, `Permission denied` dla PHP-FPM poza `public_html`; FTPS działa przez WinSCP. [Raport stagingu](LH_STAGING_20261114.md) rozdziela wyniki bieżące i historyczne. Przyczyna odmowy dostępu PHP-FPM (prawa właściciela/katalogów, ACL, izolacja lub konfiguracja PHP) pozostaje nieustalona.

| Opcja do akceptacji | Konkretny rezultat następnego zadania | Warunek i ograniczenie |
| --- | --- | --- |
| A. Zachować SQLite i wyjaśnić runtime LH | Potwierdzona przez LH prywatna ścieżka konfiguracji i SQLite, dostęp PHP-FPM oraz SSL stagingu | Najmniejsza zmiana aplikacji. Potrzebny zapis katalogu SQLite, nie tylko samego pliku. FTPS operatora nie potwierdza praw PHP-FPM. |
| B. Przygotować adapter MySQL lokalnie | Adapter dwóch sterowników, osobny schemat MySQL i testy opisane niżej, bez bazy i wdrożenia na LH | Rozwiązuje zależność magazynu od pliku SQLite. Nadal potrzebny bezpieczny dostęp PHP-FPM do sekretów i poprawny HTTPS. Najpierw ustalić silnik i wersję oferowane przez LH. |
| C. Actions tylko CI/build + ręczny transfer WinSCP | Powtarzalny wynik testów i paczka ZIP z manifestem dla zatwierdzonego SHA | Rekomendowany pierwszy zakres automatyzacji. Bez sekretów LH, OVH, Stripe i bez automatycznego uploadu. |
| D. Actions także upload stagingu | Osobny, ręcznie zatwierdzany job wysyłający zweryfikowaną paczkę do nowego katalogu stagingu | Dopiero po C, sprawdzeniu klienta FTPS na runnerze, ochrony katalogu i praw konta. Nie obejmuje DNS, SSL, DB ani przełączenia vhosta. |

Rekomendacja: **C jako osobna automatyzacja repozytorium; A jako pierwszy sposób usunięcia blokady LH. B wybrać, jeżeli operator preferuje MySQL lub LH nie zapewni obsługi prywatnego pliku SQLite. D odłożyć do odbioru infrastruktury.** Opcje A/B i C/D są niezależnymi decyzjami. Żadna nie oznacza uruchomienia sprzedaży Live.

## 2. Co rzeczywiście robi obecny backend

| Miejsce w kodzie | Zachowanie istotne dla adaptera |
| --- | --- |
| `api/_common.php:25–44`, `api/_live.php:36–50` | Konfiguracja JSON z `PF_TEST_CONFIG` / `PF_LIVE_CONFIG` albo katalogu `.pf-private` obok document root. Wymagane realpath i prywatność względem bieżącego root, HTTPS, właściwy host i klucze trybu. Walidacja DB jest obecnie wyłącznie plikowa i wymaga `pdo_sqlite`. |
| `api/_common.php:98–110` | `database()` otwiera `sqlite:db_file`, ustawia `busy_timeout=5000` i tworzy pięć tabel przy połączeniu. `tx()` wykonuje `BEGIN IMMEDIATE`, następnie COMMIT/ROLLBACK: SQLite serializuje transakcje zapisujące. |
| `api/_common.php:114–139` | `order()` szuka `req` przed transakcją i ponownie w niej. Rezerwuje przez warunkowe `UPDATE stock SET n=n-? WHERE sku=? AND n>=?`, wymaga `rowCount()===1`, potem zapisuje zamówienie. Brak dowolnego SKU wycofuje całość. |
| `api/_common.php:114–121` | Powtórka musi mieć tego samego właściciela, zaakceptowane wydanie, listy elementów kompozycji, metodę i punkt dostawy. Tylko `reserved` może wrócić jako istniejąca próba; inaczej 409. Powtórka korzysta z zapisanej wyceny. |
| `api/checkout.php:8–13`, `api/_common.php:165–184` | Rezerwacja kończy transakcję przed wywołaniem Stripe. `Idempotency-Key` to ID zamówienia; `bind_session()` przypina SID i URL warunkowym UPDATE. Błąd Stripe zachowuje rezerwację, umożliwiając ponowienie tej samej próby. |
| `api/_common.php:123–130` | Weryfikacja Paczkomatu odbywa się przed blokadą zapisu. Znana próba może wrócić bez ponownego kontaktu z katalogiem punktów. Nie przenosić HTTP pod blokadę DB. |
| `api/_common.php:192–215`, `api/webhook.php:4–7` | Podpis webhooka jest sprawdzany przed DB. `events.id` deduplikuje zdarzenia. Stan zamówienia, ewentualny zwrot zapasu i zapis eventu są w jednej transakcji. |
| `api/_live.php:51–78` | `store_meta.mode` rozdziela test/live. `attempts` utrzymuje limity w 10-minutowych koszykach; SQLite UPSERT `ON CONFLICT` i usuwanie starych koszyków wykonują się transakcyjnie. |
| `api/seed-test.php:5–14`, `api/prepare-live.php:5–17` | Narzędzia CLI są plikowe. Seed testowy odmawia ponownego zasiania istniejących stanów/zamówień. Inicjalizacja Live wymaga nowego pliku i dokładnie 12 dostarczonych stanów. |

Rezerwacja jest reprezentowana przez pomniejszony `stock.n` i `orders.quote/state`; nie ma osobnej tabeli reservations. `orders.quote` przechowuje JSON, w tym wycenę, SKU, kompozycje, zgodę na wydanie i kanoniczny adres punktu. Ceny są obliczane przez `quote()` z istniejącej polityki, nie w SQL. Adapter nie zmienia cen, SKU, dostępności ani warunków zgód.

Obecne przejścia: `reserved` → `pending` dla completed bez zapłaty; potwierdzona zapłata → `paid`; expired/async failed z `reserved` lub `pending` → `released` i jeden zwrot zapasu. Zapłata po zwolnieniu → `review`; expired po paid nie zwraca zapasu. Nie ma automatycznego lokalnego zwalniania po godzinie: termin sesji to `created+3600`, a zbyt późne wznowienie zwraca `RECONCILE`. Migracja sterownika nie powinna dodawać takiego zwalniania.

## 3. Proponowany zakres adaptera MySQL

### Połączenie, konfiguracja i inicjalizacja

1. Wydzielić niewielką warstwę połączenia/transakcji i zależnych od silnika zapytań. Zachować funkcje biznesowe, odpowiedzi HTTP, dane wyceny i dotychczasową ścieżkę SQLite. Proponowany jawny wybór `sqlite` / `mysql`; brak automatycznego fallbacku do pustej DB przy awarii MySQL.
2. Dla MySQL: `pdo_mysql`, PDO z wyjątkami i FETCH_ASSOC, jawne `utf8mb4`, natywne prepared statements, bez trwałych połączeń na początek. Parametry host/port lub socket, nazwa DB i osobne dane użytkownika w prywatnej konfiguracji; bez wstawiania wartości od klienta do DSN. Sposób połączenia i ewentualne TLS DB muszą odpowiadać rzeczywistej ofercie LH. [PDO_MYSQL](https://www.php.net/manual/en/ref.pdo-mysql.php)
3. Zmienić wyłącznie gałąź walidacji DB w `configuration()` i `live_config()`: MySQL nie wymaga `realpath(db_file)` ani zapisywalnego katalogu DB, ale nadal wymaga prywatnej, czytelnej konfiguracji, właściwego trybu i HTTPS. Nie usuwać kontroli SQLite dla starego sterownika.
4. DDL MySQL przenieść do oddzielnego, wersjonowanego kroku operatora. Połączenie runtime tylko sprawdza zgodność schematu i trybu; nie wykonuje CREATE/ALTER. DDL MySQL może powodować implicit commit, więc nie można traktować go jak części transakcji rezerwacji. [MySQL: implicit commit](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html)
5. Osobne przyszłe narzędzie inicjalizacji testowego ledgeru MySQL, z odmową ponownego seedowania i kontrolą przeznaczenia bazy. Nie przerabiać obecnego `init-inventory` na bezwarunkowy import. W tym zadaniu nie powstaje ani DDL wykonawczy, ani DB, ani dane startowe.

Zmiany implementacyjne w opcji B obejmowałyby: `api/_common.php`, DB-zależne fragmenty `api/_live.php`, nowy adapter i schemat, testowe fabryki połączeń oraz osobne narzędzie inicjalizacji. Dostosowanie `seed-test.php`, `prepare-live.php` i narzędzi integracyjnych trzeba zaplanować jawnie; nie zakładać, że po zmianie `database()` przestaną wymagać plików SQLite. Sprawdzić też listę plików wydania: `build_release.py` zbiera tylko `api/*.php`, więc adapter w podkatalogu wymagałby jawnego rozszerzenia listy. Schemat i narzędzia operatora mają pozostać poza publicznym WWW. Nie trzeba zmieniać UI, wyceny ani payloadu Stripe.

### Schemat: pięć istniejących tabel, InnoDB

Poniższe typy to propozycja do implementacji po potwierdzeniu wersji serwera. Nazwy i znaczenie pól pozostają zgodne z aktualnym kodem. Nie zakładać, że nazwa usługi „MySQL” potwierdza Oracle MySQL, konkretną wersję ani zgodność MariaDB.

| Tabela | Proponowane odwzorowanie i ograniczenia |
| --- | --- |
| `stock` | `sku VARBINARY(128) PRIMARY KEY`, `n BIGINT NOT NULL CHECK(n>=0)`. Zachować atomowy warunek `n>=?`; nie polegać wyłącznie na CHECK. Skuteczność CHECK i przepełnienia sprawdzić na docelowej wersji i w strict SQL mode. |
| `orders` | `id VARBINARY(32) PRIMARY KEY` (generator obecnie daje 28 znaków), `req VARBINARY(36) NOT NULL UNIQUE`, `quote LONGTEXT NOT NULL` w utf8mb4, `created BIGINT NOT NULL`, `state VARCHAR(16) NOT NULL` z porównaniem binarnym; nullable: `sid VARBINARY(255) UNIQUE`, `url TEXT`, `pi TEXT`, `owner VARBINARY(64)`. |
| `store_meta` | `name VARBINARY(64) PRIMARY KEY`, `value TEXT NOT NULL`. Zachować `mode=test/live`, przewidzieć jawny znacznik wersji schematu. Nie domyślać trybu po nazwie DB. |
| `attempts` | `identity VARBINARY(64)`, `bucket BIGINT`, `n BIGINT`, wszystkie NOT NULL; PK `(identity,bucket)`. Dodać indeks `bucket` dla istniejącego DELETE starych rekordów. To identyfikator sesji lub HMAC IP, nie jawne IP. |
| `events` | `id VARBINARY(255) PRIMARY KEY`; zapis w tej samej transakcji co obsługa zamówienia. Brak potrzeby dodawania pełnego webhooka lub danych płatnika. |

Klucze muszą zachować rozróżnianie bajtów/wielkości liter. Domyślne porównanie MySQL bez rozróżniania wielkości liter zmieniłoby zachowanie SQLite; `requestId` obecnie dopuszcza litery obu wielkości, bez normalizacji. Zachować wiele NULL w `orders.sid`. Nie wprowadzać indeksów prefiksowych osłabiających unikalność. Limity 32/64/128/255 są nowymi limitami adaptera: przed importem zweryfikować wszystkie identyfikatory, odrzucać przekroczenia, nigdy ich nie obcinać. W `quote` zachować zwykły tekst JSON i dotychczasową walidację PHP; natywny typ JSON nie jest potrzebny do obecnych zapytań.

### Transakcje, rezerwacja, idempotencja i blokady

**Samo `BEGIN IMMEDIATE` → `beginTransaction()` byłoby niewystarczające.** Proponowany kontrakt:

- **Rezerwacja nowej próby:** zachować szybki odczyt istniejącego `req` i walidację punktu poza transakcją. W nowej transakcji MySQL najpierw próbować INSERT zamówienia z unikalnym `req`, następnie pomniejszać wszystkie SKU i dopiero COMMIT. Wpis jest niewidoczny jako zatwierdzony do chwili commit; niedobór wycofuje także INSERT. Duplikat na indeksie `req`: pełny rollback, świeży odczyt zwycięskiego zamówienia i istniejące `existing_order()`. Nie uznawać każdego błędu 1062, np. kolizji `id` lub `sid`, za poprawną powtórkę. To zapobiega drugiemu pobraniu zapasu także wtedy, gdy pierwsza próba zużyła ostatnią sztukę. Nie opierać ochrony nieistniejącego `req` wyłącznie na SELECT.
- **Zapas wielu SKU:** pozostawić warunkowy UPDATE i wymaganie jednej aktualizacji na SKU. Kolejność blokowania ustalić przez sortowanie kluczy pomocniczej listy SKU zarówno przy pobraniu, jak i zwrocie. Zachować pierwotną kolejność `ordered` i `packs.members` w JSON; ma znaczenie dla zgodności powtórek. Nie używać `SKIP LOCKED` do decyzji o braku produktu.
- **Webhook:** w transakcji zająć unikalne `events.id`, następnie odczytać właściwe zamówienie przez `SELECT ... FOR UPDATE`. Dwie różne wiadomości dotyczące tego samego zamówienia muszą kolejno zobaczyć aktualny stan, żeby nie zwrócić zapasu dwukrotnie. Duplikat eventu ma być sukcesem idempotentnym bez zmiany zapasu; każdy błąd walidacji cofa również zapis eventu. Unikalność `events.id` sama nie serializuje różnych eventów dla jednego zamówienia. Zachować wszystkie kontrole SID, kwoty, waluty, metadanych, trybu i istniejącą maszynę stanów. [MySQL: locking reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html)
- **Przypięcie Stripe:** `bind_session()` obecnie odrzuca `rowCount()==0`. MySQL domyślnie może zwrócić zero przy ponownym zapisaniu identycznego SID/URL, mimo dopasowanego zamówienia. Rekomendowane: krótka transakcja, odczyt zamówienia z blokadą, kontrola `reserved` i zgodnego SID, jawny sukces dla identycznego powtórzenia. Alternatywa minimalna: `PDO::MYSQL_ATTR_FOUND_ROWS` ustawione przy tworzeniu połączenia, z testami wszystkich zależnych UPDATE. Nie usuwać kontroli stanu ani konfliktu SID. [PHP: ATTR_FOUND_ROWS](https://www.php.net/manual/en/class.pdo-mysql.php#pdo-mysql.constants.attr-found-rows)
- **Usługi zewnętrzne:** Stripe nadal poza transakcją z kluczem równym stabilnemu `orders.id`. Nie generować nowego ID po niejednoznacznym timeout. Rozważyć w testach webhook docierający przed `bind_session()`; zachować obecne odrzucenie bind dla zakończonej/pending próby, bez cofania stanu z webhooka. Adapter nie ma automatycznie zwalniać zapasu po błędzie sieci ani po wejściu na stronę anulowania.
- **Rate limit:** zastąpić SQLite `ON CONFLICT(identity,bucket)` wariantem MySQL `ON DUPLICATE KEY UPDATE n=n+1`. Odczyt licznika i decyzja 429 zostają w tej samej transakcji; przekroczenie wycofuje wszystkie jej inkrementacje, jak obecnie. Ujednolicić kolejność kluczy, zachować czyszczenie starych koszyków i retry tego samego requestu właściciela. [MySQL: UPSERT](https://dev.mysql.com/doc/refman/8.4/en/insert-on-duplicate.html)
- **Izolacja i retry:** ustalić jawnie izolację, proponowane READ COMMITTED z powyższymi blokadami i constraintami. Nie polegać na domyślnych ustawieniach hostingu. `tx()` MySQL musi bezpiecznie obsłużyć wyjątki i rollback tylko aktywnej transakcji. Ograniczony retry całej transakcji przy deadlock/lock timeout, np. maksymalnie 3 próby z opóźnieniem; nie ponawiać błędów biznesowych. Timeout wymaga pełnego rollback przed retry. Nie ponawiać w tej pętli Stripe/InPost. Niejasny wynik COMMIT po utracie połączenia wymaga ponownego odczytu przez `req`/event ID; nigdy nowego identyfikatora. [MySQL: obsługa deadlocków](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)

Zakres pozostaje małym adapterem, bez ORM, przebudowy koszyka, nowych statusów czy nowego modelu magazynu. Zmiany plików API wpłyną na istniejący fingerprint `live_approval()` (`api/_live.php:31`); nie wolno automatycznie przepisać zatwierdzenia Live ani ustawić flag zgód, żeby obejść ten efekt. Webhookowa ścieżka `deployment(true)` musi nadal działać po wstrzymaniu nowych zakupów.

## 4. Testy do implementacji i późniejszego wykonania

**W tym zadaniu: przegląd kodu testów, bez ich uruchamiania.** Obecne testy DB korzystają z SQLite `:memory:` lub prywatnego pliku; ich dotychczasowy PASS nie jest dowodem kompatybilności MySQL. Dla opcji B potrzebne są wspólne scenariusze na obu sterownikach, a testy współbieżności na osobnych procesach/połączeniach. Jedno połączenie lub `:memory:` nie symuluje konkurujących klientów.

| Istniejący test / obszar | Zachować lub dodać w wariancie MySQL |
| --- | --- |
| `tests/checkout-sandbox.php:36–69` | Fabryka izolowanej DB zamiast stałego `:memory:`. Rezerwacja, powtórka, konflikt, rollback po braku późniejszego SKU, zwrot dokładnie raz, pending/paid/review, spóźnione expired. Zachować dotychczasowe oczekiwania wyceny bez zmiany cen. |
| `tests/checkout-live-gates.php` | Rozdzielić testy prywatności konfiguracji od warunków pliku SQLite. Nadal odrzucać brak HTTPS, złe konto/tryb ledgeru, brak zgód i zmieniony fingerprint; zachować callback po zmianie wydania. Dodać odmowę złej konfiguracji MySQL i braku schematu bez ujawniania DSN/hasła. |
| `tests/checkout-locker.php`, `tests/inpost-mock.php` | Idempotentne wznowienie przy awarii katalogu punktów, brak rezerwacji przed pozytywną walidacją, kanoniczny zapis adresu, blokada mocka w Live; oba sterowniki. |
| `tests/inpost-mock-http.cjs` + launcher | Obecnie jawnie wymaga pliku SQLite w `.artifacts/inpost-mock-demo` i odczytuje go przez PHP. Wariant MySQL musi mieć osobną izolowaną konfigurację/znacznik celu; nie usuwać ochrony loopback ani dopuszczać przypadkowego DSN hostingu. |
| `tests/inpost-mock-ui.cjs` | Zachować jako regresję UI/mock; sam nie weryfikuje transakcji MySQL. Obecny build go uruchamia. |
| `tests/stripe-sandbox-probe.php` | Osobna, opcjonalna integracja po akceptacji. Dziś wymaga `stripe-probe.sqlite` i bezpośredniego PDO SQLite. Nie uruchamiać w domyślnym CI; nie przekazywać rzeczywistych kluczy do testów adaptera. |

Nowe przypadki akceptacyjne adaptera:

1. Dwie jednoczesne próby zakupu ostatniej sztuki: jedna rezerwacja, drugi klient dostaje STOCK; stan nigdy ujemny. Koszyki A/B i B/A: poprawny wynik lub kontrolowany retry, bez częściowej rezerwacji.
2. Ten sam `req` równolegle: jeden order, jeden ubytek; zgodne żądania wracają z tym samym ID, a inny właściciel/skład/punkt/wersja zgody dostaje REQUEST_CONFLICT. Osobno test przy wyczerpaniu zapasu przez zwycięską próbę i po zmianie polityki — powtórka zachowuje zapisaną wycenę.
3. Dwa identyczne eventy oraz dwa różne expired/failed tego samego zamówienia: pojedynczy zwrot. Paid przeciw expired: stan i zapas zgodne z kolejnością blokad; sukces po released daje review. Brak wpisu `events` po EVENT_MISMATCH i pełny rollback przy błędzie w połowie zwrotów.
4. Dwukrotne i równoległe `bind_session()` z tym samym SID/URL: brak fałszywego FINISHED. Inny SID lub SID przypisany do innego zamówienia: odmowa. Webhook przed bind nie może zostać nadpisany.
5. Timeout Stripe przed/po utworzeniu sesji: ta sama rezerwacja, ten sam klucz idempotencji; żadnego dodatkowego odjęcia. Symulacje transportu domyślnie bez HTTP. Niepewny COMMIT: odczyt poprzedniej próby, nie nowa rezerwacja.
6. Wymuszony deadlock, lock timeout, błąd SQL i zerwane połączenie: brak częściowych zmian, zamknięte transakcje, ograniczona liczba retry i przewidywalny błąd bez danych dostępowych. Sprawdzić także, że celowo wolny resolver nie trzyma blokady DB.
7. Rate limit na wielu połączeniach: dokładna granica limitu, rollback obu liczników po przekroczeniu jednego, zgodny retry właściciela, czyszczenie koszyków bez utraty bieżących liczników.
8. Schemat: klucze unikalne, rozróżnianie wielkości liter, wiele NULL SID, polskie znaki/emoji i JSON, int w odpowiedzi `stock()`, rollback constraintów i przepełnień. Seed tylko pustego ledgeru; testowy ledger nigdy nie akceptowany jako Live. Nieznany sterownik, brak rozszerzenia lub niezgodny schemat zamykają zakupy.

Środowisko przyszłych testów: efemeryczna baza ze sztucznymi stanami, silnik/wydanie zgodne z ustaleniami LH; bez klientów i sekretów hostingu. Runtime testować także kontem DML bez praw CREATE/ALTER, żeby wykryć ukryte DDL w `database()`. Po przejściu testów lokalnych/CI osobny odbiór przez rzeczywiste PHP-FPM i HTTPS stagingu; test CLI nie dowodzi praw FPM ani routingu webhooka.

## 5. GitHub Actions: możliwości i granice

W przejrzanym drzewie nie ma katalogu `.github`; nie sprawdzano ustawień ani historii Actions w usłudze. `scripts/build_release.py:20–43` wymaga czystego checkoutu, uruchamia istniejące kontrole i testy PHP/JS; linie 44–74 tworzą ZIP, manifest i raport SHA. Buduje lokalnie, bez uploadu. `check_publication.py` odczytuje też historyczne commity, więc CI musi pobrać wymagane obiekty Git, np. pełną historię. Lokalny `PF_GIT_DIR` nie jest ścieżką do przeniesienia na runner.

Actions wykonuje job na wybranym runnerze. Może pobrać kod, uruchomić PHP/Node/Python, testować adapter na efemerycznej usłudze MySQL i wyprodukować artefakt. Taki MySQL jest bazą testową runnera, nie bazą LH. Kontenery usług wymagają Linux/Ubuntu w wariancie GitHub-hosted. [Runner](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job), [kontenery usług](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)

**Repo access ≠ runtime access.** Token GitHub nie daje dostępu do LH, jego panelu, DB, plików prywatnych, logów ani ustawień PHP-FPM. FTPS umożliwia operacje plikowe w zakresie konta; nie jest SSH i nie zapewnia zdalnego PHP/CLI. Kontrola HTTP z runnera nie jest wglądem w proces FPM. Nie proponuje się webowego endpointu do migracji/diagnostyki z szerokimi prawami ani instalacji self-hosted runnera na LH jako obejścia.

Minimalny przyszły pipeline C: zaufany checkout określonego SHA → zależności i testy offline → opcjonalne izolowane testy MySQL → istniejący build → artefakt ZIP + manifest + release.json. Bez nowych plików workflow w tym zadaniu. Oddzielny opt-in probe Stripe nie jest częścią tego przebiegu.

W D: ręczny wybór już sprawdzonego SHA/artefaktu, chronione środowisko `lh-staging`, akceptacja operatora, jeden upload naraz, zamknięta lista hosta i katalogu, weryfikacja hashy oraz zachowanie poprzedniego wydania. WinSCP działa u operatora, ale to nie dowodzi pracy `ftplib` na runnerze. Można osobno przetestować klienta WinSCP na runnerze Windows lub aktualny skrypt na zgodnym runnerze; testy MySQL w kontenerze zostają w jobie Linux.

`scripts/stage_lh.py:15–31,43–62` sprawdza paczkę, używa explicit FTPS z walidacją TLS i szyfrowaniem kanału danych, tworzy nowy katalog i odczytuje pliki z powrotem do kontroli hashy. Nie przełącza vhosta, nie rozpakowuje zdalnie SQL i nie tworzy DB. Upload do nowego katalogu nie jest atomową aktywacją strony. Katalog pod `public_html` może być osiągalny inną domeną; ochronę stagingu trzeba ustalić przed wgraniem. Build nie dołącza szablonów `.htaccess` z `ops/lh` automatycznie. Aktywacja/rollback vhosta pozostają osobnym krokiem operatora.

### Minimalne sekrety i permissions — propozycja, bez konfiguracji

| Cel | Minimalne dane / uprawnienia |
| --- | --- |
| CI/build tego repo | Automatyczny `GITHUB_TOKEN`, jawne `contents: read`; bez PAT, bez sekretów dostawców. Sztuczne dane efemerycznej DB wyłącznie na czas joba, bez powiązania z LH. |
| Pobranie artefaktu innego runu | `actions: read`, tylko gdy wybrany mechanizm rzeczywiście tego wymaga. Sam upload artefaktu builda nie uzasadnia `contents: write`. |
| Zatwierdzony upload FTPS | Oddzielny login stagingu i hasło, np. istniejące nazwy `PF_FTPS_USER`, `PF_FTPS_PASSWORD`, tylko w jobie deploy/środowisku staging. Host i katalog to kontrolowane ustawienia, nie hasła. Konto ograniczone do własnego drzewa stagingu. |
| Rejestrowanie Deployment przez API GitHub | `deployments: write` tylko przy świadomym użyciu tego API. Zwykły FTPS nie wymaga go, `pages: write`, `contents: write` ani `id-token: write`. OIDC ma sens dopiero przy odbiorcy, który mu ufa; nie zastępuje hasła FTPS. |
| Runtime MySQL na LH | Osobna nazwa bazy, użytkownik i hasło; konto aplikacji SELECT/INSERT/UPDATE/DELETE wyłącznie na własnych tabelach. DDL osobnym kontem operatora; bez globalnych uprawnień, GRANT/FILE/SUPER. Sekrety runtime nie są potrzebne jobowi wysyłającemu pliki. |
| Odbiór Stripe Sandbox | Testowy klucz API, sekret podpisu webhooka i token testera/prywatny hash, tylko w odrębnym zatwierdzonym teście. Nie przekazywać kluczy Live. Prywatny token Points, jeśli potrzebny, pozostaje backendowy; publiczny token Geowidget nie zastępuje go. |
| OVH DNS / SSL | Żadne sekrety OVH ani klucze prywatne TLS nie są wymagane do CI/build/FTPS. Ewentualna późniejsza automatyzacja DNS to osobny zakres z osobnymi credentialami i akceptacją. |

Sekrety deploy udostępniać dopiero po regułach chronionego środowiska; dostępność required reviewers zależy od planu i widoczności repo — sprawdzić ją przed wyborem D. Dopuszczać zaufane refy, przypinać akcje do pełnych SHA, chronić zmiany workflow i nie uruchamiać kodu niezaufanego PR z sekretami przez `pull_request_target` ani uprzywilejowane `workflow_run`. Maskowanie nie gwarantuje ukrycia przekształconego sekretu; nie zapisywać konfiguracji prywatnej w logach/cache/artefaktach. [GitHub: secure use](https://docs.github.com/en/actions/reference/security/secure-use), [środowiska deployment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)

### OVH API, FTPS i klucze SSL

- **OVH API:** standardowe poświadczenia aplikacji obejmują application key, application secret i consumer key; zakres jest opisywany metodami i ścieżkami API. Jeśli kiedykolwiek zatwierdzona zostanie automatyzacja DNS, ograniczyć ją do potrzebnych metod i ścieżek konkretnej strefy/rekordów, z krótkim czasem ważności i planem unieważnienia. Nie używać ogólnego `/*`. Uprawnienie do tworzenia rekordów w całej strefie nie jest automatycznie ograniczeniem do nazwy `test` — dodatkowa kontrola payloadu jest konieczna. Błąd albo wyciek może naruszyć WWW, MX/TXT i pocztę. API OVH nie naprawia praw PHP na LH. Obecny zakres nie wymaga zmian DNS. [OVHcloud: API i zakresy dostępu](https://docs.ovhcloud.com/en/guides/manage-and-operate/api/first-steps)
- **FTPS:** zachować weryfikację certyfikatu serwera i szyfrowanie obu kanałów, bez „accept any” ani powrotu do FTP. Dane konta FTPS mogą umożliwić podmianę PHP, a więc pośrednio odczyt sekretów przez aplikację; izolacja katalogu i zaufany job są istotne nawet bez haseł DB w Actions. Nie włączać synchronizacji kasującej zawartość ani uploadu prywatnego JSON/SQLite. Certyfikat serwera FTPS i certyfikat `test.pracowniaform.com` są odrębnymi kontrolami — działający WinSCP nie oznacza działającego HTTPS sklepu. [WinSCP: FTPS](https://winscp.net/eng/docs/ftps), [walidacja TLS](https://winscp.net/eng/docs/tls)
- **SSL/TLS strony:** preferowana obsługa certyfikatu i odnowienia przez LH. Nie kopiować klucza prywatnego strony do repo, artefaktu ani joba FTPS; publiczny certyfikat i klucz prywatny mają różną poufność. Sama paczka aplikacji nie instaluje certyfikatu vhosta. Gdyby operator wybrał zewnętrzny ACME/DNS, wymaga to osobnej decyzji o kluczu konta ACME, uprawnieniach DNS, miejscu instalacji i odnowieniu, nie tylko jednorazowego wygenerowania pliku. [LH: konfiguracja Let's Encrypt](https://www.lh.pl/pomoc/doc/jak-uruchomic-certyfikat-ssl-lets-encrypt-na-serwerze-w-lh-pl/)

## 6. Warunki następnego kroku i granice migracji

Do wyboru A/B potrzebne są od LH: rzeczywisty silnik i wersja DB, endpoint/socket i dostęp z PHP-FPM, obecność `pdo_mysql` lub `pdo_sqlite`, dopuszczona prywatna lokalizacja konfiguracji, użytkownik/prawa FPM oraz sposób zapewnienia SSL i odnawiania dla stagingu. Obecny fallback `.pf-private` poza `www` nie gwarantuje niedostępności przez inne vhosty wskazujące nadrzędny `public_html`; należy objąć kontrolą wszystkie ścieżki publiczne. Nie obchodzić odmowy dostępu przez umieszczenie sekretów w ogólnie serwowanym katalogu albo `chmod 777`.

MySQL usuwa konieczność pliku SQLite, ale nie hasła DB, sekretu Stripe, konfiguracji ani działających sesji PHP. Obecne bramki wymagają HTTPS i cookies Secure; bez poprawnego SSL staging nie jest gotowy do odbioru zakupowego niezależnie od bazy.

Przyszła migracja danych wymaga osobnego planu po potwierdzeniu, czy istnieje ledger do zachowania. Należy przenieść spójnie wszystkie pięć tabel, zachować `req`, ID/SID, JSON i stany rezerwacji, porównać liczniki oraz zaplanować obsługę opóźnionych webhooków i rollback. Nie odtwarzać dostępnego zapasu wyłącznie z początkowych liczb, nie mieszać test/live i nie przełączać dwóch niezależnie zapisywanych ledgerów. Ten dokument nie wybiera okna migracji i nie upoważnia do tworzenia bazy.

Do akceptacji są zatem konkretne zakresy **A lub B**, niezależnie **C**, a po odbiorze infrastruktury ewentualnie **D**. Odbiór B oznacza adapter i testy z zachowaniem kontraktu; odbiór C oznacza artefakt bez sekretów; odbiór D oznacza kontrolowany upload stagingu. Żaden z nich sam w sobie nie potwierdza działania sklepu na LH ani gotowości Live.
