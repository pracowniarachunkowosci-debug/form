# PF / LH: nieaktywna propozycja Actions build + test + FTPS

**UNRUN / INACTIVE / DEPLOY BLOCKED — 14.11.2026.** Właściciel dopuścił przygotowanie propozycji, nie wykonanie Actions ani transferu. Plik pozostaje w `ops/github/lh-staging.workflow.yml.example`, poza `.github/workflows`. Nie utworzono workflow w GitHub, środowisk ani sekretów. W ramach tej propozycji nie wykonano Actions, połączenia FTPS ani zmian serwera. Osobno zatwierdzone DNS-01 i import SSL opisuje [raport SSL](LH_SSL_RESULT_20261114.md); nie odblokowują automatycznie wdrożenia ani tego workflow.

Punkt odniesienia: repo `pracowniarachunkowosci-debug/form`, gałąź `codex/issue-27-winter26-photo-store`, HEAD `a0a6cd5ce2c82edcab4c132baea878b4aabbcafe`, PR [#28](https://github.com/pracowniarachunkowosci-debug/form/pull/28). Git lokalnie odczytywany wyłącznie z jawnymi `--git-dir=C:/Users/lsolt/.codex/visualizations/2026/09/04/01a06d6a-faec-75d1-a6c5-9a6946b9c460/form-git --work-tree=C:/sklep/form`. Zapis ograniczony do `ops/github/` oraz tego dokumentu. Realizacja ACME i prywatnej ścieżki jest raportowana osobno; ta propozycja ich nie konfiguruje.

## Stan i zakres

To uszczegółowienie wariantów C/D z [LH_MYSQL_ACTIONS_OPTIONS.md](LH_MYSQL_ACTIONS_OPTIONS.md), z uwzględnieniem [diagnozy infrastruktury](LH_DNS01_PRIVATE_20261114.md) i [raportu stagingu](LH_STAGING_20261114.md). Brak nowego odbioru infrastruktury w tym zadaniu. Przygotowany kod nie stwierdza, że zewnętrzne blokady zostały rozwiązane.

| Element | Konkretne zachowanie |
| --- | --- |
| Szablon workflow | Tylko ręczny `workflow_dispatch`; wejścia: pełny SHA i `request_ftps=false`. Bez push/PR/schedule/workflow_run, hosta, ścieżki, nazwy repo, nazwy wydania czy dowolnego refa na wejściu. |
| Build | Osobna ręczna akceptacja; istniejący `scripts/build_release.py`, jego testy i nowy lokalny test zabezpieczeń; pełna historia Git dla `check_publication.py`. |
| Paczka | Oddzielny ZIP stagingowy, manifest i raport. Oryginalny build pozostaje niezmieniony. ZIP zawiera realny `.htaccess` jako pierwszy wpis i stagingowy `robots.txt`. |
| FTPS | Dwie bramki środowiskowe, dwa dosłowne `false` w YAML i niezależne `INFRASTRUCTURE_ACCEPTED = False` w Pythonie. Nie można ich zmienić inputem, sekretem ani zmienną repo. |
| Cel | Tylko `serwer533947.lh.pl:21`, login `serwer533947_pfstage14`, nowy katalog w jego jailu. Bez alternatywnego konta/celu produkcyjnego. |

Nie używać bezpośrednio `scripts/stage_lh.py --upload` w tym workflow. Odczytany skrypt sprawdza hashe i stosuje TLS, ale dopuszcza parametry hosta/katalogu, a przede wszystkim **nie dodaje ochrony dostępu ani noindex**. Odczytany `build_release.py` też nie pakuje automatycznie `ops/lh/preview.htaccess`. Sam nowy katalog pod `public_html` nie jest zabezpieczeniem.

## Zaufanie, SHA i przepływ artefaktu

Planowana, przyszła nazwa instalacji to `.github/workflows/lh-staging.yml` na chronionym `main` tego jednego repo. Samo skopiowanie pliku do tej ścieżki nie jest objęte obecną zgodą. W tej gałęzi propozycji nic nie uruchamia się automatycznie.

1. Job `request` nie pobiera ani nie wykonuje kodu repo. Sprawdza repo, zdarzenie, dokładny ref `refs/heads/main`, dokładną ścieżkę workflow oraz SHA: 40 małych znaków hex, równe `GITHUB_SHA` **i** `GITHUB_WORKFLOW_SHA`. Błędne wejście kończy run przed checkoutem. SHA nie może być tagiem, gałęzią, skrótem ani tekstem powłoki. Wartości wejściowe trafiają przez `env`, nie interpolację w `run`.
2. `build` czeka na `lh-staging-build-review`. Pobiera tylko potwierdzony SHA z repo PF, z `persist-credentials: false`, bez submodułów i LFS. Sprawdza HEAD i czystość drzewa przed/po buildzie. Nie akceptuje innego SHA z historii: kandydat musi być snapshotem tego ręcznie uruchomionego workflow. Po zmianie `main` należy wybrać aktualny zatwierdzony snapshot, nie poluzować walidację.
3. Python, Node i PHP pochodzą z obrazu `ubuntu-24.04`; preflight sprawdza ich obecność i `curl`/`pdo_sqlite` PHP. Brak zależności oznacza błąd, bez instalowania przypadkowych setup actions. Obraz runnera i wersje narzędzi są zmienne: to nie jest hermetycznie przypięty toolchain. Logi wersji wymagają przeglądu przy pierwszym przyszłym CI; lokalny PASS nie potwierdza PHP-FPM 8.5.12 na LH.
4. `build_release.py` wykonuje istniejące kontrole Python, składnię PHP/JS, testy checkout-sandbox/live-gates/locker oraz mock UI. Test live-gates jest lokalną regresją odmów, nie testem Stripe Live. Bez wywoływania `stripe-sandbox-probe.php`, testów z rzeczywistymi providerami, inicjalizacji bazy czy MySQL. Budowane PHP to obecny kod repo, ale workflow nie aktywuje trybu Live ani nie posiada danych produkcyjnych.
5. `lh_staging.py package` waliduje SHA, czystość źródła, raport, rozmiary, sumy, manifest i każdy wpis ZIP. Odrzuca traversal, duplikaty, symlinki/specjalne pliki, prywatne JSON/DB, `.env`, `.user.ini`, zagnieżdżone `.htaccess` oraz skrypty operatora. Stosuje listę dopuszczonych typów plików i limity ZIP. To kontrola struktury, nie skaner sekretów zaszytych np. w legalnym pliku PHP; przegląd zatwierdzonego commitu pozostaje wymagany.
6. Zmieniana jest tylko kopia stagingowa: `.htaccess` deny-all, `robots.txt` z `Disallow: /`, nowy manifest i raport z hashem źródłowego ZIP. Pominięte są również narzędzia CLI `api/prepare-live.php` i `api/seed-test.php`; weryfikator odrzuca ich obecność w paczce stagingowej. Oryginalne HTML/canonical oraz pliki produkcyjne repo pozostają niezmienione. Artefakt Actions zawiera tylko trzy jawne pliki: `pf-staging-denied.zip`, `manifest.json`, `release.json`; brak prywatnej konfiguracji, DB, haseł i narzędzi operatora.
7. Upload artefaktu ma `overwrite: false`, retencję 7 dni i nazwę SHA/run/attempt. Job FTPS pobiera **ID artefaktu z zależnego builda w tym samym runie**, bez wyboru repo/run/name przez użytkownika. `digest-mismatch: error` przerywa przy rozbieżności. Dodatkowo helper porównuje SHA256 ZIP, manifestu i raportu z trzema outputami builda, niezależnie od informacji wewnątrz paczki. Same hashe nie uwierzytelniają obcego artefaktu; zaufanie pochodzi z zatwierdzonego kodu i zależności jobów w tym runie.

Przypięcie akcji, ograniczenie tokena i przekazanie wejść przez środowisko odpowiadają [zaleceniom GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use). Job wdrożeniowy wykonuje helper z zatwierdzonego checkoutu, nigdy skrypt dostarczony wewnątrz artefaktu.

## Ochrona stagingu i nierozwiązana ekspozycja publiczna

LH dokumentuje, że domena techniczna wskazuje `public_html`, a podkatalogi mogą być przez nią osiągalne. Lokalny `.pf-private` obok `www` nie jest więc dowodem prywatności. Nie wolno modyfikować wspólnego `/public_html/.htaccess`, bo dotknęłoby to innych usług. [LH: domena techniczna i blokowanie katalogów](https://www.lh.pl/pomoc/doc/jak-zablokowac-dostep-do-katalogu-z-domeny-technicznej/).

`ops/github/staging-deny.htaccess` to rzeczywista polityka kwarantanny: `Require all denied`, brak listowania, `X-Robots-Tag: noindex, nofollow, noarchive`, `Cache-Control: private, no-store` i rozpoznawalna odpowiedź 403. Nie zawiera hasła, ścieżki do pliku haseł ani pozornej reguły przepuszczającej wszystko. Nie ma warunkowego `<IfModule>`, który po cichu pominąłby brak modułu. Wymaga Apache 2.4, właściwego AllowOverride oraz mod_headers. [Apache Require](https://httpd.apache.org/docs/2.4/mod/mod_authz_core.html#require), [Apache Header](https://httpd.apache.org/docs/2.4/mod/mod_headers.html#header).

**Obecność pliku w ZIP nie dowodzi działania ochrony na LH.** Ignorowanie `.htaccess` może ujawnić zawartość. Sam nagłówek `noindex` lub robots.txt nie ogranicza dostępu. Dlatego kod wdrożeniowy nadal ma twardą blokadę; lokalne testy nie mogą jej zdjąć. Kwarantanna odmawia także dostępu testerom i webhookowi: nie jest działającym podglądem sklepu. Umożliwienie uwierzytelnionego preview oraz wyjątku dla podpisanego POST webhooka wymaga oddzielnego projektu i odbioru; tego workflow nie ma operacji otwierającej dostęp.

Przed przyszłą zmianą blokad wymagane są wszystkie poniższe dowody, przejrzane przez właściciela i zapisane bez sekretów:

- HTTPS `test.pracowniaform.com`: poprawny SNI, nazwa i łańcuch certyfikatu, działanie PHP-FPM i sposób odnowienia. Poprawny certyfikat technicznego hosta lub FTPS nie wystarcza.
- Prywatna konfiguracja: rzeczywisty odczyt przez właściwy PHP-FPM przy zachowanej separacji i minimalnych prawach, prywatna lokalizacja poza **wszystkimi** publicznymi ścieżkami. Jeśli SQLite pozostaje, również właściwy prywatny katalog zapisu DB. Bez eksportu tych danych do Actions.
- Ekspozycja: inwentaryzacja hostów, aliasów, ścieżek technicznych i bezpośredniego routingu do stagingu; ochrona dedykowanego parenta przed transferem, potwierdzone dziedziczenie na nowy katalog i pliki. Sprawdzić HTTP/HTTPS, HTML, bezpośrednie zasoby, PHP, brak listowania i niedostępność plików prywatnych. Brak dowodu dowolnej ścieżki pozostawia NO-GO.
- Jail FTPS: operator potwierdza, że login `serwer533947_pfstage14` ma root `/` mapujący wyłącznie na `/public_html/pf-stage-20261114`. To założenie mapowania klienta, **nie nowy wynik pomiaru**. Sam `PWD /` nie dowodzi chroota ani braku symlinków do innych usług. Jeśli rzeczywista mapa jest inna, trzeba przejrzeć stałe w kodzie; nie dodawać dowolnego parametru `--base-dir`.
- Klient runnera: osobny odbiór explicit FTPS na wybranym runnerze, walidacja certyfikatu i kanału danych. Historyczne problemy Python/curl 425 nie są rozstrzygnięte przez działający WinSCP operatora. Nie wyłączać TLS jako obejścia.

## Dokładna propozycja transferu, nadal wyłączona

Po przyszłym odbiorze infrastruktury i zatwierdzonej zmianie kodu:

1. `infrastructure_review` czeka na środowisko `lh-staging-infrastructure-review`, a `ftps` niezależnie na `lh-staging`. Pierwsza bramka wymaga dowodów infrastruktury; druga przeglądu konkretnego SHA, runu, ID artefaktu, hashy, zakresu konta i nowego katalogu. Komunikat `echo` w pierwszym jobie niczego technicznie nie sprawdza — nie wolno uznać go za automatyczny odbiór.
2. Helper ponownie sprawdza kontekst repo/ref/workflow/SHA i hashe. Łączy się wyłącznie z ustalonym hostem explicit FTPS: weryfikowany kontekst TLS, `AUTH TLS`, stały login, `PROT P`, tryb pasywny. Hasło tylko z environment secret w tym jednym kroku. Bez jawnego FTP, wyłączania weryfikacji, parametrów URL czy komend powłoki. [Python FTP_TLS](https://docs.python.org/3/library/ftplib.html#ftplib.FTP_TLS).
3. Tworzy `winter26-<pełny-SHA>-<run_id>-<run_attempt>` w jailu. Kolizja przerywa bez użycia istniejącego katalogu. Docelowo to nowy podkatalog `/public_html/pf-stage-20261114/`, obok `www`; **nie jest podpięty pod `test.pracowniaform.com`**. Nie nadpisuje aktywnego `www` i nie przełącza vhosta. Re-run ma nowy attempt; starego katalogu nie usuwa.
4. Najpierw przesyła `.htaccess`, odczytuje go FTPS i porównuje hash; następnie nieszkodliwy `pf-access-check.txt`. Kontroluje ustaloną techniczną ścieżkę przez HTTP i HTTPS: dokładnie 403, spodziewana odpowiedź kwarantanny, noindex i no-store. Bez redirectów, dowolnych URL, proxy, Basic Auth i obchodzenia certyfikatów. Dopiero PASS dopuszcza aplikację. Ta sonda nie zastępuje wcześniejszego sprawdzenia wszystkich aliasów i konfiguracji parenta.
5. Każdy plik wysyła i odczytuje do porównania SHA256. Po payloadzie ponawia sondę blokady. Błąd przerywa; częściowy katalog z blokadą i sondą pozostaje do ręcznej oceny. Nie ma kasowania, synchronizacji z delete, rename, chmod/SITE, zdalnego unzip/CLI, inicjalizacji DB ani automatycznego ponowienia po częściowym błędzie.

Sonda HTTP w tym projekcie jest wyłącznie kodem przyszłego transferu i atrapą w testach. W ramach testów tej propozycji nie kontaktowano się z LH. Nawet przyszły udany transfer oznacza tylko zweryfikowaną kwarantannę, bez aktywacji strony i bez potwierdzenia działania zakupów.

## Zgody, minimalne sekrety i permissions

Wymagane środowiska należy utworzyć **przed** ewentualną aktywacją. Sama nazwa `environment:` nie tworzy reguł akceptacji; nieistniejące środowisko może zostać automatycznie utworzone bez ochrony. Dla każdego: required reviewers, zakaz self-review, wyłączony admin bypass i dopuszczony wyłącznie branch `main`. Lista wielu reviewerów oznacza zwykle zgodę jednego z nich, nie wszystkich. Trzy joby dają osobne punkty akceptacji, nie wymuszają trzech różnych osób. Chronić zmiany workflow/helperów i gałąź `main` przeglądem kodu. Dostępność wymaganych reguł zależy od planu i widoczności repo; nie została tutaj zweryfikowana. Jeśli nie można ich wymusić, FTPS pozostaje wyłączony. [GitHub: zarządzanie środowiskami](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

| Zasób | Minimum |
| --- | --- |
| Global / request / infrastructure_review | `permissions: {}`; żadnych sekretów. |
| Build | `contents: read` dla checkoutu; zero sekretów dostawców. Artefakt przez mechanizm runu Actions. |
| FTPS job | `contents: read` dla zaufanego helpera; pobranie po ID z tego samego runu bez osobnego PAT ani `actions: read`. |
| Environment `lh-staging` | Jedyny wymagany sekret: `PF_FTPS_PASSWORD` dla dedykowanego loginu `serwer533947_pfstage14`. Login, host i root są stałymi kodu, nie danymi wejściowymi. |
| Pozostałe środowiska | Brak sekretów. Akceptacja infrastruktury nie wymaga haseł hostingu w Actions. |

Nie potrzeba `contents: write`, `actions: write`, `deployments: write`, `pages: write`, `id-token: write`, PAT, sekretów DNS/OVH/ACME, kluczy TLS, DB, Stripe ani dostępu produkcyjnego. Workflow nie wywołuje Deployment API. Nie dodawać dodatkowych sekretów na poziomie repo/organizacji „na zapas”. Logi wyjątków transportu są ogólne; nie drukują odpowiedzi dostawcy, haseł ani argumentów. Hash paczki nie jest sekretem. Retencja artefaktów podlega także polityce repo; automatyczne wygaśnięcie artefaktu nie kasuje niczego na LH.

## Przypięte akcje — weryfikacja odczytem 14.11.2026

Odczytano `releases/latest`, `git/ref/tags/<wersja>` i `commits/<SHA>` w oficjalnych repozytoriach GitHub. Każdy tag wskazywał bezpośrednio commit, a API zwróciło `verification.verified=true`. Odczytano także kontrakt wejść `action.yml` upload/download pod tymi SHA. Bez uruchamiania akcji.

| Oficjalna akcja / aktualny release w chwili odczytu | Pełny SHA |
| --- | --- |
| [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) | [`3d3c42e5aac5ba805825da76410c181273ba90b1`](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1) |
| [upload-artifact v7.0.2](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) | [`cf430e030ddbb5b0abf93d22962f4752f3646cd9`](https://github.com/actions/upload-artifact/commit/cf430e030ddbb5b0abf93d22962f4752f3646cd9) |
| [download-artifact v8.0.2](https://github.com/actions/download-artifact/releases/tag/v8.0.2) | [`9000827ccba6bdab643e8b6fd33ac0654aef8333`](https://github.com/actions/download-artifact/commit/9000827ccba6bdab643e8b6fd33ac0654aef8333) |

Źródłowy [kontrakt download-artifact](https://github.com/actions/download-artifact/blob/9000827ccba6bdab643e8b6fd33ac0654aef8333/action.yml) potwierdza `artifact-ids`, bieżący run bez dodatkowego tokena oraz `digest-mismatch: error`. [Kontrakt upload-artifact](https://github.com/actions/upload-artifact/blob/cf430e030ddbb5b0abf93d22962f4752f3646cd9/action.yml) potwierdza ID/digest output, retencję i `overwrite`. Wersje wymagają obsługi Node 24 przez runnera. Przed przyszłą aktywacją ponowić odczyt advisory/wydań i zatwierdzić ewentualną zmianę pinów w kodzie, bez pływających tagów.

## Walidacja lokalna i granice wyniku

- **PASS, 14 testów:** `python -B ops/github/test_lh_staging.py`. Testy offline syntetycznych paczek, walidacji SHA/ref/repo, hashy, niedozwolonych ścieżek, linków, limitów, pominięcia narzędzi CLI, kolejności ochrony, kolizji, readback, odrzucenia publicznej odpowiedzi i twardej blokady przed odczytem sekretów/transportem. Wszystkie zapisy tymczasowe testów pozostają pod `ops/github/`; testy blokują rzeczywiste połączenia socket.
- **PASS:** `actionlint 1.7.12 -no-color -shellcheck= -pyflakes= ops/github/lh-staging.workflow.yml.example` — lokalne sprawdzenie YAML, składni i wyrażeń Actions. ShellCheck i Pyflakes nie były dostępne, więc ich integracje wyłączono; Python sprawdzono przez lokalne testy. Oficjalne [wydanie actionlint](https://github.com/rhysd/actionlint/releases/tag/v1.7.12), pobrany ZIP Windows amd64 zweryfikowany SHA256 `6e7241b51e6817ea6a047693d8e6fed13b31819c9a0dd6c5a726e1592d22f6e9`; tymczasowe narzędzie usunięte po walidacji.
- **PASS lokalny build** po commicie `6ea1559be02bb1a090c3c70f6af3a03d562eb7ca`: 125 plików, wszystkie istniejące suity builda. Pierwsza próba w sandboxie nie miała dostępu PHP do JSON cennika; po zatwierdzonym uruchomieniu z dostępem do workspace odczyt i cały build przeszły bez zmian aplikacji. Następnie `package` i `verify` na rzeczywistej paczce dały **PASS lokalnej integralności** (124 pliki, deny-all, bez dwóch narzędzi CLI). [Raport builda](staging-20261114/build-6ea1559.json), [raport paczki](staging-20261114/quarantine-6ea1559.json). Workflow na runnerze pozostaje **UNRUN**, FTPS twardo zablokowany.
- Nie wykonano testu Apache/AllowOverride na LH, HTTPS stagingu, prywatnego FPM ani klienta FTPS runnera. Test atrapy nie jest odbiorem infrastruktury. Brak podstaw do odblokowania jobów.

Do przeglądu pozostaje nieaktywna propozycja. Ewentualna późniejsza zgoda na CI/build nie oznacza zgody na FTPS; przy otwartych blokadach wolno aktywować najwyżej osobno zatwierdzony build, zachowując wszystkie blokady wdrożenia. Zmiana `false`/stałej wymaga osobnej, konkretnej decyzji po odbiorze dowodów; żaden input workflow jej nie zastępuje.
