# LH staging — stan na 14 listopada 2026

**NO-GO do odbioru zakupowego na LH i do sprzedaży Live.** `https://test.pracowniaform.com` nie jest jeszcze działającym sklepem. **Aktualizacja 14.11 po imporcie:** FTPS, PHP 8.5.12 i HTTPS infrastruktury działają. Za osobnymi zgodami wykonano DNS-01, wydano i zainstalowano LE tylko dla stagingu, po czym usunięto własny TXT. Niezależny odczyt potwierdził nazwę, łańcuch i numer seryjny. Pozostała odmowa prywatnego katalogu PHP-FPM. LH otrzymało aktualizację o 13:00 czasu panelu. [Wyniki SSL](LH_SSL_RESULT_20261114.md), [prywatny runtime](LH_PRIVATE_CONFIG_DECISION.md).

Rzeczywiste płatności kartą i BLIK w Stripe Sandbox przeszły wcześniej z lokalnym PHP oraz podpisanymi webhookami przez Stripe CLI. **Nie są testem aplikacji na hostingu LH.** Na LH uruchomiono wyłącznie tymczasowe sondy infrastruktury, już usunięte; WWW pusty, bez aplikacji, bazy i sekretów runtime.

## Wynik bieżącego etapu

| Obszar | Status i zakres dowodu |
|---|---|
| Staging LH | **BLOCKED** — prywatny katalog/config PHP-FPM; `TKT-KTNHLTAY` uzupełnione, nadal otwarte; bez uploadu aplikacji |
| FTPS | **PASS WinSCP** — listing, upload i usunięcie własnych sond; historyczne 425 nie blokuje tej sesji |
| HTTPS | **PASS infrastruktury** — LE z SAN stagingu, zaufany łańcuch i zgodny serial w zewnętrznym teście; 403 pustego WWW. Norton ogranicza lokalny pomiar fingerprintu origin |
| PHP i backend | PHP-FPM 8.5.12, PDO SQLite, cURL i zapis WWW **PASS na LH**; backend aplikacji **NOT RUN na LH** |
| Prywatny katalog | **FAIL** — rzeczywiste mkdir poza public_html odrzucone przez PHP-FPM; prośba do LH o dedykowany katalog i prawa |
| DNS-01 | **PASS** po zgodach: TXT → valid → cleanup → wydanie PEM; import osobno zatwierdzony i wykonany |
| Stripe karta | **PASS Sandbox + lokalny PHP**, 70,49 PLN; LH NOT RUN |
| Stripe BLIK | **PASS Sandbox + lokalny PHP**, 234,00 PLN dla 2 + 4; LH NOT RUN |
| Webhook | **PASS Stripe CLI → lokalny PHP**, podpis, `paid`, idempotencja; LH NOT RUN |
| InPost mock | **PASS lokalnie**, jawny adapter, UI, HTTP i SQLite |
| InPost Sandbox | **BLOCKED — oczekiwanie na InPost, ticket F60AADBC18** |
| Mobile | **PASS lokalnie**, 320/360/390/430 px; Checkout Stripe 390 px; nie fizyczny telefon/LH |
| Dokumenty prawne | 7 projektów uzupełnionych potwierdzeniami właściciela; pozostałe procesy/GPSR i finalna akceptacja nadal blokują Live |

