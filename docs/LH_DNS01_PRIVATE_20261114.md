# LH: DNS-01 i prywatna konfiguracja — wynik 14.11.2026

Zakres: PR #28 / Issue #24, wyłącznie `test.pracowniaform.com`, vhost `1711054`, serwer `serwer533947`, dedykowane WWW `/public_html/pf-stage-20261114/www`. Kontynuacja [polecenia właściciela](https://github.com/pracowniarachunkowosci-debug/form/pull/28#issuecomment-6875900114).

**Aktualizacja po osobnych zgodach właściciela: DNS-01 zakończone, certyfikat wydany, zweryfikowany i zainstalowany. HTTPS infrastruktury PASS.** Testowy TXT posprzątano, 16 wcześniejszych rekordów pozostało identycznych. Prywatna konfiguracja nadal blokuje upload. [Aktualny raport SSL](LH_SSL_RESULT_20261114.md), [decyzja architektoniczna](LH_PRIVATE_CONFIG_DECISION.md), [nieaktywna propozycja Actions](LH_ACTIONS_PROPOSAL.md).

**Poniżej zachowany zapis wcześniejszej diagnostyki, przed zgodami na DNS/import.** Stwierdzenia „nie wydano”, „bez zmian DNS” i „HTTPS FAIL” opisują tamten etap; bieżący stan określa raport powyżej. Nie powtarzano HTTP-01 ani sond PHP podczas importu SSL.

## Rzeczywiste pomiary

| Kontrola | Wynik |
| --- | --- |
| FTPS w istniejącej sesji WinSCP | **PASS**: listing, upload i usunięcie własnych sond; wcześniejszy błąd 425 nie jest bieżącą blokadą tej sesji |
| HTTP `/` | 403 przy pustym WWW; nie oznacza blokady portu 80 |
| Zwykły plik / plik bezpośrednio w `.well-known` | 200 i oczekiwana treść; właściwy DocumentRoot potwierdzony przez PHP |
| HTTP `/.well-known/acme-challenge/probe.txt` | **404 mimo obecności pliku**; identycznie przez DNS i z przypięciem IP LH; bez przekierowań |
| HTTPS | **FAIL**: curl/Schannel `SEC_E_WRONG_PRINCIPAL`, także z przypięciem IP |
| PHP | **8.5.12, fpm-fcgi**, PDO SQLite i cURL dostępne; dotyczy sondy, nie testu aplikacji |
| Własny katalog/plik w WWW | **PASS**: utworzenie, zapis, odczyt, usunięcie |
| Katalog `.pf-private` poza `public_html` | **FAIL: Permission denied z PHP-FPM** |
| Losowy katalog obok `public_html` | Taka sama odmowa; wynik nie zależy wyłącznie od nazwy `.pf-private` |
| Sprzątanie | **PASS**: WWW pusty; usunięte adresy sond zwracają 404; brak bazy, aplikacji i sekretów runtime |

[Dowód HTTP-01: statusy, nagłówki, treść i cleanup](staging-20261114/http01-evidence.json). Odpowiedź challenge: Apache, `404 Not Found`, `Content-Type: text/html; charset=iso-8859-1`, 236 bajtów, komunikat „The requested URL was not found on this server.”. Prawa utworzonych katalogów 0755, pliku 0644. Nie zmieniano `.htaccess` ani zabezpieczeń. Oddzielny alias/webroot ACME jest hipotezą wymagającą logów LH, nie potwierdzoną przyczyną. Warunek ponowienia zarządzanego instalatora po udanym HTTP-01 nie został spełniony.

Lokalne OpenSSL widzi SAN `*.lh.pl, lh.pl`, bez nazwy stagingu; wystawca Norton Web/Mail Shield wskazuje na inspekcję TLS na komputerze. Nie przypisujemy dat tego przedstawionego certyfikatu certyfikatowi origin LH. Nie wyłączano inspekcji ani walidacji TLS. Ostateczna kontrola po instalacji musi obejmować także połączenie bez tej lokalnej inspekcji, z poprawną walidacją zaufania i nazwy.

## DNS — bez zmian

Odczyty z `1.1.1.1`, `8.8.8.8`, autorytatywnych `dns106.ovh.net` (5.196.41.1) i `ns106.ovh.net` (5.135.65.21) są zgodne:

