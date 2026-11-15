# Points: lokalny pokaz i chroniony staging MOCK

**TEST / MOCK — bez połączenia z InPost**

Rzeczywisty odbiór InPost Sandbox: **BLOCKED — oczekiwanie na InPost, ticket F60AADBC18**.
Wyniki poniższych prób dotyczą wyłącznie syntetycznych punktów. Nie potwierdzają dostępu
do InPost, działania prawdziwej mapy, nadania, płatności ani webhooka Stripe.

## Lokalny interaktywny pokaz (Windows)

Z `C:\sklep\form`, w PowerShell:

```powershell
& 'C:\sklep\form\.artifacts\tools\php\php.exe' tests/inpost-mock-demo.php
```

Otwórz <http://127.0.0.1:8787/winter-zestaw-4.html?size=1&model=full-soft&color=marble#kompozycja>.
Wybierz dostawę do punktu, a następnie punkt/scenariusz z listy lub wpisz kod ręcznie.
Przycisk „Zapisz lokalną próbę — bez płatności” zapisuje prawdziwy snapshot zamówienia
w odizolowanej bazie SQLite. Nie wywołuje Stripe; stan pozostaje `reserved`.

Launcher wypisuje ścieżkę nowej bazy w `.artifacts/inpost-mock-demo/`. Przy każdym starcie
tworzy nową bazę z syntetycznymi stanami, bez zmiany katalogu, cennika lub istniejących baz.
Identyczny skład, punkt i metoda ponownie używają identyfikatora próby i jednej rezerwacji.
Zmiana punktu lub metody tworzy nową próbę. `Ctrl+C` kończy serwer; baza pozostaje do odczytu.
Jeśli port 8787 jest zajęty, zakończ wcześniejszą instancję tego demo; nie zatrzymuj innych usług.

Router działa tylko w PHP CLI server, z flagą ustawioną przez launcher, na loopback
i z lokalnym nagłówkiem Host. Obsługuje trzy konkretne endpointy demo oraz publiczne zasoby UI.
Nie udostępnia źródeł PHP, testów, konfiguracji, baz, seedera ani przeglądarki zamówień.
CSP blokuje zewnętrzne zasoby, formularze i połączenia przeglądarki, a proces PHP ma wyłączone
funkcje klientów sieciowych. Nie zmienia to `configuration()`, wymagań HTTPS ani logowania testera.
Nie uploaduj launchera/routera; istniejący build wydania nie pakuje `tests/`.

## Chroniony staging testowy

W istniejącej **prywatnej konfiguracji testowej** poza webroot dodaj tylko:

```json
{"inpost_points_mock": true}
```

To fragment konfiguracji, nie jej zamiennik. Zachowaj istniejący HTTPS, origin, osobną bazę
`mode=test`, dostęp testera i konfigurację Stripe Sandbox. Usuń z tej konfiguracji pola
`inpost_points_token` oraz `inpost_geowidget_token` — także puste wartości. MOCK nie używa
żadnego tokenu InPost ani Geowidget. Nie wykorzystuj wcześniej ujawnionego tokenu.

Status po uwierzytelnieniu testera zwraca `points_provider: "mock"`, oznaczenie TEST/MOCK
i listę kodów/scenariuszy bez adresów. UI nie ładuje Geowidget i nie pokazuje lokalizatora InPost.
Adres pochodzi z serwerowego adaptera: picker i JSON checkoutu wysyłają tylko kod punktu.
`pickup-point.php` i checkout zachowują istniejące bramki testera/origin/bazy.

Wyłącznie dokładne `true` z `mode=test` włącza adapter. Obecna flaga z dowolną inną wartością,
trybem `live`, brakującym trybem lub tokenem InPost jest odrzucana przez adapter (`POINTS_CONFIG`).
Status w takim przypadku pozostaje zamknięty. UI odrzuca także odpowiedź Live z danymi MOCK.
Kody `TEST…` są odrzucane przed jakimkolwiek wywołaniem rzeczywistego providera.
Nie ma konfigurowalnego URL upstream, automatycznego fallbacku ani przełączenia na produkcję.
Aby przywrócić istniejącą integrację po odblokowaniu Sandbox, **usuń** flagę MOCK i dopiero
wtedy skonfiguruj właściwą parę tokenów Sandbox. Nie ustawiaj `false` jako obejścia walidacji.

