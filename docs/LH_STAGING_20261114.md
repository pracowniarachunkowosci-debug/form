# LH staging — stan na 14 listopada 2026

**NO-GO do odbioru zakupowego na LH i do sprzedaży Live.** Skonfigurowano osobny vhost i DNS, lecz aplikacja nie została jeszcze wgrana. `https://test.pracowniaform.com` nie jest działającym sklepem: certyfikat nie odpowiada nazwie hosta, a FTPS odrzuca kanał danych. Poniższe PASS dotyczą środowiska lokalnego, chyba że jawnie wskazano inaczej.

## Wykonane zmiany

Praca na tej samej gałęzi PR #28: `codex/issue-27-winter26-photo-store`, od `910af9f`. Bez merge.

- `winter-26.css`: usunięty rzeczywisty overflow sekcji zestawów na 320/360 px. Na mobile etykiety zestawów są nad nagłówkiem; nie ściskają tytułu do pojedynczych liter. Reguły wyłącznie poniżej 600 px, desktop bez zmian.
- `api/_common.php`: porównywanie ścieżek prywatnej bazy uwzględnia separatory i wielkość liter Windows. Kontrola granicy katalogu pozostała ścisła; zachowanie POSIX niezmienione.
- `tests/checkout-live-gates.php`: regresje ścieżek (katalog, potomny, podobny prefiks, nadrzędny, inny dysk); przenośna ścieżka fixture SQLite.
- Zachowane fotografie, alt i kadry z `910af9f`, ceny, SKU, stany, dostępność, bramki zakupowe i nieaktywny kod rabatowy. Nie przypisano nowych zdjęć do wariantów. Nie rozwijano ponownie raportu fotograficznego.

## Rzeczywiste zasoby stagingu

| Zasób | Potwierdzony stan |
| --- | --- |
| LH | osobny serwer `serwer533947`, Orange, IP `195.2.223.12`, bez SSH |
| Nowy vhost | `test.pracowniaform.com`, ID `1711054` |
| Katalog WWW | `/public_html/pf-stage-20261114/www` |
| PHP vhosta | 8.5; separacja domeny włączona; Multipoczta wyłączona |
| Nowe konto FTPS | dostęp ograniczony do `/public_html/pf-stage-20261114`; hasło poza repozytorium |
| DNS OVH | dodano tylko `test A 195.2.223.12` i `test TXT "lh.pl"`, TTL 3600 |
| Weryfikacja DNS | autorytatywny `dns106.ovh.net` i resolver `1.1.1.1` zwracają powyższe wartości |
| Baza | **nie utworzona na LH**; potrzebna osobna SQLite poza wszystkimi katalogami WWW |
| Kopia przed uploadem | `STAT /www` potwierdził pusty nowy katalog (tylko `.` i `..`). Próba pobrania inwentaryzacji/kopii przez kanał danych nie powiodła się; nie deklarujemy wykonanej kopii plikowej. Nie wykonano uploadu. |
| HTTPS | **FAIL**: niedopasowana nazwa certyfikatu; początkowo panel zwracał 503, następnie błąd weryfikacji DNS mimo poprawnych publicznych rekordów |
| Ochrona dostępu/noindex | **NOT DEPLOYED**; aplikacja, Basic Auth i nagłówki stagingu nie zostały wgrane |

Nie zmieniono apex, `www`, MX, SPF, DKIM, DMARC ani nameserverów. Nie zmieniono istniejących witryn, baz, poczty, certyfikatów ani ustawień wspólnych Pracowni Rachunkowości. Na LH przed utworzeniem stagingu ten serwer pokazywał 0 stron i 0 baz MySQL; utworzono wyłącznie opisane nowe zasoby.