| Nazwa / typ | Odpowiedź |
| --- | --- |
| `test.pracowniaform.com` A | `195.2.223.12`, TTL 3600 |
| `test.pracowniaform.com` TXT | `lh.pl`, TTL 3600 |
| `test.pracowniaform.com` AAAA | NOERROR / NODATA |
| `test.pracowniaform.com` CAA | NOERROR / NODATA |
| `pracowniaform.com` CAA | NOERROR / NODATA; poprawna nazwa, bez wcześniejszej literówki |
| `www.test.pracowniaform.com` A | NXDOMAIN |
| `_acme-challenge.test.pracowniaform.com` TXT | NXDOMAIN przed proponowaną zmianą; odpowiedzi autorytatywne z AA=true |

[Publiczne wyniki zapytań](staging-20261114/dns-readonly-evidence.json). Nie ma dowodu na błędny A, konflikt AAAA ani zakaz CAA. Brak `www.test` może mieć znaczenie dla walidatora zarządzanego instalatora LH, którego instrukcja wymaga obu nazw. Nie jest wymogiem ACME dla certyfikatu z jednym SAN. Nie dodano aliasu ani rekordu `www`.

## Konkretnie przygotowany DNS-01

- Oficjalne wydanie win-acme v2.4.1, binary simple-acme/WACS **2.4.1.2444 x64 pluggable**. SHA-256 ZIP zweryfikowany z metadanymi wydania: `2faa095ea5264191a219b6935d56e59e2ef6153ab651d919e009ecfe72371630`.
- ACME `https://acme-v02.api.letsencrypt.org/`, jawny profil `classic`, walidacja certyfikatu serwera włączona. Zgoda właściciela obejmuje rejestrację z `kontakt@pracowniaform.com` i ToS v1.8 z 06.07.2026.
- Źródło manual, **jedyny host `test.pracowniaform.com`**, metoda manual DNS-01, export PEM, installation none, `--notaskscheduler`. Bez tokenów OVH i bez konfiguracji Actions.
- Konto utworzone, order/challenge uzyskany; klient zatrzymany na prośbie o potwierdzenie utworzenia rekordu. **Nie wywołano walidacji**, nie dodano TXT. Klucze/config/logi/cache znajdują się poza repo, w katalogu z ACL ograniczonym do bieżącego operatora Windows i SYSTEM. W repo jest tylko szablon sondy bez tokenu i ścieżki konta.

Zmiana do osobnej akceptacji: **jeden nowy TXT**, strefa `pracowniaform.com`, nazwa względna `_acme-challenge.test`, FQDN `_acme-challenge.test.pracowniaform.com`, rekomendowany TTL 300, wartość z bieżącego wyzwania przekazana w rozmowie. To nie jest zamiana istniejącego `test TXT lh.pl`. Przed zapisem ponownie odczytać RRset; jeśli pojawią się cudze wartości, zachować je. W razie wygaśnięcia zamówienia wygenerować i przedstawić nową wartość zamiast używać starej.

Po akceptacji TXT: dodać dokładnie tę wartość, sprawdzić obie autorytatywne odpowiedzi i publiczne resolvery, dopiero wtedy kontynuować klienta. Po pozytywnej autoryzacji i pobraniu certyfikatu usunąć **wyłącznie dodaną wartość**, zachowując pozostałe rekordy. Jeśli klient poprosi o cleanup, sprawdzić wynik autoryzacji przed potwierdzeniem. Nie tworzyć delegacji NS/CNAME ani konta API OVH.

## Import do LH — procedura gotowa, zapis jeszcze niewykonany

W panelu **tego vhosta** otwarto SSL → „Własny”; formularz udostępnia trzy obowiązkowe pola. [Zrzut formularza](staging-20261114/lh-custom-ssl-form.jpg). Anulowano bez zapisu.

| Pole LH | Plik PEM z klienta |
| --- | --- |
| Certyfikat | `*-crt.pem` — sam certyfikat serwera (leaf) |
| Klucz prywatny | `*-key.pem` — odpowiadający mu klucz |
| Klucze CA (pośrednie) | `*-chain-only.pem` — certyfikaty pośrednie, bez ponownego leaf |

