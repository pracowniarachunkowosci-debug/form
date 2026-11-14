# WINTER 26 — jak włączyć wybór automatu Paczkomat® na LH

**Co dostaje klient:** przy 1–5 ozdobach w całym koszyku kurier na polski adres kosztuje 20,49 zł brutto, a odbiór w automacie 18,49 zł. Od 6 ozdób obie metody są bez dopłaty. To ceny dla klienta oparte na gabarycie B w [cenniku detalicznym InPost Szybkie Nadania](https://inpost.pl/cenniki). Do ręcznego nadania wybierz gabaryt rzeczywistego kartonu. Integracja nie kupuje etykiety i nie zleca podjazdu.

## Jednorazowo — właściciel i lokalny Codex

1. Zaloguj się do [Managera Paczek](https://manager.paczkomaty.pl/) (na próbę do [osobnego panelu Sandbox](https://sandbox-manager.paczkomaty.pl/)). W **Moje konto → Dane** uzupełnij dane firmy, adres i dane do faktury. Przejdź do **Moje konto → API**.
2. W sekcji **Geowidget** wygeneruj **publiczny token mapy** dla hosta sklepu. Podaj host faktycznie widoczny w pasku adresu (bez ścieżki); dla testów użyj rzeczywistego hosta HTTPS stagingu i tokenu Sandbox. Dla wersji publicznej wybierz domenę docelową i token produkcyjny.
3. W sekcji **API ShipX** wygeneruj lub wybierz **token z dostępem do API Points**. To drugi, prywatny klucz: serwer sprawdzi nim status, identyfikator i adres automatu. InPost w [instrukcji generowania](https://inpost.pl/sites/default/files/pdf/instrukcja-konfiguracji-api-shipx.pdf) opisuje dostęp do samych usług paczkomatowych bez numeru umowy kurierskiej. Nie kupuj pakietu dla samej mapy. Jeśli na Twoim koncie brakuje uprawnień lub tej sekcji, skontaktuj się z InPost przez panel. Nie zastępuj tokenu Points tokenem mapy.
4. Lokalny operator umieszcza oba klucze w konfiguracji właściwego środowiska LH poza publicznym katalogiem, jak w [instrukcji checkoutu](WINTER26_CHECKOUT.md). **Nazwy pól**: `inpost_points_token` — prywatny token odczytu katalogu punktów; `inpost_geowidget_token` — publiczny token mapy. Użyj prawdziwej pary z danego środowiska, nie publikuj jej w repozytorium ani w zadaniu. Cennik sklepu pochodzi z rejestru cen; dawny prywatny parametr ceny kuriera nie zmienia kwoty.
5. Na telefonie wykonaj próby poniżej. Następnie powtórz konfigurację na właściwej domenie z produkcyjnymi tokenami. Klient może wpisać znany kod automatu bez ładowania mapy, ale również w tym przypadku serwer musi potwierdzić punkt. Bez dostępu do Points pozostaje kurier. Przy błędzie InPost koszyk nie przechodzi sam na droższą dostawę.

## Odbiór do piątku na rzeczywistym LH i Stripe Sandbox

| Próba | Wynik do sprawdzenia |
| --- | --- |
| 1 ozdoba, kurier | 70,49 zł; w Stripe jest polski adres odbiorcy. |
| 1 ozdoba, Paczkomat® | 68,49 zł. Na telefonie wybierz automat na mapie. Zobacz kod i adres przed płatnością; po opłaceniu muszą być takie same w zamówieniu. Jest imię i nazwisko, telefon i e-mail do nadania. |
| Zmiana wyboru | Wybierz inny automat, a potem przełącz na kuriera. Nie może pozostać stary punkt ani stara cena. Sprawdź również ręczne wprowadzenie identyfikatora i odrzucenie błędnego kodu. |
| 4 + 1 ozdoba vs 4 + 2 ozdoby | Pięć ozdób w dwóch kompozycjach: 220,49 zł kurierem lub 218,49 zł do automatu. Sześć ozdób w dwóch kompozycjach: 234 zł w obu metodach, z zachowaniem wybranego automatu. Sam zestaw 6: 220 zł. |
| Awaria/kasowanie wyboru | Brak potwierdzonego punktu uniemożliwia rozpoczęcie nowej płatności za dostawę do automatu i nie rezerwuje zapasu. Kuriera można wybrać jawnie. |
| Karta / BLIK | Przejdź po jednej rzeczywistej płatności testowej każdą metodą, w tym jedną z odbiorem w automacie. Potwierdź podpisany webhook, status opłacenia i zapas, a nie tylko ekran sukcesu. |

## Jak nadać pierwsze zamówienie

Po potwierdzonej płatności otwórz zamówienie w Stripe Dashboard. Sprawdź numer zamówienia, skład i ilości, kwotę i metodę dostawy. Parametry zamówienia zawierają `delivery_method` (kurier: `courier`, automat: `locker`), a przy automacie również `pickup_point` (kod) oraz `pickup_address` (adres). Te same dane zostają zapisane w prywatnym zamówieniu na LH; adres automatu nie jest adresem klienta. Dane kontaktowe odbiorcy odczytasz w Checkout. Następnie w [Szybkich Nadaniach](https://inpost.pl/SzybkieNadania/) wybierz doręczenie do automatu albo pod adres i właściwy gabaryt. Nie wysyłaj na podstawie samego przekierowania po płatności.

Dokumentacja InPost: [mapa Geowidget PL](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/pages/50069505) · [API Points — generowanie dostępów, tryb testowy i produkcyjny](https://dokumentacja-inpost.atlassian.net/wiki/spaces/PL/pages/18153493).
