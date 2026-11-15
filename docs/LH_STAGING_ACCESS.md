# Ochrona test.pracowniaform.com przed uploadem aplikacji

Zakres: **tylko vhost 1711054**, WWW `/public_html/pf-stage-20261114/www`, konto `serwer533947_pfstage14`. To przygotowane narzędzia, **nie potwierdzenie wdrożenia lub testu LH**. Nie aktywują GitHub Actions ani zakupów.

## Warunek użycia

Najpierw LH wskazuje prywatny katalog poza wszystkimi webrootami i potwierdza izolację oraz kanał dostarczenia konfiguracji. [Sonda runtime](LH_RUNTIME_PROBE.md) musi przejść na rzeczywistym FPM, a operator osobno potwierdzić brak publicznych aliasów. Prywatny plik Basic Auth musi być dostępny do odczytu właściwemu serwerowi HTTP; to nie musi być ten sam proces co FPM. Nie umieszczać hasła, jego pliku ani konfiguracji Stripe w WWW lub repozytorium.

## Przygotowany szablon

[`ops/lh/staging.htaccess.in`](../ops/lh/staging.htaccess.in) wymaga zastąpienia **wyłącznie** `@PRIVATE_AUTH_FILE@` potwierdzoną bezwzględną ścieżką do prywatnego pliku. Nie kopiować nierenderowanego pliku na serwer. Nie stosować go do domeny głównej ani innego vhosta. Nie nadpisywać istniejącego `.htaccess`: przed uploadem świeża inwentaryzacja i kopia wszystkich istniejących plików.

- HTTPS; Basic Auth dla strony, assetów i API. `noindex` oraz `private, no-store`.
- Dokładny host `test.pracowniaform.com`; domena techniczna jest odrzucana.
- Wyjątek od Basic Auth wyłącznie dla dokładnego `POST /api/webhook.php`, bez query, PATH_INFO i alternatywnego zakodowania ścieżki. Nie otwiera całego `/api`.
- `api/webhook.php` pozostaje niezmieniony: wymagany podpis Stripe, weryfikowany przed otwarciem SQLite i zastosowaniem zdarzenia.
- Dotfiles, wewnętrzne include i CLI `seed-test.php`/`prepare-live.php` zablokowane także po podaniu hasła.
- Bez `IfModule` pomijającego ochronę: brak wymaganej funkcji Apache ma zatrzymać odbiór, a nie udostępnić pliki.

Szablon korzysta z [kontenerów autoryzacji Apache](https://httpd.apache.org/docs/2.4/mod/mod_authz_core.html#require) i [zmiennych wyrażeń Apache](https://httpd.apache.org/docs/2.4/expr.html#vars). Nie potwierdzono jeszcze jego obsługi w konfiguracji LH. Lokalnie nie ma działającego Apache; testy weryfikatora HTTP nie zastępują testu tych reguł na serwerze.

## Odbiór na LH

1. Wgrać samą wyrenderowaną ochronę i własny niesensytywny plik kontrolny. Sprawdzić anonimowy HTTPS, poprawne/błędne hasło, HTTP i techniczny adres **wyłącznie pod ścieżką tego stagingu**. Publiczny plik lub błąd konfiguracji oznacza STOP. Usunąć tylko własny plik kontrolny.
2. Dopiero po PASS wgrać świeży, zweryfikowany build dokładnego SHA `9cb6100e6368c125e9fc6cbde6958496838c490d` zgodnie z komentarzem właściciela. Osobny seed Sandbox; żadnego ledgeru Live, rzeczywistych zamówień ani zmian stanów handlowych.
3. Uruchomić [`scripts/check_lh_staging_access.py`](../scripts/check_lh_staging_access.py). Wskazać istniejący asset z manifestu i lokalny plik raportu. Dedykowane dane Basic Auth podać przez prywatne środowisko `PF_STAGING_HTTP_USER` / `PF_STAGING_HTTP_PASSWORD`, nigdy w argumentach komendy. Narzędzie nie loguje danych logowania ani treści odpowiedzi, nie śledzi przekierowań, nie wysyła hasła przez HTTP lub do hosta technicznego i zachowuje weryfikację TLS.

```powershell
python scripts/check_lh_staging_access.py --asset /assets/PLIK_Z_MANIFESTU.webp --report .artifacts/lh-staging-access.json
```

Weryfikator sprawdza 21 przypadków. Anonimowe `POST` bez podpisu ma dojść do PHP i zwrócić **400 / SIGNATURE**, nie 200, 401 ani 503. To dowód poprawnego wyjątku i odrzucenia niepodpisanego zdarzenia, **nie dowód dostarczenia podpisanego webhooka Stripe**. Rzeczywiste testy Sandbox karta/BLIK, powtórne zdarzenie, wygasła sesja, stan zamówienia i SKU należy wykonać osobno. Dane testera i payloady pozostają prywatne.

HTTP może zwrócić 403 albo przekierować dokładnie do `https://test.pracowniaform.com/`; przekierowanie nie jest śledzone, a HTTPS jest sprawdzany niezależnie. Dostęp przez host techniczny musi być odrzucony. Inne przekierowania zatrzymują odbiór.

## Test lokalny narzędzia

`python tests/lh-staging-access.py`: **7/7 PASS**, bez sieci. Sprawdza ograniczenie odbiorcy danych logowania, brak śledzenia przekierowań, rozpoznanie błędu podpisu, odrzucenie publicznych assetów, redakcję błędów transportu, odrzucenie ścieżek spoza manifestu oraz regresję zbyt szerokiego wyjątku POST w API. Wynik nie oznacza PASS Apache, FPM, LH, Stripe ani telefonu.