`*-chain.pem` zawiera leaf + chain i nie jest zamiennikiem chain-only w trzecim polu. Format jest zgodny z opisem pól LH; **serwerowego przyjęcia zewnętrznego LE z jednym SAN nie testowano**. LH poproszono o potwierdzenie tego wariantu i braku wymogu `www.test`. Nie przenosimy ogólnego wymogu `www` z instrukcji zarządzanego LE na import własnego certyfikatu bez potwierdzenia.

Po wydaniu: sprawdzić SAN (dokładnie staging), issuer, notBefore/notAfter, łańcuch i zgodność klucza publicznego wyprowadzonego z klucza prywatnego z certyfikatem. Nie drukować klucza prywatnego w logach. Po **osobnej akceptacji instalacji** ponownie potwierdzić ID 1711054, wkleić trzy PEM w jego formularzu i zapisać. Żadnego globalnego certyfikatu konta ani podmiany certyfikatów innych witryn. Następnie zweryfikować HTTPS z SNI i walidacją hosta/łańcucha, SAN, daty i fingerprint; sam kod 403 pustego WWW nie jest błędem TLS.

## Odnowienie: odpowiedzialność operatora, nie automatyczna obietnica

Profil LE `classic` obecnie daje certyfikaty 90-dniowe. To limit certyfikatu, nie gwarancja dostępności tego samego challenge. Wiążące są daty otrzymanego certyfikatu. **Manual DNS-01 wymaga operatora przy odnowieniu; import „Własny” nie oznacza automatycznego odnowienia/reinstalacji przez LH.** Nie utworzono harmonogramu ani automatyzacji.

Wykonalny proces: wskazany operator sprawdza termin co tydzień; rozpoczyna odnowienie najpóźniej 30 dni przed notAfter (około 55–60 dnia od wydania). Używa tego samego prywatnego konta ACME i zatwierdzonej konfiguracji, uzyskuje nowe wyzwanie tylko stagingu, dodaje jego TXT po wymaganej akceptacji, waliduje, pobiera i sprawdza nowy zestaw PEM. Ponownie importuje **nowy leaf, odpowiadający klucz i chain**, kontroluje certyfikat podawany przez vhost, usuwa tylko nowy TXT. Stary zestaw zachowuje prywatnie do potwierdzenia działania nowego; nie usuwa działającego SSL przed wymianą. Brak skutecznego odnowienia eskaluje do LH 14 dni przed wygaśnięciem, ponownie 7 dni przed; nie czeka na awarię HTTPS.

Rekomendacja: manual DNS-01 jako kontrolowane uruchomienie stagingu, równolegle naprawa obsługi ACME przez LH. Zarządzany certyfikat po naprawie może ograniczyć pracę operatora, lecz jego rzeczywiste odnowienie i routing muszą zostać potwierdzone. Nie wybrano płatnego certyfikatu ani automatyzacji z szerokim dostępem do strefy OVH.

## PHP-FPM i prywatne miejsce na konfigurację

Nowa [sonda jako szablon](../scripts/lh_private_probe.php.in) wymagała właściwego Host, POST, krótkotrwałego losowego tokenu w nagłówku, zgodności SHA-256 i czasu ważności. Token nie był częścią URL ani repo. Bez tokenu GET/POST i z błędnym tokenem: **404**, bez informacji diagnostycznych. Autoryzowany test: **200**, wyłącznie booleany/statusy; bez phpinfo, pełnych ścieżek, UID, haseł i zmiennych środowiskowych. Ponieważ HTTPS nie działa, użyto HTTP wyłącznie dla krótkotrwałej sondy bez sekretów aplikacji; skrypt już usunięto.

`HOME` i jego `realpath` są zgodne z katalogiem konta opisanym przez LH, a `DOCUMENT_ROOT` ze stagingiem. Odpowiedź nie ujawnia pełnej ścieżki. `open_basedir` jest pusty; separacja w panelu pozostaje włączona. Faktyczne mkdir poza `public_html` daje `Permission denied`, mimo `is_writable(HOME)=true`. To wynik procesu **PHP-FPM**, niezależny od ograniczenia FTPS do podkatalogu. Dokładnej przyczyny systemowej (ACL/izolacja/inne ograniczenia) nie da się wskazać bez danych LH. [Zanonimizowany wynik i cleanup](staging-20261114/php-fpm-private-anonymized.json).

