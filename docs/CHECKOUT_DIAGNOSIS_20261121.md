# WINTER 26 checkout — diagnoza i poprawka do przeglądu

Aktualizacja drugiej recenzji: [CHECKOUT_REVIEW2_20261121.md](CHECKOUT_REVIEW2_20261121.md). Pierwsza wersja PR miała luki w sprawdzaniu `pending` i blokadzie edycji; poniższy raport historyczny nie stanowi dowodu ich poprawności. Aktualne poprawki, świeży odczyt Uberspace i testy opisuje raport drugiej recenzji.

Status: draft, bez publikacji, bez merge, bez Stripe Live. Produkcyjnej bazy, stanów, konfiguracji, cen, SKU, zdjęć, dokumentów i hostingu nie zmieniano.

## Ustalenie wersji

Badany adres: https://pracowniaform.com/sklep/winter-zestaw-4.html?size=1&model=full-soft&color=dual#kompozycja

Wydanie `PF-W26-FINAL-20261119-145544-CET` powstało z rzeczywistych plików serwera, nie z jednego commitu Git. Commit `b2f279fc55a857ac37e871fee4aba151a320072a` w draft PR #29 dokumentuje publikację, ale NIE jest kompletnym źródłem produkcji. PR #28 ani bieżący branch nie są jej dowodem.

Publiczny GET JS oraz odczyt SSH plików backendu potwierdziły zgodność z manifestem tego wydania:

| Plik | SHA-256 produkcji |
| --- | --- |
| api/_common.php | 85276bf045ac21b775f338e166bed2767f42493938fc1762449d7cafcdc27860 |
| api/_reservations.php | e82122b57ade52f434e05d4aa9b28e139990513064d5cc927138a7feed05f77c |
| api/checkout.php | 1e839872dbd5aa13e0d0d0c70b0ff6c6a64fc16f35e59a98c98d5b482b32cbf2 |
| api/webhook.php | 94fa5c4e74c7457e4f653f2999909ff3f3f097b4a9928c5085dcea4a08d8b0f6 |
| winter-config.js | 8ad0bd3dcdf50cec40c6c4faa92958b36087b4b3775d9715646839eb634204ec |

Lokalny commit `ce3d214` stanowi kotwicę źródeł checkoutu odczytanych z wydania. Reszta tego drzewa repozytorium NIE jest pełnym obrazem produkcji. Nie wdrażać całego brancha. Z tego powodu PR ma osobny branch bazowy kotwiczący checkout; jego diff pokazuje poprawkę, a nie wcześniejszy rozjazd produkcji z Git.

## Potwierdzona przyczyna

SQLite otwarto przez `mode=ro` i `PRAGMA query_only=ON`; nie wywoływano inicjalizatora bazy aplikacji ani reconciliatora produkcji. W ostatnich czterech godzinach znaleziono jedną próbę za 6849 groszy, utworzoną **21.11.2026 o 14:44:35 CET**, pasującą do podanego czasu i kwoty. Nie identyfikowano klienta przez dane osobowe.

Historia: `RESERVED` → `CREATE_ATTEMPT` → `CREATE_RESULT {http:0, notSent:true, reason:LOCAL_KEY}` → `LOCAL_NOT_SENT_RELEASE`. Bieżący stan: `released`; `sid` pusty. Nie ma aktywnej rezerwacji tej próby. Kod kończy transport przed `curl_init`, więc żądanie tworzenia sesji nie zostało wysłane i ta operacja nie utworzyła sesji Stripe. W jej historii nie ma wygaśnięcia ani webhooka jako przyczyny zakończenia. Nie wykonywano niezależnej inspekcji konta Stripe Live.

`_live.php` akceptuje rodziny kluczy `sk_live` i `rk_live`, natomiast `reservation_http()` akceptował wyłącznie `sk_live`. Produkcja przeszła bramkę Live, ale transport odrzucił klucz lokalnie. To potwierdzona niespójność walidacji; jej skutkiem było bezpieczne zwolnienie próby, a potem błąd `FINISHED` przy powtarzaniu tego samego `requestId`. Restricted keys są wspieranym typem klucza Stripe: https://docs.stripe.com/keys

Nie odczytywano ani nie ujawniano klucza. Dostępność i uprawnienia klucza po stronie Stripe wymagają jeszcze testu Sandbox i późniejszej kontroli operacyjnej.

## Przebieg i poprawka

1. Przycisk blokuje drugi równoległy klik. Identyfikator pochodzi z UUID, a przy potwierdzaniu terminu z `dispatchId`.
2. POST `/api/checkout.php` sprawdza origin, bramki, ofertę, warunki, koszyk i dostawę. `order()` w transakcji zachowuje jedną operację dla danego identyfikatora; istniejąca próba musi odpowiadać właścicielowi i koszykowi.
3. Mechanizm rezerwacji zapisuje dokładne body i klucz idempotencji przed wysłaniem, z blokadą pracy i oznaczeniem niepewności. Poprawka dopuszcza oba typy kluczy, zachowując rozdzielenie test/live.
4. `reservation_reconcile()` tworzy lub odzyskuje sesję; zapis sesji następuje przez `reservation_apply_session()`. Starsza funkcja `bind_session()` nie jest używana w produkcyjnej ścieżce checkoutu tego wydania.
5. Webhook weryfikuje podpis, tryb, kwotę i powiązanie sesji. Jego stan wygrywa ze spóźnioną odpowiedzią tworzenia sesji; nie zmieniono zasad zwalniania stanów. Nowe testy obejmują webhook przed zapisem SID.
6. Frontend weryfikuje kwotę i domenę URL przed `location.assign`. Zachowuje dokładne żądanie również w `sessionStorage` na powrót do sklepu. Nie generuje nowego zamówienia po timeout, błędnym JSON, nieznanym wyniku ani edycji koszyka w czasie niezamkniętej próby.
7. `ATTEMPT_RELEASED` pozwala wyczyścić zakończoną próbę i na następne świadome kliknięcie utworzyć nowy UUID wraz z nowym potwierdzeniem terminu. Nie następuje automatyczny POST nowego zamówienia.
8. `ORDER_PAID` i `PAYMENT_REVIEW` blokują kolejną płatność; `PAYMENT_PENDING` zachowuje identyfikator i pozwala ponownie sprawdzić wynik. Istniejący konflikt tokenu terminu zwraca `REQUEST_CONFLICT`, więc nie może omyłkowo odblokować nowej płatności.