FTPS: certyfikat i logowanie AUTH TLS/PROT P przechodzą. LIST/MLSD/NLST kończą się `425 Unable to build data connection: Operation not permitted`. Błąd potwierdzony w Pythonie i curl/Schannel; próby ponownego użycia sesji TLS 1.2 również nie odblokowały kanału danych. HOST jest reklamowany w FEAT, ale `HOST serwer533947.lh.pl` został odrzucony jako nieznany host. Nie obniżano zabezpieczeń TLS ani separacji. Po zgodzie właściciela wysłano [zgłoszenie LH TKT-KTNHLTAY](https://www.lh.pl/panel/helpdesk/ticket/9235), utworzone 14.11.2026 o 00:39, status „W trakcie obsługi”. Dotyczy wyłącznie stagingu, bez sekretów i bez zgody na zmiany globalne. Odpowiedź techniczna jeszcze nie dotarła.

Techniczna domena LH udostępnia `public_html`, dlatego sam katalog obok `www` nie dowodzi prywatności. Przed uploadem sekretów LH musi potwierdzić prywatną ścieżkę i dostęp PHP przy zachowanej separacji. Nie użyto katalogu innej firmy ani wspólnej bazy.

## Testy lokalne

Lokalne PHP 8.4.27 NTS z curl/PDO SQLite/SQLite3, pobrane z oficjalnego wydania Windows; SHA-256 paczki zweryfikowany. Bez zmian systemowego PATH. LH PHP 8.5 nie został jeszcze uruchomiony na kodzie aplikacji.

| Kontrola | Wynik i granice |
| --- | --- |
| PHP lint | **PASS**, 14 plików |
| `tests/checkout-sandbox.php` | **PASS**, ceny, koszyk, rezerwacja SKU, niedobór/rollback, idempotencja, payload Stripe, podpis webhooka, kwota/tryb i cykl płatności; bez sieci |
| `tests/checkout-live-gates.php` | **PASS**, blokady niepełnych dokumentów, katalogu, zgód, niespójnych kluczy i zapasu; bez Stripe |
| `tests/checkout-locker.php` | **PASS**, stawki, próg łączny, aktywny punkt PL, błędy lookup, kanoniczny adres, zapis danych i idempotencja; bez InPost |
| Pricing Python | **PASS**, 4 testy |
| Render/EOL, rejestr konfiguracji, store gate, publikacja | **PASS**; 16 stron i 581 lokalnych referencji, formularz Brevo bez zmian |
| Cookies, konfigurator, kompozycja i składnia JS | **PASS**; zgody i zamknięty checkout zachowane |
| Handoff fotografii | **PASS**, 26 assetów/23 źródła; automatyczne przypisywanie nadal wyłączone |
| Fizyczne rastry | **PASS**, 85 plików przeszło weryfikację dekodera; nie tworzono fałszywych WebP/AVIF |
| UI | **PASS** lokalnie: wybór VASE/koloru, podsumowanie 1 szt. + kurier = 70,49 zł, odrzucenie nieaktywnego kodu |

Obowiązkowy cennik zweryfikowany lokalnie po stronie JS i PHP:

| Koszyk | Produkty | Kurier: razem | Paczkomat: razem |
| --- | ---: | ---: | ---: |
| 1 | 50,00 zł | 70,49 zł | 68,49 zł |
| 2 | 84,00 zł | 104,49 zł | 102,49 zł |
| 4 | 150,00 zł | 170,49 zł | 168,49 zł |
| 6 | 220,00 zł | 220,00 zł | 220,00 zł |
| 8 | 290,00 zł | 290,00 zł | 290,00 zł |
| 2 + 4 | 234,00 zł | 234,00 zł | 234,00 zł |

Nie wykonano powyższych płatności w Stripe. Koszyk 2 + 4 zachowuje ceny dwóch kompletów, ale próg darmowej dostawy liczy łącznie 6 sztuk.

## Mobile i desktop

Rzeczywisty pomiar w przeglądarce lokalnej, nie fizyczny telefon. Landing po poprawce, konfigurator i trzy karty produktów nie mają poziomego overflow na 320/360/390/430 px. W pomiarach mobile scrollbar zajmował 15 px: szerokości treści 305/345/375/415 px. `scrollWidth == clientWidth` we wszystkich czterech. Desktop 1440 px również bez overflow. Zawieszki i kontury zachowują wcześniej zaakceptowane kadry; nie zmieniano zdjęć.

- [Desktop — pełny landing](staging-20261114/landing-desktop.jpg)
- Mobile: [320](staging-20261114/landing-320.jpg), [360](staging-20261114/landing-360.jpg), [390](staging-20261114/landing-390.jpg), [430](staging-20261114/landing-430.jpg)
- [Konfigurator — wybór i podsumowanie](staging-20261114/configurator-mobile-selection.jpg)
- [Pomiary landingu](staging-20261114/landing-after.json), [konfiguratora](staging-20261114/mobile-measurements.json)

## Stripe i InPost — środowiska zewnętrzne

| Test rzeczywisty | Status |
| --- | --- |
| Stripe karta Sandbox | **NOT RUN** — brak wdrożonego backendu i poprawnego HTTPS |
| Stripe BLIK Sandbox | **NOT RUN** — dostępność metody i test niepotwierdzone |
| PLN / kwota koszyka w rzeczywistym Checkout | **NOT RUN** |
| Podpisany webhook z Stripe do LH | **NOT RUN** |
| `livemode=false` na konkretnej transakcji | **NOT RUN** — nie utworzono transakcji; widoczny panel „Pracownia Form sandbox” nie jest dowodem płatności |
| Opłacone zamówienie / pojedyncze odjęcie właściwego SKU na LH | **NOT RUN** |
| InPost mapa / wybór / zmiana punktu / przełączenie na kuriera | **NOT RUN na LH** |
| InPost rzeczywista walidacja kodu/adresu i zapis punktu | **NOT RUN** |

Sesja Stripe Sandbox jest zalogowana. Nie utworzono nowego klucza ani endpointu webhook; nie zapisano sekretu w repo. Właściciel zgłosił zalogowanie do InPost Sandbox, lecz ponowne wejście przez `sandbox-manager.paczkomaty.pl` i przycisk „Zaloguj przez Konto InPost” nadal kończy się formularzem na `stage-account.inpost-group.com`. Zalogowana karta `manager.paczkomaty.pl` jest produkcyjna, więc nie zastępuje testowej sesji. Otwarta właściwa karta wymaga dokończenia logowania: własny e-mail/telefon → „Akceptuj i kontynuuj” → uwierzytelnienie → powrót do `sandbox-manager.paczkomaty.pl`. Haseł, OTP i tokenów nie należy przesyłać w rozmowie. Wcześniej ujawnionego tokenu nie użyto. Nie utworzono przesyłek ani etykiet. Rozdział tokenów mapy testowej i produkcyjnej potwierdza [dokumentacja Geowidget InPost](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/pages/50069505).

## Dokumenty i dane blokujące Live

- Regulamin, dostawa/płatności, zwroty/reklamacje i formularz odstąpienia: historyczne źródła w PR #4, **brak kompletnych zatwierdzonych dokumentów sprzedaży w tym PR**.
- Polityka prywatności: istnieje; wymaga finalnego powiązania z rzeczywistą obsługą zamówień, odbiorcami danych i retencją. Nie jest potwierdzonym odbiorem prawnym.
- Cookies i zgody: lokalna suita przechodzi, marketing pozostaje odrębny od zakupu. Nie testowano wysłania formularza do Brevo ani doręczenia wiadomości; nie zapisano testowego adresu na produkcyjną listę.
- GPSR, materiał i wymiary w katalogu: niepotwierdzone; bramki sprzedaży pozostają zamknięte. Karty A6 nadal są proofem, nie plikami dopuszczonymi do druku.

Krótka lista potrzebnych danych właściciela (nie blokuje dalszej pracy technicznej):

1. Potwierdzenie sprzedawcy i czynnego kontaktu sklepu oraz rzeczywisty adres przyjmowania zwrotów/reklamacji.
2. Producent i jego kontakt, materiał/wymiary/identyfikacja trzech modeli oraz zatwierdzone informacje bezpieczeństwa wynikające z oceny produktu.
3. Realny czas realizacji od startu nadań 23.11.2026, treść/moment potwierdzenia umowy i zatwierdzenie kompletu dokumentów. Nie utożsamiać daty nadania z doręczeniem.

## Paczka i decyzja

Build z czystego commitu `da2f1c6badb4bd8384976f09150d5c2cd4ecaea4`: **PASS**.
124 pliki, ZIP 9 207 958 bajtów; SHA-256 `e9ba6e3a208a41ef8bee81782dff481aba77dc8b3a8ef3db288bfbc5010417b7`.
Paczka lokalna `.artifacts/lh-da2f1c6badb4/pracownia-form-lh.zip`, `uploaded_by_this_build=false`. Nie jest jeszcze skonfigurowanym stagingiem z uwierzytelnieniem.

**NO-GO:** najpierw LH musi umożliwić FTPS, poprawny certyfikat i jednoznacznie prywatny katalog SQLite/sekretów. Następnie potrzebny upload z ochroną dostępu/noindex, dane Sandbox i rzeczywiste testy Stripe/InPost na telefonie. Żaden lokalny PASS nie zastępuje tych prób. Bez produkcyjnego DNS, merge, Stripe Live i reklam.
