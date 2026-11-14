# Decyzja: prywatna konfiguracja stagingu LH

14.11.2026, zadanie weekendowe z [PR #28](https://github.com/pracowniarachunkowosci-debug/form/pull/28#issuecomment-6876261610). **Rekomendacja: zachować SQLite i uzyskać jeden dedykowany katalog poza wszystkimi webrootami, z minimalnymi prawami PHP-FPM tego stagingu.** W obecnym zakresie samoobsługowego panelu nie znaleziono bezpiecznej, kompletnej alternatywy. Nie oznaczamy infrastruktury jako PASS i nie wgrywamy aplikacji ani sekretów.

## Dowody zamiast założenia o możliwościach hostingu

- Faktyczny PHP-FPM uruchomiony na `test.pracowniaform.com` potwierdził zgodny HOME/realpath, brak ustawionego open_basedir i działający zapis w swoim WWW. Utworzenie `.pf-private` oraz losowego katalogu obok `public_html` zakończyło się **Permission denied**. To nie błąd FTP. [Wynik testu i cleanup](staging-20261114/php-fpm-private-anonymized.json).
- Konto FTPS `serwer533947_pfstage14` jest ograniczone do `/public_html/pf-stage-20261114`; WinSCP działa. Jego katalog `/` nie jest systemowym HOME. Nie użyto głównego konta FTP ani nie rozszerzano uprawnień.
- Ponownie obejrzano panel vhosta **1711054** i serwera **533947**. Vhost udostępnia PHP/SSL/katalog/separację, bez pola env lub prywatnego pliku. Panel serwera Orange pokazuje brak SSH i Redis. Nie ma samoobsługowego edytora puli FPM ani prywatnej konfiguracji aplikacji. To zakres widocznego UI, nie zapewnienie, że operator nie może skonfigurować takiej funkcji.
- Formularz nowego konta FTP pozwala wskazać **istniejący** katalog; samo pole ścieżki nie tworzy prywatnego katalogu ani praw FPM. Formularz zamknięto bez wypełniania/utworzenia konta.
- MySQL: panel pokazuje host `sql209.lh.pl`, **0 baz** i potrzebę ustawienia hasła konta głównego przed tworzeniem baz. Nie ustawiano hasła, nie tworzono DB/użytkownika. Wersja/silnik i dostęp konta aplikacyjnego nie są jeszcze potwierdzone. PDO MySQL było obecne w wcześniejszym odczycie PHP, ale nie wykonano połączenia do DB.
- „Bezpieczny PHP” pozostaje włączony; panel wymienia blokadę exec/system/proc_open i funkcji systemowych POSIX. Nie wymienia mkdir. Ta lista nie wyjaśnia automatycznie odmowy zapisu HOME. Nie zmieniono zabezpieczeń ani separacji.

## Wszystkie rozpatrzone drogi

| Opcja | Wniosek dla obecnego stagingu |
| --- | --- |
| Własny katalog w HOME poza `public_html` | Właściwy kierunek; jego samodzielne utworzenie przez FPM faktycznie odrzucone. Potrzebna interwencja ograniczona do dedykowanej ścieżki. |
| Katalog obok `www`, nadal pod `public_html` | Odrzucony jako magazyn sekretów/SQLite: domena techniczna może udostępniać nadrzędne `public_html`. Dot-prefiks i blokada `.htaccess` nie spełniają wymogu fizycznego umieszczenia poza wszystkimi webrootami. |
| Per-vhost env puli FPM | Technicznie możliwe w PHP-FPM; brak takiej funkcji w obejrzanym panelu LH. LH może ustawić **niesekretny wskaźnik** `PF_TEST_CONFIG` do prywatnego pliku; trzeba potwierdzić wsparcie oraz odczyt z procesu vhosta. Nie ujawniać pełnego środowiska przez sondę. |
| Prywatny plik dostarczony przez panel/operatora | Nie znaleziono funkcji w panelu. Możliwa usługa operatora, pod warunkiem wskazania ścieżki, praw i bezpiecznego kanału dostarczenia. Nie wysyłać sekretów w zwykłym zgłoszeniu supportowym. |
| `.user.ini` | Dokumentowana przez LH konfiguracja dyrektyw PHP w katalogu strony. **Nie jest menedżerem sekretów ani plikiem konfiguracji puli FPM**. Nie wstawiać tam kluczy, `env[...]` ani JSON sklepu. Opcjonalny niesekretny wskaźnik `auto_prepend_file` wymaga istniejącego prywatnego pliku i odrębnego testu, więc nie rozwiązuje braku katalogu. Nie wgrano `.user.ini`. |
| `SetEnv` / konfiguracja PHP w `.htaccess` | Sekret umieszczony w tym pliku nadal byłby zapisany w WWW; odrzucone. Sam niesekretny wskaźnik wymaga wcześniejszego utworzenia prywatnej ścieżki i potwierdzenia przekazania do FPM. |
| Katalog aplikacji całkowicie poza WWW | Może spełnić wymaganie, jeżeli LH nada FPM dostęp tylko do jego dedykowanej ścieżki. Istniejące konto FTPS nie ma tam dostępu. Nie zgadywano innych katalogów konta i nie użyto cudzych danych. |
| `sys_get_temp_dir()` / sesje / cache | Odrzucone jako trwały ledger SQLite i magazyn konfiguracji: niepotwierdzona trwałość, sprzątanie i izolacja. Nie utworzono tam bazy ani sekretów. |
| MySQL | Zastępuje **sam plik bazy**, po implementacji adaptera/transakcji i testach. Nie zastępuje bezpiecznej konfiguracji z hasłem DB, kluczem Stripe i webhook secret. Nie daje gotowości do uploadu. |
| Cron, SSH, większy pakiet, zewnętrzny secret store | Cron nie jest prywatnym magazynem i nie daje nowych praw FPM. SSH niedostępny w Orange; sam upgrade nie dowodzi usunięcia odmowy FPM. Zewnętrzny secret store nadal wymaga bezpiecznej tożsamości startowej. Nie zmieniono pakietu ani architektury usług. |

## Konkretne minimalne zlecenie dla LH

Docelowa ścieżka logiczna: **`<HOME>/.pf-private/pf-stage-20261114`**, poza `public_html`, bez publicznych aliasów/symlinków. Operator może wskazać równoważny dedykowany katalog, ale musi potwierdzić go dla vhosta 1711054 i wszystkich adresów technicznych. Nie należy nadawać aplikacji prawa zapisu całego HOME.

1. Utworzyć tylko ten katalog i ustalić rzeczywistą tożsamość procesu FPM stagingu. Nie zakładać, że właściciel FTP jest tym samym użytkownikiem systemowym.
2. `config/`: runtime ma odczyt pliku i przejście przez katalog, bez zapisu. Operator może dostarczać/rotować plik. Przykładowy model 0750/0640 z **dedykowaną** grupą albo ACL tylko tego FPM; nie nadawać odczytu wspólnej grupie wszystkich stron.
3. `data/`: FPM ma odczyt/zapis/przejście i tworzenie/usuwanie **wyłącznie tutaj**; SQLite potrzebuje też plików journal/WAL/SHM. Przykładowo właściciel FPM, 0700 katalog i 0600 pliki. Dokładne prawa zależą od potwierdzonego modelu izolacji LH.
4. Opcjonalne `sessions/` z dedykowanymi prawami zapisu, osobno od DB; retencja i sprzątanie tylko sesji, nie ledgeru. Plik hasła ochrony stagingu poza WWW musi mieć minimalny odczyt również właściwego serwera HTTP, jeśli jest to inny proces niż FPM.
5. Minimalne prawo przejścia przez rodziców i dopuszczenie tej ścieżki w mechanizmie separacji **tylko tego vhosta**, bez otwierania innych katalogów. Jeśli FPM używa współdzielonej tożsamości uniemożliwiającej separację, LH musi zaproponować izolowany wariant; nie udawać, że sam chmod zapewnia izolację.
6. Bezpieczny sposób dostarczania plików poza WWW: dedykowany ograniczony kanał/operator, bez użycia głównego FTP i bez kluczy w zgłoszeniu. Ustawić `PF_TEST_CONFIG` na prywatny JSON albo wskazać wspierany mechanizm bootstrapu. Obecny fallback aplikacji obok WWW nie wystarcza przy publicznym nadrzędnym `public_html`.
7. Potwierdzić backup i trwałość, zakres dostępu innych vhostów oraz brak zmian zasobów Pracowni Rachunkowości. Nie wyłączać separacji/open_basedir, nie stosować 0777, nie zmieniać globalnej konfiguracji.

Taki zakres doprecyzowano w otwartym **TKT-KTNHLTAY** o 13:00 czasu panelu; w chwili odczytu brak odpowiedzi LH. Osobno rozwiązano SSL — [wynik](LH_SSL_RESULT_20261114.md). Ten dokument zamyka wybór architektoniczny, lecz **nie potwierdza wykonania praw przez operatora**.

## Odbiór po wykonaniu przez LH

Najpierw krótkotrwała sonda ograniczona do stagingu, bez sekretów: odczyt nonsensytywnego pliku konfiguracji, zapis/odczyt/rename/usunięcie własnego pliku w `data`, brak zapisu do `config`, sprawdzenie realpath i braku publicznego mapowania. Potem sprawdzenie SQLite i sesji na sztucznych danych. Negatywny test od strony innej firmy jest **niedozwolony** — izolację między użytkownikami potwierdza LH, nie uruchamiamy kodu w innych vhostach. Dopiero po PASS i poprawnym HTTPS dostarczyć sekrety oraz aplikację.

MySQL pozostaje planem B opisanym w [zakresie adaptera](LH_MYSQL_ACTIONS_OPTIONS.md), nie sposobem pominięcia prywatnego runtime config.

Źródła: [LH: `.user.ini`](https://www.lh.pl/pomoc/doc/zmiany-w-ustawieniach-pliku-konfiguracyjnego-php/), [PHP: zakres `.user.ini`](https://www.php.net/manual/en/configuration.file.per-user.php), [PHP-FPM: konfiguracja puli](https://www.php.net/manual/en/install.fpm.configuration.php). Kontrole panelu są odczytem rzeczywistego konta; opisy producentów nie zastępują testu praw FPM na LH.
