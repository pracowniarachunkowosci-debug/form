# Druga recenzja checkoutu WINTER 26, 21.11.2026

Kandydat: draft PR #30, branch `codex/winter26-checkout-retry-20261121`. Bez publikacji i merge. Wszystkie zmiany oraz testy zapisu wykonano lokalnie. Nie zmieniano produkcyjnych plików, baz, konfiguracji, cen, SKU, fotografii, dokumentów ani DNS.

## Świeży odczyt Uberspace

21.11.2026 o **15:32:16 CET** odczytano przez SSH rzeczywiste źródła sześciu plików w `/var/www/virtual/pf26/winter26-live/app/public`. Nie uruchamiano PHP aplikacji na produkcji, inicjalizatorów, migracji, reconciliatora ani operacji zapisu. Nie czytano konfiguracji ani baz. Klucz SSH odblokowano w lokalnym oknie; jego hasła nie zapisywano ani nie przekazywano do modelu.

Hashe `_common.php`, `_reservations.php`, `checkout.php`, `webhook.php` i `winter-config.js` są identyczne z tabelą poprzedniego raportu. Dodatkowo `_live.php`: `44eefd076f747dda7133a28a01ab04b04c59b34d44965c07b347488e1ffbc6bd`, zgodny z archiwalnym manifestem. Wersja checkoutu pozostaje zgodna z wydaniem `PF-W26-FINAL-20261119-145544-CET`. GitHub nie służył do odtwarzania produkcji. Baza PR `ce3d214` nadal odpowiada badanym źródłom checkoutu; nie jest pełnym źródłem całej witryny.

## Problem A: potwierdzony

W produkcji `existing_order()` dopuszcza tylko `reserved` i `reconcile`, a `pending` odrzuca jako `FINISHED`. Pierwsza wersja PR zastąpiła ten błąd `PAYMENT_PENDING`, ale nadal przerywała obsługę przed sprawdzeniem sesji; dodatkowa kontrola na wejściu `stripe_session()` blokowała ją ponownie. W efekcie kliknięcie mogło jedynie odczytać lokalny stan i liczyć na webhook lub worker, mimo komunikatu sugerującego sprawdzenie płatności.

Poprawka:

- Weryfikacja tożsamości właściciela, requestId, koszyka, dostawy i tokenu pozostaje obowiązkowa. Następnie `pending` przechodzi do sprawdzenia sesji.
- `stripe_session()` dla `pending` odczytuje zapisany SID i wykonuje GET tej sesji. Świadome kliknięcie omija harmonogram `next_check`, ale nie omija lease zabezpieczającego równoległe żądania.
- `pending` bez SID nie może wykonać POST ani zwolnić stanów. Ta zasada obowiązuje również we wspólnym reconciliatorze, nie tylko w HTTP.
- Spóźniony GET z `open` nie cofa `pending` do `reserved` i nie udostępnia ponownego przekierowania do płatności.
- `complete/paid` oznacza `paid`. `complete/unpaid` pozostaje `pending`: samo `unpaid` nie dowodzi definitywnej odmowy. Potwierdzony event `async_payment_failed` lub potwierdzone `expired` zwalnia rezerwację dokładnie raz.
- `completed`, `async_payment_succeeded`, `async_payment_failed`, `expired` zachowują dotychczasową walidację podpisu, powiązania, kwoty i trybu. Nie zmieniono webhook.php. Fencing chroni przed starym wynikiem GET po webhooku.

