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
| Sposób wysyłki | `Przesyłki realizujemy przez InPost Kurier na adres w Polsce.` |
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

Po aktywacji termin nadania, przewoźnik, koszt wysyłki, suma i kluczowe warunki muszą być widoczne bezpośrednio przed zapłatą. Dla tej wersji przewidziany jest InPost Kurier na adres w Polsce; Paczkomaty nie są obecnie obsługiwane.

Wszystkie flagi akceptacji pozostają `false`, linki Stripe pozostają puste, a Stripe Live nie jest aktywny.

## Akceptacja właściciela

Do potwierdzenia pozostają: brzmienie etykiety i CTA, planowany termin 23.11.2026, sposób wysyłki InPost Kurier na adres w Polsce, zastrzeżenie że nadanie nie jest doręczeniem oraz komplet danych handlowych i prawnych wymaganych przed aktywacją zakupów.
