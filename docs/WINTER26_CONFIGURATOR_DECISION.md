# WINTER 26 — kompozycja i decyzja o płatnościach

**Decyzja dla Pracowni Form:** udostępnić do odbioru konfigurator jako część katalogu. Do sprzedaży zestawów z indywidualnym składem i wspólnym stanem wybrać **Checkout Sessions tworzone na serwerze**. Zachować Payment Links dla gotowych, jednoznacznych SKU z osobnym zapasem. [Odbiór Sandbox #16](https://github.com/pracowniarachunkowosci-debug/form/pull/16) potwierdził jedną stałą pozycję + kuriera, nie zamówienia komponowane. W #17 nie tworzono kont, sesji, rezerwacji, linków ani płatności.

## Co klient może zrobić teraz

Z katalogu prowadzą trzy wejścia do **jednej** strony Kwartetu: [4](../winter-zestaw-4.html?size=4#kompozycja), [6](../winter-zestaw-4.html?size=6#kompozycja) i [8](../winter-zestaw-4.html?size=8#kompozycja). Dotychczasowy adres działa bez parametrów (4). [Duet](../winter-zestaw-2.html) pozostaje zapowiedzią. W każdym miejscu można zmienić model, a po zatwierdzeniu palety — kolor. Zmiana modelu czyści kolor wyłącznie tej pozycji. Powiększenie zestawu zachowuje wybory; zmniejszenie wymaga potwierdzenia, jeśli odrzuci wybrane pozycje. Escape zachowuje wybory. Wyzerowanie również wymaga potwierdzenia. Podsumowanie grupuje identyczne pozycje; poszczególne sztuki nadal edytuje się osobno.

Podsumowanie liczy osobno miejsca z modelem i miejsca z dostępnym kolorem. Cztery wybrane modele bez potwierdzonej palety dają „Modele: 4/4 · Kolory: 0/4”. Kompozycja jest kompletna dopiero po wybraniu dostępnego koloru dla każdego modelu. Kompozycja jest przechowywana wyłącznie w pamięci otwartej strony; odświeżenie ją usuwa. „Powiadom mnie o przedsprzedaży” prowadzi na listę informacyjną, nie przesyła składu ani nie rezerwuje egzemplarzy. Nie ma współdzielonego stanu między klientami ani aktywnej sprzedaży. Modelowe miniatury są materiałami koncepcyjnymi i nie dokumentują gotowego SKU; żadnego barwienia zdjęć.

## Jedno źródło danych

[Rejestr](../data/winter26-products.json) → generator → tylko zatwierdzone dane w statycznym HTML. Lista modeli nie jest kopiowana do JS. Do zmiany palety/stanu trzeba odbudować katalog i paczkę; to migawka, **nie system rezerwacji**.

| Pole w rejestrze | Zasada |
|---|---|
| `products[].id`, `name`, `family`, `photos` | Model i jego ilustracje; nie są handlowym SKU. |
| `configuration.colors[]` | Stabilne `id`, nazwa `label`, rzeczywisty kod próbnika `hex`, `approved`. Obecnie pusta lista. Kolor bez potwierdzenia nie daje próbnika. |
| `products[].variants[]` | Przypisanie do modelu przez zagnieżdżenie (jego `id` = modelId). `colorId`, `sku`, `stock`, `grossGrosz` (grosze brutto, PLN), `available`, `status` = draft/approved, `photoAsset`. Pary model–kolor i SKU nie mogą się powtarzać. Brak produktu handlowego = pusta tablica; nie tworzyć fikcyjnych SKU. `null` oznacza brak wartości. |
| Zdjęcie wariantu | Klucz w mapie mediów i w zdjęciach danego modelu; `kind: fotografia`, ten sam `colorId`, zatwierdzony fizyczny kadr i opis. Bez zdjęcia po wybraniu próbnika jest neutralny komunikat. Wycinki i wizualizacje nie zastępują zdjęcia koloru. |
| `configuration.sizes[]` | Rozmiary 4/6/8. Opcjonalna stała kwota brutto dla danego rozmiaru `grossGrosz` + `priceApproved`; niezależnie `shippingGrosz` + `shippingApproved`. Bez zatwierdzenia kwot UI nie wyświetla ceny ani nie zakłada darmowej wysyłki. Cena zależna od składu wymaga odrębnej reguły. |

Przykład częściowej kompozycji w pamięci (bez danych handlowych):

```json
{"size":4,"slots":[{"model":"helix","color":null},{"model":"knitted-star","color":null},{"model":"knitted-star","color":null},{"model":"full-soft","color":null}]}
```

Wprowadzenie wariantów: zatwierdzić próbkę i wariant powiązane ID, przypisać fizyczny SKU/stan/cenę oraz zdjęcie, odbudować i obejrzeć kartę z próbnika. Zatwierdzony wariant z zerowym stanem można obejrzeć na pojedynczej karcie, ale nie użyć do ukończenia pozycji zestawu. Limit ilości dotyczy danego SKU w całym bieżącym składzie. Dodanie SKU do JSON **nie włączy zakupu**: ogólny link modelu ani link dawnego Kwartetu nie mogą pobierać opłaty za wybrany skład. Bramy #13 dla niezależnego stałego produktu pozostają testowane.

## Stripe — porównanie wariantów

| Kryterium | A — Payment Link za rozmiar | B — Checkout Session dla zamówienia |
|---|---|---|
| Cena i skład | Link ma z góry ustaloną cenę. Model działa tylko wtedy, gdy **każdy** dopuszczony skład rozmiaru ma identyczną cenę. Parametr URL nie definiuje ceny ani pozycji. Trzy linki nie zapiszą kombinacji. | Przeglądarka przesyła identyfikatory i kolejność; serwer sam waliduje dozwolone modele/kolory, rozmiar, stan, ceny, regułę rabatu, VAT i ustaloną metodę dostawy. Stripe dostaje zatwierdzone pozycje/kwoty z serwera. |
| Odzyskanie zamówienia | `client_reference_id` jest edytowalnym parametrem do uzgadniania. Może być pominięty (np. przy nieprawidłowej wartości). Wymaga uprzednio zapisanego, niezmiennego składu w prywatnej ewidencji. Krótki niepoufny ID, nie dane klienta, lista wyborów ani dowód uprawnienia. Custom fields służą zbieraniu odpowiedzi, nie zapewniają integralności składu ani magazynu. | Trwałe zamówienie i pozycje na serwerze. Referencja zamówienia w Session i PaymentIntent (ustawić oba jawnie); trwałe powiązanie order ↔ session ↔ payment. Operator znajduje ID w Stripe i pełny skład w ewidencji. |
| Ostatnia sztuka / dwa okna | Limit ukończeń linku nie odlicza wspólnych SKU zestawu i singli. Wysyłka wyłącznie po ręcznej rezerwacji **przed** wydaniem prywatnego linku, uzgodnieniu kwoty, ID i składu oraz kontroli powtórzeń. Nieprawidłowy/brakujący ID = brak wysyłki. | Jedna atomowa rezerwacja SKU wszystkich pozycji. W dwóch równoczesnych zamówieniach ostatnią sztukę może otrzymać tylko jedno. Każdy kanał (także single) musi korzystać z tej samej rezerwacji lub mieć odseparowany zapas. |
| Koszt i obsługa | Niski nakład dla **stałego** produktu. Ręczne sprawdzanie każdej indywidualnej konfiguracji rośnie wraz z liczbą zamówień. Bez prywatnej ewidencji nie da się zrekonstruować wyborów po płatności. | Większy jednorazowy koszt implementacji i obsługi webhooków, kopii i alertów. Bez dodatkowego abonamentu SaaS, **jeśli** kupiony hosting wystarczy do utrzymania endpointu i trwałej transakcyjnej bazy. |

**Granica wyboru:** już wymóg samoobsługowego zakupu dwóch zestawów o różnym składzie, korzystających z tego samego ostatniego SKU, przekracza bezpieczne możliwości samych Payment Links. Przy cenie zależnej od wyboru link o stałej cenie odpada również z powodów cenowych. Nie generować oddzielnego linku dla każdej kombinacji. Dla małej serii zamiast wdrażać backend można nadal sprzedawać osobno potwierdzone **gotowe** zestawy; nie podpinać ich linków pod ten konfigurator.

[Parametry Payment Link](https://docs.stripe.com/payment-links/url-parameters) i [ograniczenia pól](https://docs.stripe.com/payment-links/customize) opisują możliwości wariantu A. [Tworzenie Session](https://docs.stripe.com/api/checkout/sessions/create) i [realizacja po zapłacie](https://docs.stripe.com/checkout/fulfillment) są podstawą wariantu B.

## Minimalny plan integracji B — poza tym PR

1. Potwierdzić na tym planie LH: wspierane PHP, HTTPS, wyjście do Stripe, możliwość weryfikacji podpisu webhooka na surowym body, sekrety poza public_html, transakcyjną bazę (np. MySQL/InnoDB), kopie, możliwość odzyskania danych, zadanie okresowe i monitoring. Statyczna strona nie musi zmieniać hostingu. Jeśli LH nie wystarczy, porównać koszt małego osobnego endpointu z trwałą bazą; nie kupować z góry usługi.
2. Serwer akceptuje wyłącznie identyfikatory, rozmiar i kolejność, z limitem żądań i ochroną przed masowym blokowaniem zapasu. Nie ufa cenie, SKU ani kwocie z klienta. W jednej transakcji agreguje powtórzenia, blokuje SKU w stabilnej kolejności, sprawdza wolny zapas i zapisuje **wszystkie lub żadne** rezerwacje. Utrwala snapshot pozycji z numerem miejsca, cenami brutto, polityką rabatu/dostawy, datą i terminem rezerwacji. Zastosować unikalny klucz żądania, aby ponowne kliknięcie nie utworzyło zamówienia po raz drugi.
3. Po zatwierdzeniu transakcji tworzy Session z [idempotency key](https://docs.stripe.com/api/idempotent_requests) dla zamówienia/próby; utrwala zwrócone ID przed przekierowaniem. Płatność jednorazowa PLN, zatwierdzona metoda InPost, telefon i adres. Ostateczna metoda dostawy, cena i ewentualny próg darmowej wysyłki pozostają decyzją właściciela. Dla stałej ceny użyć pozycji rozmiaru z niezmiennym składem w zamówieniu. Błąd sieci przy tworzeniu: wznowienie z tym samym kluczem, sprawdzenie stanu istniejącej sesji, nie automatyczne tworzenie drugiej.
4. [Podpisany webhook](https://docs.stripe.com/webhooks/signature), unikalne event ID i przejścia statusów odporne na zmianę kolejności i duplikaty. Uzgodnić session/order, PaymentIntent, PLN, kwotę produktu/dostawy i ostateczny status. `completed` bez zapłaty i sam powrót użytkownika nie oznaczają realizacji; obsłużyć m.in. sukces/odmowę asynchroniczną BLIK. Tylko raz zmienić rezerwację w wydanie. Historia płatności i skład pozostają do porównania przed nadaniem InPost.
5. [Wygaśnięcie/porzucenie](https://docs.stripe.com/payments/checkout/managing-limited-inventory): uzgodnić termin rezerwacji z wygaśnięciem Session. Nie zwalniać zapasu wyłącznie dlatego, że minął lokalny timer, gdy płatność nadal oczekuje. Po definitywnym wyniku zwolnić raz; cyklicznie uzgadniać brakujące webhooki. Spóźniona zapłata po utracie zapasu lub rozbieżność kwoty → manualna kolejka, brak wysyłki, uzgodnienie/zwrot. Zwrot pieniędzy nie przywraca zwróconej fizycznej bombki na stan bez kontroli.
6. **Sandbox przed Live:** próba manipulacji kwotą/ID/rozmiarem, brak koloru, duplikaty, ostatnia sztuka singiel vs zestaw z dwóch przeglądarek, utrata odpowiedzi po utworzeniu Session, sukces/odmowa karty i BLIK, porzucenie/timeout, ponowiony lub opóźniony webhook, zwrot pełny/częściowy oraz zgodność rzeczywistego składu i danych dostawy w ewidencji. Bez tych wyników i odrębnej zgody nie uruchamiać Live.

## Odbiór interfejsu

[Desktop](previews/atelier-desktop.jpg) · [390 px](previews/atelier-mobile390.jpg) · [320 px](previews/atelier-mobile320.jpg). Sprawdzono w Chrome brak poziomego przewijania, natywne radia strzałkami i spacją, przełączanie rozmiarów, powtórzenia/edycję, Escape w oknie utraty wyborów, potwierdzenie zmniejszenia i reset. W prywatnej próbie (poza wydaniem) rzeczywisty UI osiągnął 4/4, zablokował drugą sztukę wyczerpanego SKU, obsłużył dwie sztuki innego SKU i pokazał cenę/zdjęcie wybranej próbki oraz komunikat przy braku fotografii. Przypadki 6/6 i 8/8, inne SKU, puste i nadmiarowe wybory pokrywają testy reguł. Testy generatora LF/CRLF, starej bramki, cookies, niezmienionego hero i referencji należą do builda #18.

### Korekta R02 względem PR #18

| Szerokość w Chrome | Kwartet z PR #18 | Konfigurator R02 |
|---|---|---|
| 1440 px | [Karta zestawu](previews/quartet-base-1440.jpg) | [Edycja i podsumowanie](previews/atelier-desktop.jpg) |
| 390 px | [Karta zestawu](previews/quartet-base-390.jpg) | [Miejsca i edytor](previews/atelier-mobile390.jpg) · [Podsumowanie](previews/atelier-summary390.jpg) |
| 320 px | [Karta zestawu](previews/quartet-base-320.jpg) | [Podsumowanie i nieaktywna nawigacja](previews/atelier-mobile320.jpg) |

Pozostaje tło karty z PR #18. Panel edycji odsłania to samo tło, sloty i podsumowanie mają wspólną porcelanę (#faf8f3), wybrany model i fokus klawiatury — grafit (#25231f). W Chrome sprawdzono obramowanie po najechaniu, zaznaczenie, widoczny fokus i nieaktywny przycisk ostatniej pozycji. Przy wszystkich trzech szerokościach zawartość obu stron mieści się w obszarze przewijania bez przewijania w poziomie. W galerii HELIX sprawdzono zmianę ujęcia, otwarcie drugiego kadru Enterem i powrót fokusu do powiększanego kadru po Escape.

## Decyzje właściciela przed sprzedażą

- Które fizyczne kolory są gotowe **dla każdego modelu**, z jaką nazwą, próbnikiem, zdjęciem i SKU?
- Ile gotowych sztuk jest dostępnych per SKU, czy dopuszczalne są powtórzenia do wysokości stanu i czy single dzielą zapas z zestawami?
- Jakie są ceny brutto singli i czy 4/6/8 mają stałą cenę, rabat czy cenę zależną od składu?
- Jakie rzeczywiste opakowanie i gabaryt, koszt dostawy oraz czas nadania obowiązują dla każdego rozmiaru?
- Czy zaczynamy od gotowych SKU z wydzielonym zapasem, czy zlecamy etap B dla indywidualnych kompozycji? Odbiór LH, dokumentów i Brevo z [#18](https://github.com/pracowniarachunkowosci-debug/form/pull/18) pozostaje oddzielny.