To nie jest ponowne obciążenie: sprawdzenie `pending` nie tworzy zamówienia, sesji, PaymentIntent ani płatności. Dokumentacja rozróżnia przetwarzanie i późniejsze zdarzenia płatności: [Stripe fulfillment](https://docs.stripe.com/checkout/fulfillment). Testy BLIK w tym raporcie dotyczą kontraktu stanów; rzeczywiste zachowanie BLIK musi zostać sprawdzone w Sandbox.

## Problem B: potwierdzony

Produkcyjny frontend nie ma nowego mechanizmu sessionStorage z PR. Pierwsza wersja PR zachowywała poprzedni payload i ponawiała go poprawnie, ale pozostawiała aktywną edycję liczby, wariantów, zestawów i punktu. Widoczny koszyk mógł więc różnić się od wysyłanego zamówienia. Aktualna produkcja oferuje tylko Paczkomat, więc alternatywna metoda dostawy nie jest widoczna w jej UI.

Poprawka przywraca ze snapshotu dokładny skład wszystkich zestawów, punkt odbioru, zaakceptowane warunki, kwotę i zapisany termin; wyświetla podsumowanie zapisanej próby. Równocześnie blokuje natywne kontrolki oraz funkcje edycji, w tym syntetyczne eventy z galerii i spóźnione odpowiedzi wyboru punktu. Potwierdzenie terminu nie jest odświeżane pod aktywną próbą.

Nowy zapis zawiera publiczny kontekst wyświetlania punktu i terminu. Starszy zapis bez kontekstu nadal zachowuje payload i token; UI informuje, że obowiązuje poprzednio potwierdzony termin, zamiast wymyślać datę lub nowy plan. Po potwierdzonym `released` blokady są zdejmowane, a nowa płatność wymaga świadomego kliknięcia i nowych wymaganych potwierdzeń. `paid` i `review` nie odblokowują następnej płatności. `pending` udostępnia wyłącznie sprawdzenie tej samej próby.

`pageshow` przy odtworzeniu z BFCache usuwa wyłącznie stan zajętości przycisku, zachowując próbę. Odświeżenie i ponowne otwarcie innej strony konfiguratora w tej samej karcie przywraca zapisany koszyk. Zakres trwałości to `sessionStorage` danej karty; nie jest to mechanizm globalnej synchronizacji niezależnie otwieranych kart ani odtwarzania po usunięciu danych przeglądarki.

## Zmienione pliki w drugiej recenzji

| Plik | Cel |
| --- | --- |
| api/_common.php | Dopuszczenie pending do ścieżki sprawdzenia po weryfikacji pierwotnego zamówienia |
| api/_reservations.php | GET zapisanego SID; zakaz POST dla pending; brak cofnięcia do reserved; zachowanie lease i fencing |
| winter-config.js | Przywrócenie i blokada koszyka; zachowanie punktu i terminu; obsługa BFCache |
| tests/checkout-pending.php | Integracja order → odczyt Stripe → stan/stock; komplet zdarzeń, brak drugiej sesji, wyścigi |
| tests/checkout-basket-lock-ui.cjs | Edycja, reload, ponowne otwarcie, powrót, wiele zestawów, nowa próba dopiero po released |
| tests/checkout-retry.php | Korekta kontraktu: pending ma przechodzić do bezpiecznego sprawdzenia |
| tests/checkout-retry-ui.cjs | Wspólny harness aktualnego kontrolera, wariant adresu i event pageshow |
| docs/CHECKOUT_DIAGNOSIS_20261121.md | Oznaczenie ograniczeń pierwszej recenzji i odsyłacz do aktualnych wyników |
| docs/CHECKOUT_REVIEW2_20261121.md | Niniejszy raport |

## Testy i zakres dowodu

PASS lokalnie: `checkout-sandbox.php`, `checkout-live-gates.php`, `checkout-locker.php`, `checkout-pending.php` (uruchamia również `checkout-retry.php` i `checkout-reconciliation.php`), `checkout-retry-ui.cjs`, `checkout-basket-lock-ui.cjs`, składnia PHP/JS i pakiet trzech plików do przeglądu.

Testy integracyjne używają rzeczywistego SQLite oraz kodu obsługi zamówień, z transportem Stripe zastąpionym kontrolowanymi odpowiedziami. Testy UI wykonują rzeczywisty JS w harnessie DOM; reload/reopen i BFCache są symulowane. To nie jest rzeczywisty test przeglądarki na stronie Stripe.

| Scenariusz | Wynik |
| --- | --- |
| BLIK/pending po completed/unpaid | PASS, rezerwacja zachowana |
| Późniejszy sukces GET i async_payment_succeeded | PASS, paid, brak kolejnej płatności |
| Późniejsza odmowa async_payment_failed | PASS, released dokładnie raz, także przy powtórzonym evencie |
| Powrót podczas pending | PASS zachowany request, widoczny zapisany koszyk |
| Odczyt istniejącej sesji | PASS dokładny GET SID, również przed next_check |
| Brak drugiej sesji/zamówienia | PASS licznik CREATE bez zmian, jeden rekord zamówienia |
| Edycja przy niepewnym wyniku | PASS liczba/model/kolor/zestawy/punkt/termin; kontrolki i handlery zablokowane |
| Reload i ponowne otwarcie | PASS ten sam ID/payload; inny URL nie zmienia koszyka |
| Released i świadoma nowa próba | PASS, brak automatycznego POST; nowy ID po kliknięciu |
| Podwójny klik / równoległe sprawdzenie | PASS jeden request UI / jedna operacja GET pod lease |
| Wyścig webhook/GET | PASS sukces i odmowa wygrywają ze starym GET |
| Rezerwacje | PASS paid/pending trzymają, potwierdzona odmowa/expiry zwalnia raz, timeout nie zwalnia |
| Pending bez SID i stary open | PASS bez POST, bez cofnięcia do reserved |
| Powrót Wstecz/BFCache | PASS odblokowanie sprawdzania bez usunięcia ID i bez odblokowania edycji |

Starych kontroli wydania nie wyłączano. Pełny build oraz znane historyczne kontrole render/publication/composition i stare harnessy UI pozostają osobnymi blokadami opisanymi w poprzednim raporcie; nie deklaruje się zielonego pełnego wydania.

## Rzeczywisty Stripe Sandbox: wykonany częściowo 21.11.2026

Odczyt SSH potwierdził osobny katalog stagingu i istnienie pliku konfiguracji testowej, bez odczytu jego treści. Cztery z sześciu porównanych plików stagingu mają inne hashe niż produkcja; staging nie zawiera tej poprawki. Początkowe anonimowe żądania zwracały 401. Po zalogowaniu przez właściciela użyto istniejącej sesji Chrome, bez ponownego pobierania haseł ani tokenu. Dostęp testera działa. API status potwierdziło `mode: test`, `available: true`, approvalVersion `9f36abae3149fb6e9f7489d935f6b69a9d7fafb6c23c5b1cffcd432cb2e6972d`.

Koszyk w obu świadomie rozpoczętych próbach: 1 × VASE Dual (50,00 zł), Paczkomat InPost WRO01M (18,49 zł), razem 68,49 zł. InPost zweryfikował rzeczywisty punkt, bez nadania przesyłki. Stripe wyświetlił „Pracownia Form sandbox”, „Piaskownica”, sesje `cs_test_` i identyczne pozycje/kwoty. Nie użyto Stripe Live ani prawdziwych danych płatniczych.

| Scenariusz na istniejącym Uberspace staging | Obserwacja |
| --- | --- |
| Pierwszy redirect do Stripe | PASS, właściwa kwota i dostawa, rzeczywista sesja TEST |
| Odmowa BLIK | PASS, wzorzec e-mail `bank_declined` i kod testowy z dokumentacji; komunikat odmowy, formularz ponownie aktywny |
| Odmowa karty | PASS, oficjalna karta testowa odmowy; komunikat odmowy, ta sama sesja |
| Powrót bez zapłaty | PASS strona „Przerwano próbę płatności”; sama nawigacja nie deklaruje płatności |
| Powrót do konfiguratora i kontynuacja | FAIL: pusty zestaw 6 sztuk zamiast zapisanego VASE Dual; obecny staging nie ma mechanizmu PR #30 |
| Ponowienie w istniejącym Stripe Checkout | PASS: historia przeglądarki otworzyła dokładnie ten sam SID; bez nowej sesji na tym kroku |
| Sukces karty | Karta sukcesu w tej samej sesji przekierowała na „Powrót z płatności testowej” |
| Sukces BLIK | Druga, świadomie utworzona próba; pokazano oczekiwanie „Zatwierdź płatność”, następnie automatyczny powrót na stronę płatności testowej |
| Stan dostępny VASE Dual | API przed: 19; po dwóch próbach: 17. Zgodne z dwoma rezerwowanymi/sprzedanymi egzemplarzami; nie dowodzi stanu paid |
| Webhook, paid/pending/released w SQLite | NIEPOTWIERDZONE: SSH w BatchMode odrzucił istniejące uwierzytelnienie; nie pobierano ponownie sekretów |
| Rzeczywisty pending → GET, expiry i zwolnienie raz | NIEPOTWIERDZONE E2E; lokalne testy integracyjne PASS |

Strona powrotu jest ogólna: nie jest dowodem zapisania `paid` ani dostarczenia webhooka. Utworzenie sesji potwierdza działanie uprawnienia CREATE w TEST, lecz nie jest pełnym audytem uprawnień restricted ani dowodem GET i webhooków. Nie potwierdzono na nowo ścieżki aktywnej SQLite ani izolacji jej pliku przez SSH; potwierdzono osobny katalog aplikacji i tryb TEST. Nie wykonywano bezpośrednich zapisów do baz, resetów, zmian konfiguracji ani wdrożeń.

Testy wykonywano według [Stripe BLIK](https://docs.stripe.com/payments/blik/accept-a-payment?payment-ui=checkout) i [kart testowych Stripe](https://docs.stripe.com/testing), z syntetycznymi danymi. Nie zaliczamy całości E2E ani kandydata PR: wymagane pozostają wdrożenie kandydata wyłącznie na zatwierdzony staging, kontrola izolacji SQLite, odczyt rekordów i webhooków oraz rzeczywista weryfikacja bezpiecznego ponowienia ze sklepu. PR pozostaje draftem.

## Kolejny test zakupowy

Na zweryfikowanym Sandbox: ułożyć koszyk, wybrać punkt, potwierdzić podsumowanie i przejść do Stripe. Sprawdzić osobno kartę oraz BLIK, sukces, odmowę i powrót bez płatności. Podczas pending wrócić, odświeżyć i otworzyć inny URL konfiguratora w tej samej karcie: ma pozostać poprzedni skład/kwota/punkt/termin, edycja ma być nieaktywna. Kliknięcie sprawdzenia ma wykonać wyłącznie GET istniejącej sesji. Porównać SID, liczbę zamówień i historię rezerwacji przed/po; nigdy nie czyścić bazy dla ponowienia.

Po potwierdzonym released sprawdzić możliwość edycji i świadomego rozpoczęcia nowej próby. Dla paid/review nie powinno być kolejnej płatności. Scenariusze BLIK wykonywać według aktualnej [instrukcji Stripe Sandbox](https://docs.stripe.com/payments/blik/accept-a-payment?payment-ui=checkout), z syntetycznymi danymi i wyłącznie TEST. Produkcja pozostaje bez zmian do akceptacji właściciela.
