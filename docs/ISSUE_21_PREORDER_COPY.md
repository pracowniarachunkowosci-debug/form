# Issue #21 — WINTER 26: komunikacja przedsprzedaży

Dokument akceptacyjny dla tekstów i zasad wdrażanych w draft PR. Nie aktywuje zakupów, Stripe Live ani publikacji.

## Proponowana komunikacja publiczna

| Miejsce | Tekst po zmianie |
|---|---|
| Etykieta kolekcji | `WINTER 26 — przedsprzedaż` |
| Stan katalogu | `Przedsprzedaż wkrótce` |
| Główne CTA przy nieaktywnym zakupie | `Powiadom mnie o przedsprzedaży` |
| CTA po późniejszym uruchomieniu zakupu | `Zamów w przedsprzedaży` |
| Termin realizacji | `Nadawanie zamówień planujemy rozpocząć 23 listopada 2026 r.` |
| Sposób wysyłki | `Przesyłki planujemy realizować przez InPost. Ostateczna metoda zostanie potwierdzona przed aktywacją zakupów.` |
| Zastrzeżenie terminu | `Data nadania nie jest gwarantowaną datą doręczenia. Termin doręczenia zależy od przewoźnika.` |

Termin 23 listopada 2026 r. oznacza planowany start nadań przez InPost, a nie obiecaną datę dostawy.

## Stan wdrożony teraz

- Przedsprzedaż jest komunikowana jako przygotowywana, ale zakupy pozostają nieaktywne.
- Zapis na listę informacyjną nie jest zamówieniem ani rezerwacją produktu.
- Karty i szczegóły produktów nie używają eksponowanych określeń „wizualizacja poglądowa” ani „druk 3D”. Zachowują oznaczenie kadru koncepcyjnego oraz informację, że materiał, warianty i fotografie wymagają potwierdzenia przed zakupem.
- Konfigurator pomaga zbudować kompozycję 4/6/8, ale nie rezerwuje produktów i nie tworzy zamówienia.
- Nie dodano cen, kolorów ani stanów, ponieważ nie zostały jeszcze zatwierdzone.
- Nie zmieniono typografii, kolorów, zdjęć, hero ani layoutu.

## Warunek aktywacji zakupów

Przed uruchomieniem checkoutu trzeba zatwierdzić dla każdego SKU: model i wariant, kolor, materiał, wymiary, fotografię, SKU, stan, cenę brutto, koszt wysyłki, dane GPSR, regulamin sprzedaży, zwroty i reklamacje. Dla zestawów trzeba dodatkowo potwierdzić skład i odrębny zapas.

Po aktywacji termin nadania, przewoźnik, metoda dostawy, koszt wysyłki, suma i kluczowe warunki muszą być widoczne bezpośrednio przed zapłatą. Na tym etapie potwierdzony jest kierunek InPost, ale nie przesądzamy jeszcze o Kurierze, Paczkomatach, cenie ani progu darmowej wysyłki.

Wszystkie flagi akceptacji pozostają `false`, linki Stripe pozostają puste, a Stripe Live nie jest aktywny.

## Wymagania techniczne dla przyszłego checkoutu

Obsługa kolorów oraz zestawów 4/6/8 ma zostać wykonana później przez serwerowe Stripe Checkout Sessions, bez Payment Links generowanych dla każdej kombinacji. Przed implementacją trzeba:

1. utrwalać zatwierdzone warianty `modelId + colorId + SKU + cena + stan + fotografia` oraz skład zestawu w jednej ewidencji;
2. przyjmować z przeglądarki wyłącznie identyfikatory, rozmiar i kolejność miejsc, a ceny, dostępność, rabaty, VAT i dostawę wyliczać ponownie na serwerze;
3. atomowo rezerwować wszystkie SKU zestawu, agregować powtórzenia i chronić ponowienia żądania kluczem idempotencji;
4. tworzyć Session z serwera z trwałym `orderId`, `client_reference_id` i powiązaniem do PaymentIntent, bez zaufania do kwot z klienta;
5. obsłużyć podpisany webhook, duplikaty i zmianę kolejności zdarzeń, zwolnienie rezerwacji po wygaśnięciu oraz ręczną kolejkę rozbieżności;
6. pokazać przed zapłatą dokładny skład, warianty kolorystyczne, ilość, cenę, metodę i koszt dostawy, sumę oraz planowany termin nadania;
7. przejść Sandbox dla manipulacji identyfikatorami i kwotami, dwóch równoległych klientów, ostatniej sztuki, BLIK, timeoutów, powtórzonych webhooków i zwrotów.

Do tego czasu konfigurator pozostaje prezentacyjny, bez backendu, sesji, rezerwacji i płatności.

## Akceptacja właściciela

Do potwierdzenia pozostają: brzmienie etykiety i CTA, planowany termin 23.11.2026, ostateczna metoda dostawy w ramach InPost, ceny, ewentualny próg darmowej wysyłki, zastrzeżenie że nadanie nie jest doręczeniem oraz komplet danych handlowych i prawnych wymaganych przed aktywacją zakupów.
