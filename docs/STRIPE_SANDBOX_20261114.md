# Rzeczywisty Stripe Sandbox + lokalny PHP — 14.11.2026

**PASS dla Stripe Sandbox i lokalnego backendu. NIE jest to test LH ani Live.**

Istniejące konto `Pracownia Form sandbox`, `acct_1UXldqH7sElYuMPY`. Sesje utworzył
produkcyjny kod `quote()` → `order()` → `stripe_session()` → `bind_session()`, wywołany
przez jawny, niewdrażany [driver integracyjny](../tests/stripe-sandbox-probe.php).
Checkout obsłużono w przeglądarce przy 390 × 844 px, nie na fizycznym telefonie.
Użyto wyłącznie danych syntetycznych, karty testowej Stripe i kodu testowego BLIK.
Nie zapisano karty w Link. Nie użyto Live, prawdziwej karty, API InPost ani etykiet.

## Wyniki rzeczywistych płatności

| Próba | Karta + kurier | BLIK + testowy punkt |
|---|---|---|
| Koszyk | 1 × VASE / marble | 2 + 4; VASE/marble × 2, STAR/red-matte × 2, MEDALLION/white × 2 |
| Towar | 50,00 zł | 84,00 + 150,00 = 234,00 zł |
| Dostawa | 20,49 zł | 0,00 zł — 6 ozdób łącznie |
| Razem / waluta Stripe | 7049 groszy / `pln` | 23400 groszy / `pln` |
| Stripe Dashboard | Succeeded, Visa ••••4242 | Succeeded, BLIK |
| API sesji | `payment_status=paid`, `livemode=false` | `payment_status=paid`, `livemode=false` |
| Lokalna SQLite | `state=paid` | `state=paid` |
| Dostawa | adres dostawy PL obecny w sesji | `TEST01A`, adres oznaczony TEST / MOCK zapisany w zamówieniu i metadanych |

Identyfikatory do porównania z panelem:

- Karta: zamówienie `w26_e9bcf73911b6d5ea39a2d242`, płatność `pi_3UbUjtH7sElYuMPY1rIYhi4k`.
- BLIK: zamówienie `w26_e9545aaa07d0fc65cdd05751`, płatność `pi_3UbUluH7sElYuMPY1R2DovJT`.
- Pełny odczyt bez kluczy i danych kontaktowych: [wyniki JSON](staging-20261114/stripe-sandbox-results.json).
- [Dowód w Stripe Dashboard](staging-20261114/stripe-dashboard-payments.jpg).

Zrzut panelu pokazuje obie nowe płatności z 14 listopada oraz starsze próby z 4 listopada.
Nie zmieniano ani nie refundowano starszych transakcji. Panel używa UTC, PHP czasu Warszawy.

## Webhook i zapas

Oficjalny Stripe CLI 1.55.11 przekazał rzeczywiste podpisane zdarzenia do odbiornika
`http://127.0.0.1:8788/webhook`. Sekret CLI i klucz API pozostają poza repozytorium.
Odbiornik sprawdził HMAC i wiek podpisu, a następnie uruchomił `apply_event()` z aplikacji:

| Zdarzenie | Typ | HTTP | Podpis / ponowne przetworzenie |
|---|---|---|---|
| `evt_1UbUjuH7sElYuMPYQRolGk9f` | `checkout.session.completed` — karta | 200 | poprawny; zapas bez ponownego odjęcia |
| `evt_1UbUm8H7sElYuMPYxujOEGmo` | `checkout.session.completed` — BLIK | 200 | poprawny; zapas bez ponownego odjęcia |
| `evt_1UbUm8H7sElYuMPYJ19NavQI` | `checkout.session.async_payment_succeeded` — BLIK | 200 | poprawny; zapas bez ponownego odjęcia |

Każde zdarzenie miało `livemode=false`. Powtórzono `apply_event()` dla tego samego
rzeczywistego zdarzenia i porównano zapas. Nie przedstawiamy tego jako ponownej dostawy
HTTP przez Stripe. Oddzielny POST z niepoprawnym podpisem został odrzucony kodem **400**.
Powtórne utworzenie tej samej sesji zwróciło ten sam identyfikator Stripe; ponowne
`order()` nie utworzyło drugiej rezerwacji.

Osobna, jednorazowa baza zaczynała od 20 szt. każdego z trzech testowanych SKU:

| SKU | Start | Po obu zamówieniach | Oczekiwany rozchód |
|---|---:|---:|---:|
| `full-soft:marble` | 20 | 17 | 3 |
| `knitted-star:red-matte` | 20 | 18 | 2 |
| `knitted-medallion:white` | 20 | 18 | 2 |

Zapas jest rezerwowany atomowo przy tworzeniu zamówienia. Zapłata potwierdza rozchód,
nie odejmuje tych samych sztuk po raz drugi. Katalog sprzedażowy i rzeczywiste stany
pozostały niezmienione. Błędy, zwalnianie rezerwacji, późne zdarzenia i anulowania
pokrywa suita offline `tests/checkout-sandbox.php`; nie deklarujemy nowych rzeczywistych
płatności błędnych/anulowanych ani prób tych scenariuszy na LH.

## Odtwarzanie i ograniczenia

Driver wymaga `PF_STRIPE_PROBE_CONFIG` wskazującego prywatny JSON poza repo, z
`purpose=local-stripe-sandbox-probe`, `mode=test`, kluczem `sk_test_…`,
`origin=http://127.0.0.1:8788`, osobnym `db_file` o nazwie `stripe-probe.sqlite` w tym
samym prywatnym katalogu oraz `signing_secret_file`. Nie używać bazy stagingu/produkcji.
Polecenie `create card-courier` lub `create blik-mixed-locker` tworzy rzeczywistą sesję
Sandbox, dlatego nie uruchamia się automatycznie podczas builda. Opcjonalny trzeci
argument pozwala ponowić własne niezakończone zamówienie bez ponownej rezerwacji.
`inspect` tylko odczytuje wynik. Router uruchamia się wyłącznie przez PHP CLI server
na loopback. `tests/` nie trafia do paczki WWW.

Publiczne certyfikaty z istniejącego magazynu zaufania Windows dodano do lokalnego
pliku CA PHP po błędzie OpenSSL 60. Weryfikacja TLS pozostała włączona. Nie zmieniano
systemowego magazynu zaufania, certyfikatów serwera ani konfiguracji LH.

Próba BLIK używała kodu Sandbox zgodnie z [oficjalną instrukcją Stripe](https://docs.stripe.com/payments/blik/accept-a-payment?payment-ui=checkout).
Transport zdarzeń: [Stripe CLI](https://docs.stripe.com/stripe-cli).

**Pozostaje odbiór na LH:** prawdziwe HTTPS, kontrola dostępu, prywatna baza i
konfiguracja, wdrożony endpoint `/api/webhook.php`, webhook dostarczony bezpośrednio
przez Stripe oraz pełna ścieżka sklepu na telefonie. Lokalny driver nie potwierdza
tych elementów ani pełnej obsługi cookies/origin/logowania testera na LH.
