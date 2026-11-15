# Krótkotrwała sonda odbioru prywatnego runtime LH

**LOCAL ONLY / LH UNRUN — 14.11.2026.** Kontynuacja [PR #28, komentarz 6877154112](https://github.com/pracowniarachunkowosci-debug/form/pull/28#issuecomment-6877154112), punkt odniesienia HEAD `9cb6100e6368c125e9fc6cbde6958496838c490d`. LH nie wskazało jeszcze prywatnej ścieżki. Sonda nie zgaduje lokalizacji i nie ponawia starego `mkdir HOME`. Nie wykonano uploadu, połączenia z hostingiem, zdalnego testu ani zmian aplikacji.

Pliki tego zakresu:

- `scripts/lh_runtime_acceptance.php.in` — samodzielny szablon sondy; poza buildem aplikacji.
- `tests/lh-runtime-acceptance.py` — lokalne fixture’y i testy odmów/cleanup/SQLite.
- Ten dokument — warunki przygotowania i interpretacja odpowiedzi.

## Co operator musi wcześniej uzgodnić z LH

Istniejący, dokładnie wskazany prywatny runtime ma mieć strukturę:

```text
<PRIVATE_ROOT>/
  config/
    lh-runtime-probe-fixture.txt
  data/
```

Sonda nie tworzy tych trzech katalogów ani fixture’a. Nie czyta rzeczywistej konfiguracji sklepu. Operator dostarcza **wyłącznie niesekretny** fixture o dokładnej treści poniżej, zakończonej jednym LF:

```text
PF-RUNTIME-PROBE-NONSECRET-v1
```

PHP-FPM stagingu ma odczyt fixture’a oraz przejście przez rodziców. Fixture, `config/` i sam `<PRIVATE_ROOT>` nie mogą być zapisywalne dla FPM; chroni to również przed podmianą katalogu `config`. W `data/` FPM potrzebuje tworzenia plików/katalogu własnej próby, zapisu, rename i usuwania. Sonda nie zmienia uprawnień, nie nadpisuje istniejącego config/ledgeru, nie inicjalizuje sklepu. Jeśli LH proponuje inny układ niż `config/` i `data/`, wymaga to jawnego dopasowania i ponownego przeglądu szablonu, bez zgadywania ścieżek.

**LH musi osobno potwierdzić inwentaryzację wszystkich webrootów, vhostów, aliasów, symlinków i ścieżek domeny technicznej oraz izolację innych procesów.** `realpath` i porównanie z pojedynczym document root nie dowodzą niepubliczności całego runtime. Nie wykonujemy testów z vhosta innej firmy ani przeszukiwania jej katalogów. Sonda nie jest narzędziem do konfiguracji ochrony HTTP/webhooka.

## Pięć placeholderów, przygotowanie poza WWW

| Placeholder | Dokładne znaczenie |
| --- | --- |
| `@PRIVATE_ROOT@` | Istniejący kanoniczny katalog runtime wskazany przez LH; bez końcowego separatora, `.`/`..`, symlinków i aliasów. |
| `@WEBROOT@` | Dokładny kanoniczny document root `test.pracowniaform.com`, w którym tymczasowo będzie plik sondy. Nie wyprowadzać go z HOME ani ścieżki FTPS. |
| `@TOKEN_SHA256@` | Mały hex SHA256 nowego tokena. Token: 32 losowe bajty zapisane jako 64 małe znaki hex; hash liczyć z tych 64 znaków ASCII. |
| `@ISSUED_UNIX@` | Początek ważności, 10-cyfrowy Unix timestamp UTC. |
| `@EXPIRES_UNIX@` | Koniec ważności; większy od issued, maksymalnie 900 sekund później. Przy `now >= expires` odmowa. |

Wszystkie placeholdery są ujęte w PHP w pojedyncze cudzysłowy. Podstawiać jako **dane**, z poprawnym escapowaniem PHP; nie wykonywać interpolacji powłoki. Szablon celowo przechodzi lint również przed podstawieniem, ale nierozwiązane placeholdery nie dopuszczą requestu. Ścieżki POSIX ograniczone są do znaków liter/cyfr, `_`, `-`, `.`, `/`; brak obsługi dowolnych znaków/URL. Nie rozszerzać tej listy bez potrzeby i ponownego testu.

Raw token, ewentualny plik nagłówka requestu oraz robocze pliki przygotowania pozostają **poza wszystkimi WWW**, z minimalnym dostępem operatora. W pliku sondy znajduje się wyłącznie hash. Nie podawać tokena w URL, body, argumentach polecenia widocznych w historii, logach, zrzutach ekranu ani repo. Nie używać rzeczywistego hasła/tokena aplikacji. Renderować i lintować kopię prywatnie; do użycia po wskazaniu ścieżki przez LH i sprawdzeniu zakresu przeznaczyć nową, unikalną nazwę PHP, nigdy nie nadpisywać istniejącego pliku.

Przed ewentualnym użyciem operator musi zweryfikować, że plik wykonywany jest jako PHP i że odpowiedzi błędów PHP nie ujawniają kodu/ścieżek. Sonda wyłącza `display_errors`, `display_startup_errors` i `log_errors` na czas requestu oraz tłumi komunikaty warning; **błąd składni przed wykonaniem skryptu lub konfiguracja serwera są poza jej kontrolą**. Dlatego wymagany jest lint konkretnej wyrenderowanej kopii. Wykonanie na LH pozostaje wstrzymane do wskazania prywatnej ścieżki i potwierdzenia zakresu przez operatora; zgoda właściciela na taki warunkowy test jest już zapisana w PR.

## Bramki requestu i zakres plików

Każdy warunek jest obowiązkowy; brak któregokolwiek daje HTTP 404 i tylko stały JSON `not_found`:

- SAPI dokładnie `fpm-fcgi`; prawdziwe CLI nie może uruchomić próby.
- `HTTPS` dokładnie `on`, port serwera `443`; `X-Forwarded-Proto` nie jest dowodem TLS.
- Host dokładnie `test.pracowniaform.com`, bez dopisanej domeny czy `:443`; metoda wyłącznie POST.
- Poprawny przedział czasu do 15 minut i token wyłącznie z `X-PF-Probe-Token`, o dokładnym formacie, porównany przez `hash_equals` z hashem.

Po autoryzacji sprawdzane są dokładne `__DIR__`, `DOCUMENT_ROOT`, `SCRIPT_FILENAME` oraz `__FILE__`. Każdy istniejący komponent skonfigurowanych ścieżek musi mieć oczekiwany typ, zgodny `realpath` i nie może być symlinkiem. Niedopuszczalne są dot-segmenty, podwójne separatory, twarde linki do plików oraz nakładanie się skonfigurowanego runtime i webroota. Linux/POSIX jest docelowym środowiskiem; obsługa rodzimych ścieżek Windows służy lokalnym fixture’om.

Sonda zapamiętuje tożsamość katalogów (device/inode/type) i sprawdza ją przed operacjami własnych plików oraz sprzątaniem. Nie pobiera HOME/env/UID, nie wywołuje `phpinfo`, nie zwraca praw, nazw katalogów, zawartości plików, SQL ani tekstów wyjątków. To kontrola ścieżek i aktualnych praw FPM, nie dowód izolacji od równolegle działającego uprzywilejowanego procesu; ten warunek wymaga potwierdzenia LH.

## Rzeczywiste operacje próby

1. **Config:** odczyt ograniczony do 128 bajtów ze stałego niesekretnego fixture’a; porównanie dokładnej treści i tożsamości otwartego pliku. Kontrola braku zapisu fixture/config/private root przez `is_writable`. Dodatkowo próba stworzenia pustego, losowego `pf-config-denial-<32hex>.tmp` przez `fopen('x+b')` musi zostać odrzucona. Nie otwiera istniejącego fixture’a do zapisu. Jeśli utworzenie canary niespodziewanie się powiedzie, wynik jest FAIL i cleanup usuwa tylko ten własny pusty plik.
2. **Data:** wyłącznie pod istniejącym `data/` powstaje nowy `pf-runtime-probe-<32hex>` z żądanym trybem 0700. W nim losowy plik `x+b`, zapis/odczyt losowego markera, rename na nową losową nazwę, ponowny odczyt i usunięcie. Kolizja nie jest traktowana jako własny plik ani powód do jego nadpisania.
3. **SQLite DELETE:** nowy plik DB rezerwowany najpierw przez `x+b`, dopiero potem PDO SQLite. Własna tabela z jedną syntetyczną liczbą; transaction rollback oraz commit z kontrolą danych. `PRAGMA journal_mode=DELETE` musi być potwierdzone, ale samo nie wystarcza: podczas obu transakcji wymagany jest rzeczywisty, regularny, niepusty plik `-journal`, po rollback/commit jego brak.
4. **SQLite WAL/SHM:** ten sam własny DB, potwierdzone WAL, wyłączony autocheckpoint. Po zapisie wymagane są **rzeczywiste niepuste** `-wal` i `-shm`, zgodne ścieżki i typy. Osobne połączenie czyta zatwierdzone dane. Sprawdzane są również rollback i commit w WAL. `wal_checkpoint(TRUNCATE)` musi zwrócić brak zajętości i opróżnić WAL; po zamknięciu obu połączeń wymagany jest brak WAL, SHM i journal.
5. **Cleanup:** zamknięcie/rollback połączeń również po wyjątku, usuwanie wyłącznie plików z rejestru własności, przy ponownej kontroli rootów, realpath i tożsamości plików. SQLite może wcześniej sam usunąć własny sidecar. Katalog próby usuwany jest tylko pusty. Brak rekursywnego delete, globowania istniejących DB, usuwania config/data ani „naprawiania” cudzych plików.

Przy zmianie rootu, podmianie pliku, obcym wpisie lub niemożności bezpiecznego usunięcia wynik to `cleanup_failed`, a nie próba szerszego kasowania. Handler zakończenia podejmuje ten sam ograniczony cleanup przy nieoczekiwanym zakończeniu PHP. Zabicie procesu/awaria hosta może uniemożliwić cleanup; nie ma gwarancji sprzątnięcia po takim zdarzeniu. Operator musi wtedy ocenić konkretną własną próbę bez zbiorczego kasowania. Wygaśnięcie tokena blokuje nowe requesty, nie usuwa samego endpointu — jego późniejsze usunięcie i kontrola 404 są osobnym obowiązkiem operatora po użyciu.

## Interpretacja JSON

Wartości pól są wyłącznie boolean; jedyny wyjątek to `error` z zamkniętej listy: `not_found`, `scope_rejected`, `config_rejected`, `data_failed`, `sqlite_failed`, `cleanup_failed`, `operation_failed`, `operator_verification_required`. Nie ma pola na exception/message/path.

| Pole / status | Znaczenie |
| --- | --- |
| `runtime_ok=true` | W tym requestcie przeszły wszystkie kontrole techniczne config/data/SQLite i cleanup. |
| `cleanup_ok=true` | Własne zarejestrowane pliki i katalog próby usunięte; lub odmowa nastąpiła przed utworzeniem czegokolwiek. |
| `operator_verified=false` | **Zawsze false w sondzie.** Wymagana niezależna inwentaryzacja i potwierdzenie LH/operatora, których JSON nie może sam wytworzyć. |
| `accepted=false` | **Zawsze false.** Nawet runtime PASS nie daje samodzielnej zgody na sekrety/aplikację. Odbiór operatora musi mieć osobny zapis dowodów. |
| HTTP 200 + `operator_verification_required` | Techniczna próba zakończona; oczekiwanie na osobną bramkę operatora. |
| HTTP 503 + bezpieczny kod fazy | Błąd po autoryzacji; nie kontynuować do danych rzeczywistych. |

Nie oznaczać wszystkich webrootów jako sprawdzonych na podstawie tego JSON. Nie utożsamiać `scope_ok` z dowodem braku dostępu przez techniczną domenę LH.

## Lokalna walidacja wykonana w tym zadaniu

**PASS: lint PHP 8.4.27 CLI i 30/30 scenariuszy. LH/FPM/HTTPS/ACL runtime pozostają UNRUN.**

```powershell
& .artifacts/tools/php/php.exe -l scripts/lh_runtime_acceptance.php.in
python -B tests/lh-runtime-acceptance.py
```

Testy używają tylko dedykowanego prywatnego katalogu poza repo:

```text
C:/Users/lsolt/.codex/visualizations/2026/09/04/01a06d6a-faec-75d1-a6c5-9a6946b9c460/pf-staging-private/runtime-probe-tests
```

Każda sesja tworzy świeży `pf-runtime-synthetic-*` przez exclusive `mkdtemp`; nie odczytuje żadnych innych plików prywatnego katalogu. Przed cleanup weryfikuje dokładny parent, granicę własnej sesji i brak przechodzenia przez symlink/junction. Zastosowano nowy token syntetyczny dla każdego przypadku, raw token wyłącznie w prywatnym wrapperze poza fixture WWW. Po testach usunięto własne sesje; dedykowany katalog testów pozostał pusty.

Sandbox początkowo blokował PHP odczyt prywatnego fixture’a. Ten sam test uruchomiony z eskalacją dostępu lokalnego przeszedł; nie oznaczało to zgody na sieć ani dostępu do prawdziwych sekretów. Nie zmieniano guardów sondy, by obejść sandbox.

**Jawne transformacje wyłącznie w wygenerowanej kopii syntetycznej:** test podmienia jedną deklarację SAPI na `fpm-fcgi`, a `$_SERVER` ustawia w osobnym prywatnym wrapperze CLI. Sprawdzenia host/HTTPS/POST/token/czas nadal wykonuje rzeczywisty kod guardów. Windows nie odwzorowuje praw POSIX FPM: dodatni scenariusz modeluje dwa wyniki polityki readonly (zbiorcze `is_writable` i odmowę tworzenia canary). Pozostałe operacje plikowe, realpath, rename, cleanup i SQLite działają na rzeczywistym filesystemie. Oddzielne scenariusze pozostawiają oryginalne sprawdzenia zapisu i potwierdzają FAIL oraz cleanup dla faktycznie zapisywalnego config. To nie jest pozytywny test ACL na LH.

Zakres przypadków: odmowa niezmodyfikowanej sondy w CLI; dodatni model FPM; HTTP/forwarded-proto/port/host/suffix/GET/token; zły document root/script filename; expiry/future/za długa ważność; traversal i alias katalogu (Windows junction); zły fixture i zapisywalny config; kolizja istniejącego pliku bez nadpisania; wyjątek bez ujawnienia ścieżki/stderr; cleanup po awarii z otwartym DELETE journal i WAL; obowiązkowa obecność WAL/SHM; odmowa cleanup przy zmienionej tożsamości rootu oraz zachowanie obcego pliku. Fault injection występuje tylko w prywatnych kopiach testowych, nigdy w szablonie do użycia na LH.

Brak remote PASS. Do kolejnego etapu potrzebna jest odpowiedź LH z kanoniczną prywatną ścieżką, strukturą/prawami i potwierdzeniem inwentaryzacji publicznych mapowań.