W ustawieniach tego vhosta nie znaleziono pola per-vhost env/private config. Nie oznacza to dowodu braku takiej funkcji u operatora. **Wysłano uzupełnienie TKT-KTNHLTAY o 11:39 czasu panelu**, z prośbą o utworzenie dedykowanego prywatnego katalogu poza wszystkimi webrootami, minimalne prawa jego PHP-FPM i bezpieczny sposób dostarczenia konfiguracji przy ograniczonym FTPS/braku SSH. Zapytano też o env/private config path. [Treść wysłanej odpowiedzi](staging-20261114/lh-followup-20261114.txt), [potwierdzenie w panelu](staging-20261114/lh-followup-sent.jpg). Zgłoszenie pozostaje otwarte. Wykluczono chmod 777, wyłączenie izolacji, zmiany globalne i zasoby Pracowni Rachunkowości.

## MySQL, Actions i następny upload

[Konkretne opcje adaptera MySQL, schematu, transakcji, testów i minimalnych uprawnień Actions](LH_MYSQL_ACTIONS_OPTIONS.md). MySQL wymaga m.in. blokad rezerwacji/webhooków i zachowania idempotencji; nie rozwiązuje przechowania sekretów ani HTTPS. Nie utworzono bazy/migracji. Rekomendowany pierwszy zakres automatyzacji to CI/build bez sekretów dostawców i ręczny transfer WinSCP. Nie zmieniano ani nie uruchamiano workflow DNS/FTPS; GitHub nie otrzymał dostępu do LH/OVH ani sekretów runtime.

Po rozwiązaniu **obu** blokad: ponowna weryfikacja dedykowanych zasobów i ich kopia/inwentaryzacja; prywatna konfiguracja i testowa baza; ochrona dostępu/noindex z wyjątkiem podpisanego POST webhooka; aktualny build konkretnego SHA; transfer i porównanie hashy wyłącznie stagingu; odbiór PHP, Stripe Sandbox karta/BLIK, webhook, idempotencja, stan właściwego SKU, dostawy i fizyczny telefon. Do czasu odblokowania InPost można stosować jawny MOCK; nie nazywać go testem InPost. Bez automatycznego przejścia do produkcji.

## Źródła i granice weryfikacji

- [LH: własny certyfikat i trzy pola PEM](https://www.lh.pl/pomoc/docs/jak-przeniesc-certyfikat-ssl-na-nowy-serwer-w-lh-pl/), [ścieżka konta](https://www.lh.pl/pomoc/doc/sciezka-do-konta-od-strony-serwera/), [zarządzany Let's Encrypt](https://www.lh.pl/pomoc/doc/jak-uruchomic-certyfikat-ssl-lets-encrypt-na-serwerze-w-lh-pl/).
- [LE: DNS-01](https://letsencrypt.org/docs/challenge-types/), [profile certyfikatów](https://letsencrypt.org/docs/profiles/), [zatwierdzone warunki](https://letsencrypt.org/documents/LE-SA-v1.8-July-06-2026.pdf).
- [Oficjalne wydanie klienta v2.4.1](https://github.com/win-acme/win-acme/releases/tag/v2.4.1), [format eksportu PEM](https://www.win-acme.com/reference/plugins/store/pemfiles). Flagi sprawdzono również w pomocy pobranego binary; strony starszego klienta nie zastępują rzeczywistego `--help`.

W tym etapie zmieniono dokumentację i dodano szablon diagnostyczny, nie kod sklepu. Lint wygenerowanej sondy oraz rzeczywiste kontrole autoryzacji, PHP i cleanup przeszły w opisanym zakresie. Dodatkowo **6 lokalnych przypadków CLI** sprawdziło brak/błędny token, GET, niewłaściwy Host, wygaśnięcie i zatrzymanie poza FPM; [wynik](staging-20261114/probe-local-check.json). Próba dodatkowego HTTP na loopback została zablokowana przez sandbox i nie jest zaliczona jako PASS. Pełny wcześniejszy build/testy sklepu pozostają historycznymi wynikami wskazanych commitów; nie są dowodem odbioru LH. **NO-GO zakupów na LH i Live** do zamknięcia infrastruktury oraz osobnych bramek aplikacyjnych/prawnych.
