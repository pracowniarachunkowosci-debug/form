# Dane produktów i funkcja odstąpienia — projekt techniczny

## Model wariantu

Źródło: `data/winter-26.json`. `null` oznacza brak zatwierdzonych danych, nigdy cenę 0, zerowy stan ani termin natychmiastowy. Numery 01–04 są numeracją redakcyjną, nie SKU. `id` identyfikuje kartę w interfejsie, nie zastępuje identyfikatora produktu/partii wymaganego przez GPSR.

| Pole | Docelowe znaczenie |
| --- | --- |
| `sku` | Unikalny identyfikator konkretnego modelu/koloru/wariantu; do nadania |
| `color`, `pricePLN` | Zatwierdzona nazwa wariantu i cena brutto w PLN |
| `availability` | `in_stock`, `made_to_order`, `unavailable` |
| `stock` | Rzeczywisty dostępny stan danego SKU; nie globalny stan modelu |
| `dispatchDaysInStock` | Osobny zatwierdzony czas wysyłki z magazynu |
| `dispatchDaysMadeToOrder` | Czas wytworzenia i przygotowania do wysyłki wariantu na zamówienie |
| `photo`, `photoAlt`, `material` | Zweryfikowane zdjęcie, opis alternatywny i materiał |
| `manufacturer`, `safety` | Miejsca na rzeczywiste dane producenta, kontakt, ostrzeżenia i instrukcje; format do ustalenia z dokumentacją produktu |

Aktualnie cztery modele mają po jednym pustym szkielecie wariantu i `unavailable`. Nie są to gotowe rekordy magazynowe. Mały stan gotowy i druk standardowych wariantów są kierunkiem przyszłej obsługi, bez wymyślonych nakładów. Renderer review pokazuje jawne placeholdery, nie wybór czy rezerwację SKU. Zestawy 2/4 są wyłącznie kartami projektu — bez konfiguratora zamówień.

Przed uruchomieniem trzeba doprecyzować jednostki i przedziały terminów (dni robocze/kalendarzowe), oddzielić dostawę przewoźnika oraz zdecydować o wspólnej lub dzielonej wysyłce. `stock=0` nie może samodzielnie włączać druku na zamówienie: potrzeba zatwierdzonej zdolności produkcji. Rezerwacje zapasu, walidacja ceny i idempotentne zamówienia należą do przyszłego backendu. Sam JSON nie stanowi jego implementacji.

## Elektroniczne odstąpienie

W `formularz-odstapienia.html` dostępne są dobrowolny wzór do wydruku i lokalne demo: rozpoczęcie → dane → podsumowanie → potwierdzenie → jednoznaczny komunikat „nic nie wysłano”. Można wrócić i poprawić dane oraz wyczyścić demo. Bez logowania, uzasadnienia, uploadu i checkboxa zgody na przetwarzanie niezbędne do obsługi odstąpienia. Imię, identyfikacja umowy i adres potwierdzenia odpowiadają kierunkowi art. 11a. Dane istnieją tylko w DOM/pamięci karty; po opuszczeniu/odświeżeniu znikają. Brak endpointu, poczty i zapisu w localStorage.

### Proponowany kontrakt po odrębnej akceptacji

1. Widoczny link do funkcji przez cały okres prawa odstąpienia, także bez konta; podpis przycisku zgodny z zatwierdzoną implementacją krajową. Nie utrudniać alternatywnych kanałów.
2. Krok danych: imię i nazwisko, numer lub opis umowy, adres elektroniczny do trwałego potwierdzenia. Uwzględnić możliwość wskazania zakresu odstąpienia dla zamówień wieloproduktowych.
3. Podsumowanie oświadczenia i osobny przycisk potwierdzenia; możliwość korekty. Walidacja zrozumiała i dostępna klawiaturą/czytnikiem.
4. `POST /api/withdrawals` dopiero po potwierdzeniu: `consumerName`, `contractReference`, `confirmationAddress`, `scope`, `statementVersion`, `idempotencyKey`. Serwer przyjmuje zgłoszenie bez ujawniania danych zamówienia osobom postronnym; szczegóły dalszej weryfikacji nie mogą uniemożliwiać terminowego oświadczenia.
5. Serwer ustala datę/godzinę UTC i prezentuje lokalną strefę; atomowo zachowuje treść, identyfikator i zdarzenie do kolejki potwierdzeń. Ponowienie z tym samym kluczem zwraca ten sam wynik. Walidacja po stronie serwera, limity żądań i ochrona nadużyć bez zbędnych barier konsumenckich.
6. Niezwłoczne potwierdzenie na trwałym nośniku (np. e-mail) zawierające pełną treść, datę i godzinę. Sam toast/ekran nie wystarcza. Kolejka z ponawianiem, monitoring niedoręczeń i ręczny proces naprawczy; rozdzielić przyjęcie oświadczenia od dostarczenia e-maila. Zachować dowód obu zdarzeń.
7. Minimalizacja danych, ograniczenia dostępu, szyfrowanie i retencja ustalona z polityką; brak danych osobowych w URL/analityce i zwykłych logach technicznych.

### Kryteria odbioru przyszłego wdrożenia

- Prawidłowe zgłoszenie, nieznany numer/opis umowy, częściowy zakres, korekta, polskie znaki i obsługa klawiaturą.
- Podwójne kliknięcie, ponowienie po utracie sieci, timeout i błąd serwera nie dublują zgłoszenia ani nie pokazują fałszywego sukcesu.
- Potwierdzenie zawiera identyczną treść i serwerowy czas; działa ponawianie po awarii dostawcy poczty, a użytkownik widzi rzeczywisty stan.
- Oświadczenie nie jest blokowane przez brak konta, opcjonalną zgodę marketingową ani obowiązkowe uzasadnienie.
- Recenzja prawnika względem finalnych przepisów krajowych i test bezpieczeństwa endpointu przed uruchomieniem.

Żaden powyższy endpoint ani integracja nie został aktywowany w tym PR. Aktualny test dotyczy wyłącznie lokalnych przejść UI.