Dowody: [Stripe i zapas](STRIPE_SANDBOX_20261114.md), [MOCK i uruchomienie lokalne](INPOST_MOCK_TEST.md), [pakiet dokumentów](legal-draft/index.html), [jedna lista brakujących danych D1–D7](legal-draft/index.html#dane).

## Wykonane zmiany

Praca na tej samej gałęzi PR #28: `codex/issue-27-winter26-photo-store`, od `910af9f`. Bez merge.

- `winter-26.css`: usunięty rzeczywisty overflow sekcji zestawów na 320/360 px. Na mobile etykiety zestawów są nad nagłówkiem; nie ściskają tytułu do pojedynczych liter. Reguły wyłącznie poniżej 600 px, desktop bez zmian.
- `api/_common.php`: porównywanie ścieżek prywatnej bazy uwzględnia separatory i wielkość liter Windows. Kontrola granicy katalogu pozostała ścisła; zachowanie POSIX niezmienione.
- `tests/checkout-live-gates.php`: regresje ścieżek (katalog, potomny, podobny prefiks, nadrzędny, inny dysk); przenośna ścieżka fixture SQLite.
- Zachowane fotografie, alt i kadry z `910af9f`, ceny, SKU, stany, dostępność, bramki zakupowe i nieaktywny kod rabatowy. Nie przypisano nowych zdjęć do wariantów. Nie rozwijano ponownie raportu fotograficznego.
- Dodany adapter Points `inpost_points_mock: true`: tylko test, bez tokenów i sieci InPost, z jawnym oznaczeniem oraz danymi syntetycznymi. `winter-config.js` obsługuje wybór i błędy bez ładowania Geowidget w tym trybie. Rzeczywisty provider zachowany osobno.
- Dodane testy MOCK (PHP, UI, HTTP/SQLite), lokalny launcher oraz opt-in driver rzeczywistego Stripe Sandbox. Driver i launcher nie trafiają do wydania WWW. Test UI MOCK dodany do builda.
- Przygotowane projekty siedmiu dokumentów w `docs/legal-draft`; bez publikacji, zmiany aktywnych dokumentów i bez otwierania bramek Live.

## Rzeczywiste zasoby stagingu

| Zasób | Potwierdzony stan |
| --- | --- |
| LH | osobny serwer `serwer533947`, Orange, IP `195.2.223.12`, bez SSH |
| Nowy vhost | `test.pracowniaform.com`, ID `1711054` |
| Katalog WWW | `/public_html/pf-stage-20261114/www` |
| PHP vhosta | 8.5; separacja domeny włączona; Multipoczta wyłączona |
| Nowe konto FTPS | dostęp ograniczony do `/public_html/pf-stage-20261114`; hasło poza repozytorium |
| DNS OVH | trwałe `test A 195.2.223.12` i `test TXT "lh.pl"`, TTL 3600; tymczasowy TXT DNS-01 dodany i usunięty po zgodzie, reszta identyczna |
| Weryfikacja DNS | oba autorytatywne OVH oraz 1.1.1.1 i 8.8.8.8 zgodne; brak AAAA/CAA hosta i CAA apex; szczegóły w nowym raporcie |
| Baza | **nie utworzona na LH**; potrzebna osobna SQLite poza wszystkimi katalogami WWW |
| Kopia przed uploadem | Katalog początkowo i po sprzątaniu pusty, listing WinSCP działa. Nie było istniejących plików do kopiowania; nie deklarujemy kopii aplikacji. Przed przyszłym uploadem powtórzyć inwentaryzację i skopiować ewentualne nowe dane. |
| HTTPS | **PASS po DNS-01 / imporcie Własny**, ważny do 12.02.2027. Pierwotne błędy zarządzanego LE i routing HTTP-01 nadal do diagnozy LH |
| Ochrona dostępu/noindex | **NOT DEPLOYED**; aplikacja, Basic Auth i nagłówki stagingu nie zostały wgrane |

Nie zmieniono apex, `www`, MX, SPF, DKIM, DMARC ani nameserverów. Nie zmieniono istniejących witryn, baz, poczty, certyfikatów ani ustawień wspólnych Pracowni Rachunkowości. Na LH przed utworzeniem stagingu ten serwer pokazywał 0 stron i 0 baz MySQL; utworzono wyłącznie opisane nowe zasoby.

Historia FTPS: wcześniejsze Python/curl zwracały 425 kanału danych. **Obecna sesja WinSCP działa**, co potwierdził upload, listing i cleanup sond. Nie wyłączano TLS ani separacji. [Zgłoszenie LH TKT-KTNHLTAY](https://www.lh.pl/panel/helpdesk/ticket/9235), utworzone 14.11 o 00:39, zaktualizowano o 11:39 czasu panelu o pomiary HTTP-01, odmowę PHP-FPM i pytania o custom SSL/private config. Nadal „W trakcie obsługi”, w chwili kontroli bez odpowiedzi LH. Dotyczy wyłącznie stagingu, bez sekretów i bez zgody na zmiany globalne.

Techniczna domena LH udostępnia `public_html`, dlatego sam katalog obok `www` nie dowodzi prywatności. Przed uploadem sekretów LH musi potwierdzić prywatną ścieżkę i dostęp PHP przy zachowanej separacji. Nie użyto katalogu innej firmy ani wspólnej bazy.

## Testy lokalne — wcześniejsze wyniki aplikacji

Lokalne PHP 8.4.27 NTS z curl/PDO SQLite/SQLite3, pobrane z oficjalnego wydania Windows; SHA-256 paczki zweryfikowany. Bez zmian systemowego PATH. LH PHP 8.5 nie został jeszcze uruchomiony na kodzie aplikacji.

| Kontrola | Wynik i granice |
| --- | --- |
| PHP lint | **PASS**, 15 plików |
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

Pełną matrycę cen sprawdzono lokalnie; w rzeczywistym Stripe Sandbox opłacono 1 szt. z kurierem oraz 2 + 4 z testowym punktem i darmową dostawą. Koszyk 2 + 4 zachowuje ceny dwóch kompletów, ale próg darmowej dostawy liczy łącznie 6 sztuk.

## Mobile i desktop

Rzeczywisty pomiar w przeglądarce lokalnej, nie fizyczny telefon. Landing po poprawce, konfigurator i trzy karty produktów nie mają poziomego overflow na 320/360/390/430 px. W pomiarach mobile scrollbar zajmował 15 px: szerokości treści 305/345/375/415 px. `scrollWidth == clientWidth` we wszystkich czterech. Desktop 1440 px również bez overflow. Zawieszki i kontury zachowują wcześniej zaakceptowane kadry; nie zmieniano zdjęć.

- [Desktop — pełny landing](staging-20261114/landing-desktop.jpg)
- Mobile: [320](staging-20261114/landing-320.jpg), [360](staging-20261114/landing-360.jpg), [390](staging-20261114/landing-390.jpg), [430](staging-20261114/landing-430.jpg)
- [Konfigurator — wybór i podsumowanie](staging-20261114/configurator-mobile-selection.jpg)
- [Pomiary landingu](staging-20261114/landing-after.json), [konfiguratora](staging-20261114/mobile-measurements.json)
- Nowy MOCK: [desktop](staging-20261114/mock-desktop.jpg), [mobile](staging-20261114/mock-mobile.jpg), [cztery szerokości bez overflow](staging-20261114/mock-mobile-measurements.json). W UI potwierdzono zmianę A → B, zapis próby, blokadę przy awarii API oraz poprawne przejście na kuriera. Test HTTP sprawdza także ręczne kody, nieczynne punkty, kanoniczny adres w SQLite, idempotencję i koszyk 2 + 4.

## Stripe i InPost — środowiska zewnętrzne

| Test rzeczywisty | Status |
| --- | --- |
| Stripe karta Sandbox | **PASS z lokalnym PHP**, Succeeded, `paid`, 70,49 PLN, `livemode=false` |
| Stripe BLIK Sandbox | **PASS z lokalnym PHP**, Succeeded, `paid`, 234,00 PLN, `livemode=false` |
| PLN / kwota koszyka w rzeczywistym Checkout | **PASS** dla karty 1 szt. + kurier i BLIK 2 + 4 + punkt MOCK gratis |
| Podpisany webhook z Stripe do LH | **NOT RUN** |
| Podpisany webhook Stripe CLI → lokalny PHP | **PASS**, trzy zdarzenia, HTTP 200, poprawny HMAC; nieprawidłowy podpis HTTP 400 |
| `livemode=false` na konkretnych transakcjach | **PASS**, odczyt API obu sesji i zdarzeń oraz obie płatności Succeeded w Dashboard Sandbox |
| Opłacone zamówienie / pojedyncze odjęcie właściwego SKU na LH | **NOT RUN** |
| Opłacone zamówienie / właściwy SKU w lokalnej SQLite | **PASS**, VASE/marble 20→17, STAR/red-matte 20→18, MEDALLION/white 20→18; tylko stany syntetyczne |
| InPost mapa / wybór / zmiana punktu / przełączenie na kuriera | **NOT RUN na LH** |
| InPost rzeczywista walidacja kodu/adresu i zapis punktu | **NOT RUN** |

Stripe: wykorzystano istniejący klucz testowy, przechowany poza repo; nie tworzono nowego klucza ani stałego endpointu webhook w Dashboard. Sekret tymczasowego nasłuchu CLI również jest prywatny. [Dokładny zakres testu i identyfikatory](STRIPE_SANDBOX_20261114.md).

**Aktualizacja InPost 14.11:** logowanie do testowego Konta InPost na `stage-self-service.inpost-group.com` zostało potwierdzone; przejście do Managera Sandbox kończy się pomyślną autoryzacją i żądaniem dokończenia rejestracji. Rejestrację blokuje błąd pola kodu pocztowego. Pole automatycznie dodaje myślnik i podpowiada `01-990`, ale ma `pattern="[0-9]*"`; także przykład z podpowiedzi kończy się `patternMismatch` i klasą Angular `ng-invalid`. Wpisanie samych cyfr oraz znak po znaku nie pomogło. Przywrócono dane właściciela; nie wysłano rejestracji ani nie obchodzono walidacji.

Po zgodzie właściciela wysłano [formularzem wsparcia InPost](https://inpost.pl/formularz-wsparcie) zgłoszenie **F60AADBC18**, kategoria „Wsparcie klienta / Webserwis / Manager paczkomatów”. Portal potwierdził przyjęcie i zapowiedział odpowiedź w ciągu **2 dni roboczych**. Przekazano opis odtworzenia błędu i zatwierdzony kontakt do odpowiedzi; bez haseł, tokenów, identyfikatorów sesji i załączników zawierających dane konta. Dostęp do API/Geowidget Sandbox pozostaje zablokowany do zakończenia rejestracji. Nie użyto ujawnionego wcześniej tokenu ani sesji produkcyjnej, nie utworzono przesyłek ani etykiet. Rozdział środowisk potwierdza [dokumentacja Geowidget InPost](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/pages/50069505).

## Dokumenty i dane blokujące Live

- Gotowy [pakiet 7 projektów HTML](legal-draft/index.html), zaadaptowany z PR #4: regulamin, dostawa/płatności, zwroty/reklamacje, wzór odstąpienia, prywatność, cookies/zgody i GPSR. Oznaczone **DO AKCEPTACJI / NIEPUBLIKOWANE**, z jedną tabelą danych D1–D7. Nie są zatwierdzonymi dokumentami Live.
- **PASS** struktury i 57 odwołań w 8 stronach pakietu. Źródła prawne, ograniczenia weryfikacji oraz pozostałe kontrole: [raport prawny](WINTER26_LEGAL_REVIEW.md). Aktywna polityka prywatności i treści strony bez zmian.
- Cookies i zgody: lokalna suita przechodzi, marketing pozostaje odrębny od zakupu. Nie testowano wysłania formularza do Brevo ani doręczenia wiadomości; nie zapisano testowego adresu na produkcyjną listę.
- Pakiet prawny zawiera już potwierdzone przez właściciela: sprzedawcę/producenta/administratora, kontakt, adres zwrotów, PLA, faktury Subiekt 123 e-mailem i kontakt do spraw danych bez tytułu IOD. Parametry CAD trzech modeli odczytano ze źródeł projektu; nie są pomiarem gotowych sztuk. Nie zmieniono automatycznie flag akceptacji katalogu. Karty A6 nadal są proofem, nie plikami dopuszczonymi do druku.

Skrót jednej [listy danych i decyzji D1–D7](legal-draft/index.html#dane), bez ponownego pytania o ceny i potwierdzone geometrie:

1. Nie pytamy ponownie o potwierdzone dane firmy, adres i kontakt. Pozostaje test doręczenia wiadomości oraz rzeczywista obsługa potwierdzeń/faktur i realizacji zamówień.
2. Pozostają pomiary gotowych sztuk, specyfikacja dokładanych zawieszek, identyfikacja partii, ocena ryzyka i wynikające z niej instrukcje GPSR.
3. Wcześniejsze opłacone zamówienia: nadanie **1 grudnia 2026**; płatności od tej daty: 2–3 dni robocze. Termin 23.11 zastąpiony decyzją właściciela. Do zamknięcia zasada jednej paczki, częściowe zwroty zestawów oraz moment zawarcia umowy i potwierdzenia. Nadanie nie gwarantuje daty doręczenia.
4. Rzeczywiste umowy/role dostawców, retencja i pomiary usług zewnętrznych oraz finalna akceptacja dokumentów; pełen aktualny zakres w pakiecie prawnym D1–D7.

## Paczka i decyzja

Build z czystego commitu `4ce364b3bb200d61490ad87542637980a2df9e01`: **PASS**, w tym 15 plików PHP i nowy test UI MOCK.
125 plików, ZIP 9 210 328 bajtów; SHA-256 `0b322faf4b6263a8a25b17ca891bd2fccd93753a3224b790d986e44ba7a44adc`.
Paczka lokalna `.artifacts/lh-4ce364b3bb20/pracownia-form-lh.zip`, `uploaded_by_this_build=false`. Nie jest jeszcze skonfigurowanym stagingiem z uwierzytelnieniem. Raporty prawne, sterowniki testowe, SQLite i sekrety są wyłączone z paczki.

Późniejsze poprawki launchera otrzymały blokadę i kontrolę portu; test HTTP/SQLite przeszedł po wskazaniu bazy właściwego serwera. Nie zaliczono nieudanych prób jako PASS. **Powyższy ZIP jest historyczny:** późniejszy commit `70c1fd0` zmienił datę nadań na 1 grudnia i uzupełnił pakiet prawny. Przed uploadem zbudować i sprawdzić aktualne wydanie; nie przesyłać starej paczki z terminem 23 listopada. Obecny etap diagnostyki dodaje jedynie dokumentację, dowody i szablon sondy poza wydaniem WWW.

**NO-GO do odbioru LH:** FTPS odblokowany; nadal potrzebne poprawne HTTPS i jednoznacznie prywatny katalog SQLite/sekretów. DNS-01 przygotowany do osobnej akceptacji TXT i importu, prywatna ścieżka oczekuje LH. Następnie aktualny build, upload z ochroną dostępu/noindex i bezpośredni webhook Stripe na LH. InPost nie blokuje dalszego testu sklepu: można użyć jawnego MOCK, a prawdziwy Sandbox pozostaje `BLOCKED — F60AADBC18`. Żaden lokalny PASS nie zastępuje prób na LH i fizycznym telefonie. Bez produkcyjnego DNS, merge, Stripe Live i reklam.