Runtime zmienia tylko `api/_common.php`, `api/_reservations.php`, `winter-config.js`. Pozostałe zmiany to testy, dostosowane fixture'y już wdrożonych bramek, raport i generator lokalnego pakietu przeglądowego.

## Walidacja

PASS: `php tests/checkout-sandbox.php`, `php tests/checkout-live-gates.php`, `php tests/checkout-locker.php`, `php tests/checkout-retry.php` (wykonuje też pełne `checkout-reconciliation.php`), `node tests/checkout-retry-ui.cjs`. Wszystkie używają izolowanych danych i syntetycznych transportów, bez transakcji Stripe.

| Scenariusz | Wynik / zakres |
| --- | --- |
| Pierwsze przejście do Stripe | PASS kontrakt sesji i wywołanie przekierowania w kontrolerze; bez rzeczywistej strony Stripe |
| Powtórzenie żądania | PASS ten sam order/SID/body/key, jedna rezerwacja |
| Podwójny klik | PASS jedna prośba UI; również test dwóch procesów/lease SQLite |
| Błąd połączenia | PASS nieznany wynik zachowuje body/key; ponowienie odzyskuje sesję |
| Wygaśnięcie | PASS potwierdzone zdarzenie zwalnia dokładnie raz |
| Nowa próba po zakończeniu | PASS osobny UUID dopiero po jednoznacznym stanie |
| Stany magazynowe | PASS niedobór/rollback, wielokrotne eventy, tryb produkcji na zamówienie |
| Sukces płatności | PASS syntetyczny podpisany webhook, brak ponownego obciążenia |
| Odrzucenie | PASS pozostająca otwarta sesja i osobno async failure; nie wykonywano odmowy na prawdziwej stronie Stripe Sandbox |
| Powrót bez płatności | PASS zapisany request i ponowne wykorzystanie sesji |
| Restricted keys | PASS obie rodziny, odrzucenie kluczy z innego trybu i błędnego formatu |
| Wyścig webhook/create | PASS paid/expired przed odpowiedzią, bez cofnięcia stanu |

PASS: składnia 20 plików PHP w `api` i trzech głównych JS; kontrole cen, registry, store gate, consent i config.

FAIL: pełny `python scripts/build_release.py` zatrzymuje się w `render_store.py --check` na dawnym selektorze `product-card`; `check_render_eol.py` dziedziczy ten sam błąd. `check_publication.py` oczekuje innego historycznego układu. `check_store_composition.cjs` oczekuje kuriera zamiast wdrożonego Paczkomatu. `configurator-journey.cjs` i `inpost-mock-ui.cjs` mają nieaktualne fixture'y routingu/UI. Nie wyłączono tych kontroli i nie deklaruje się pełnego PASS wydania. Nowy test UI wykonuje rzeczywisty, aktualny kontroler. Wszystkie sześć powyższych niepowodzeń odtworzono również na niezmienionej bazie ce3d214 w osobnym worktree; nie zostały wprowadzone tą poprawką.

Nie wykonano E2E z prawdziwym Stripe Sandbox ani płatności Live. Lokalny pakiet `scripts/build_checkout_patch.py` zawiera jedynie trzy runtime pliki i przed/po SHA-256; jest do przeglądu, nie stanowi zgody na wdrożenie.

## Ponowny test i publikacja

Najpierw zakończyć przegląd i uruchomić odizolowany Sandbox z kopią aktualnego wydania, oddzielną bazą i kluczem testowym. Sprawdzić tworzenie sesji kluczem restricted z wymaganymi uprawnieniami, prawdziwy redirect, odmowę, sukces, powrót, webhooki i wygaszenie. Nie używać danych ani klucza Live. Powtórzyć scenariusze tabeli oraz sprawdzić wariant z potwierdzaniem terminu i zgodą na dokumenty.

Dopiero po akceptacji właściciela można planować publikację: zweryfikować hashe bazowe trzech plików, zachować ich backup oraz obecny fingerprint wydania, uwzględnić istniejącą bramkę `approvedReleaseSha256`, wykonać atomową aktualizację sprawdzonym procesem. Nie wdrażać pełnego starego checkoutu repozytorium ani zmieniać bazy. Rollback obejmuje wyłącznie pliki i odpowiedni fingerprint, nigdy odtwarzanie bazy ani zwiększanie stanów. Niniejsza praca niczego nie publikuje.

Na poprawionym Sandbox: otworzyć podany adres ścieżki, skonfigurować 1 VASE dual, wybrać testowy punkt, potwierdzić aktualne podsumowanie i kliknąć płatność 68,49 zł. Po komunikacie o zakończonej próbie ponownie potwierdzić podsumowanie i świadomie rozpocząć nową. Po niepewnym wyniku użyć sprawdzenia tej samej próby. Dla `paid`, `pending`, `review` nie rozpoczynać kolejnej płatności.