## Scenariusze

| Kod | Oczekiwane zachowanie |
|---|---|
| `TEST01M` | Punkt A, fikcyjny adres 1 |
| `TEST02M` | Punkt B, fikcyjny adres 2 |
| `TESTOFF` | Nieczynny punkt, 422 `PICKUP_POINT` |
| `TESTBAD` | Nieprawidłowy adres z API, 422 `PICKUP_POINT` |
| `TESTBROKEN` | Nieprawidłowa struktura odpowiedzi, 503 `POINTS_UNAVAILABLE` |
| `TESTERROR` | Symulowana awaria API, 503 `POINTS_UNAVAILABLE` |
| `TESTUNKNOWN`, `WRO01M`, niepoprawny format | Odrzucenie, bez połączeń z InPost |

Adresy obu poprawnych fixture zawierają pełny napis „TEST / MOCK — bez połączenia z InPost”.
Ten napis i kod `TEST…` są utrwalane w `orders.quote.pickup_address` / `pickup_point`
i w przygotowanych metadanych płatności; operator nie powinien pomylić próby z prawdziwym punktem.
Nie dodano nowych pól wejściowych checkoutu. Podany przez klienta adres jest odrzucany.

Sprawdź wybór A → B, ręczne ` test01m `, nieprawidłowy kod, każdy scenariusz błędu,
wyczyszczenie wyboru oraz przełączenie na kuriera. Błąd punktu blokuje zamówienie do punktu
i nie rezerwuje zapasu. Kurier nie niesie `pickup_point` ani adresu automatu.

Ceny pozostają 50 / 84 / 150 / 220 / 290 zł dla 1 / 2 / 4 / 6 / 8 szt.
Kurier: 20,49 zł; punkt: 18,49 zł; od 6 szt. 0 zł. 2+4 = 234 zł z darmową dostawą.
Pojedyncza sztuka: 70,49 zł kurierem lub 68,49 zł do punktu. Kod rabatowy pozostaje nieaktywny.

## Powtarzalne testy

```powershell
$env:PF_PHP_BIN='C:\sklep\form\.artifacts\tools\php\php.exe'
& $env:PF_PHP_BIN tests/checkout-sandbox.php
& $env:PF_PHP_BIN tests/checkout-live-gates.php
& $env:PF_PHP_BIN -d 'disable_functions=curl_init,curl_exec,fsockopen,pfsockopen,stream_socket_client' tests/checkout-locker.php
node tests/inpost-mock-ui.cjs
node scripts/check_store_composition.cjs
```

`checkout-locker.php` obejmuje także `tests/inpost-mock.php`: blokady trybu i tokenów,
scenariusze fixture, niezmienione ceny/progi, zapis ID/adresu, brak rezerwacji przy błędzie,
idempotencję i przełączenie kuriera. Test UI uruchamia rzeczywisty `winter-config.js`
w izolowanym DOM, z odpowiedziami wygenerowanymi przez PHP, bez przeglądarki/sieci.

Gdy demo jest uruchomione, w drugim terminalu:

```powershell
node tests/inpost-mock-http.cjs 'C:\sklep\form\.artifacts\inpost-mock-demo\PLIK-WYPISANY-PRZEZ-LAUNCHER.sqlite'
```

To smoke test wyłącznie `127.0.0.1:8787`: sprawdza HTTP, CSP, zabezpieczenia host/origin,
wybór/adres, błędy, idempotencję, kuriera i 2+4 oraz odczytuje zapisane zamówienia w wskazanej
bazie demonstracyjnej. Dodaje wyłącznie syntetyczne rezerwacje do tej konkretnej bazy.
W sandboxie aplikacji Windows PHP `is_readable()` może błędnie zwracać false; uruchomienie
lokalnych testów poza sandboxem rozwiązuje ograniczenie, bez zmiany bramek aplikacji.

Rzeczywiste UI/screenshoty na 320 / 360 / 390 / 430 px pozostają osobnym odbiorem.
Płatność karta/BLIK, podpis webhooka i dane konta Stripe wymagają osobnego testu Sandbox.
