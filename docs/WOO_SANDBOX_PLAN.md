# P24 i InPost — plan integracji testowej, bez aktywacji

02.11.2026. Dokument do kolejnego etapu po lokalnym prototypie. Nie założono kont, nie wpisano kluczy i nie wykonano transakcji ani zlecenia przewozu. Obecny prototyp blokuje płatności, pocztę i żądania zewnętrzne.

## Przelewy24

Wybrać oficjalny [moduł WooCommerce](https://www.przelewy24.pl/do-pobrania/woocommerce) zgodny z docelowymi wersjami WordPress/Woo/PHP i używanym checkoutem. Zweryfikować HPOS oraz częściowe zwroty. Nie zastępować go modułem „P24 przez Stripe”.

P24 opisuje [utworzenie sandboxa](https://www.przelewy24.pl/centrum-pomocy/wsparcie-techniczne-api/jak-zalozyc-srodowisko-testowe) przez panel po rejestracji i akceptacji umowy. **Nie zakładamy konta w ramach tej pracy**; właściciel dostarcza zatwierdzony dostęp testowy albo zatwierdza osobno wymagane formalności. Klucze testowe i produkcyjne przechowywać oddzielnie, poza repo.

Po zgodzie: sandbox i syntetyczny klient, kwota 1 zł oznaczona testowo, brak sprzedaży realnego produktu. Test BLIK/karta/przelew: sukces, odmowa, anulowanie, timeout, zamknięcie przeglądarki po zapłacie, ponowione i spóźnione powiadomienie, kwota/waluta niezgodna z zamówieniem, ostatnia sztuka kupowana równolegle, zwrot pełny i częściowy. Serwer potwierdza płatność zgodnie z [P24 REST](https://developers.przelewy24.pl/); powrót klienta nie jest potwierdzeniem. Przy module testujemy wynik, nie dopisujemy drugiej konkurencyjnej obsługi callbacka.

Localhost nie odbierze callbacka operatora. Pełne E2E wymaga odrębnie zatwierdzonego testowego HTTPS (chroniony staging, z dostępem tylko do potrzebnej trasy callbacka). **Nie uruchomiono tunelu ani stagingu.** Lokalny mock nie jest dowodem integracji z P24. Przed testem upewnić się, że dozwolone endpointy i dane należą do sandboxa; nie przełączać na produkcję po udanym teście.

## InPost

Oficjalna [instrukcja modułu WooCommerce](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/pages/89620481/ENG%2BWooCommerce) rozdziela Production/Sandbox i wymaga właściwych tokenów, ID organizacji oraz tokenu Geowidget. Dla sandboxa podaje osobny Manager Paczek i wirtualne środki. Nie zakładano konta i nie użyto tokenu produkcyjnego.

Po zatwierdzeniu dostępu testowego: wybrać Sandbox, skonfigurować osobny punkt nadania i syntetyczne dane, testową usługę oraz gabaryt. Zweryfikować wybór punktu w checkout, zapis ID punktu w zamówieniu HPOS, brak punktu/nieaktywny punkt, zmianę dostawy, kuriera opcjonalnie, testową etykietę, aktualizację statusu i powtórzenie requestu po timeout. Ponowienie po utworzeniu przesyłki nie może naliczyć drugiej paczki. Testowej etykiety nie przekazujemy do realnego nadania. Zweryfikować jednostki wymiarów i masy; nie wpisywać nieznanych wymiarów realnych produktów jako zatwierdzonych.

## Odbiór i ograniczenia

- Tylko syntetyczne dane; skrzynka testowa lub lokalny mail sink, bez Brevo produkcyjnego.
- Raport ma podawać wersje modułów, środowisko, przypadki zakończone i niewykonane, status magazynu oraz identyfikatory testowe w prywatnych logach bez sekretów.
- Testy MySQL/HPOS, blokad rezerwacji, prawdziwego crona i restore na wybranym serwerze są osobnym obowiązkiem. Playground SQLite potwierdza tylko lokalny prototyp funkcji/wyglądu.
- Zgoda na sandbox nie oznacza zgody na sprzedaż, płatności produkcyjne, DNS ani publikację. PR #5 i działające formularze strony pozostają nietknięte.
