# Kontrolowany odbiór listy premierowej — plan, niewykonany

03.11.2026. **Wymaga osobnej zgody właściciela przed pierwszym POST lub wysłaniem wiadomości.** Sprawdzenie HTML/HTTP 200 nie jest testem integracyjnym. Istniejący formularz, jego endpoint, pola i zgoda nie zostały zastąpione makietą.

## Zakres zgody do ustalenia

Właściciel wskazuje dwa kontrolowane adresy odbiorców (najlepiej różni operatorzy), formularz/listę Brevo, adres nadawcy, origin testu, termin i wykonawcę. Proponowany limit: po jednym nowym zapisie na adres, po jednym ponowieniu już potwierdzonego zapisu, maksymalnie jedna wiadomość testowa po DOI na adres. Nadmiarowe wiadomości/ponowienia wymagają zatrzymania i diagnozy. Brak wysyłki do realnej bazy klientów. Test kontaktu: jedna wiadomość na `kontakt@pracowniaform.com` i odpowiedź do kontrolowanego nadawcy. Nie używać losowych adresów ani skrzynek osób trzecich.

Odczyt konfiguracji (po zapewnieniu dostępu właściciela) powinien poprzedzać wysyłkę: ustalić docelową listę, tryb DOI, nadawcę/Reply-To, szablon potwierdzenia, przekierowania, wypisanie i automatyzacje. Jeżeli zapis uruchamia nieuzgodnioną kampanię — STOP, nie wykonywać testu. Bez samodzielnych zmian ustawień konta. [Dokumentacja formularzy Brevo](https://help.brevo.com/hc/en-us/sections/202171729-Forms) obejmuje konfigurację DOI; [wypisanie](https://help.brevo.com/hc/en-us/articles/208772629-Customize-an-unsubscribe-page-to-integrate-into-your-email-campaigns) jest odrębnym etapem od potwierdzenia zapisu.

## Scenariusze i kryteria odbioru

| Krok | Oczekiwany wynik / dowód |
|---|---|
| Bez zgody / błędny e-mail | Brak poprawnego zapisu, widoczny komunikat walidacyjny; sprawdzone lokalnie bez POST |
| Nowy e-mail + zgoda | Potwierdzenie przyjęcia formularza, dokładnie jeden kontakt/pending DOI zgodnie z konfiguracją; informacja, że trzeba potwierdzić zapis |
| Przed kliknięciem DOI | Brak dopuszczenia do marketingowej wysyłki; wiadomość potwierdzająca trafia na kontrolowany adres |
| Doręczenie DOI | Nadawca i Reply-To poprawne, temat i tekst bez sugerowania zamówienia, działający HTTPS link; zapisać czas, folder inbox/spam, Message-ID w prywatnym protokole |
| Potwierdzenie | Kliknięcie raz aktywuje zgodę/listę; poprawna docelowa strona potwierdzenia; ponowne kliknięcie nie dubluje kontaktu |
| Duplikat zapisu | Brak duplikacji kontaktu i nieuzgodnionych wiadomości; oczekiwany stan potwierdzony w panelu |
| Jedna uzgodniona wiadomość | Dostarczona do obu testowych adresów; poprawne linki, brak produkcyjnej kampanii do całej bazy |
| Wypisanie | Odnośnik w wiadomości dostępny, stan blokady wysyłki widoczny w panelu; następna kwalifikacja segmentu wyklucza kontakt (bez wysyłania kolejnej kampanii) |
| Uwierzytelnienie | Z nagłówków wiadomości odczytać `Authentication-Results`, SPF, DKIM (`d=`, `s=`) i zgodność domen z DMARC; brak rekordu DMARC nie oznacza automatycznie testu PASS |
| Skrzynka kontaktowa | Wiadomość przyjęta i odczytana, odpowiedź dochodzi; potwierdzony opiekun skrzynki i obsługa próśb o wypisanie |
| Docelowy host | Po zatwierdzonym przełączeniu ponowić minimalny uzgodniony test z apex HTTPS; lokalny origin nie potwierdza ograniczeń domeny formularza |

Proponowany próg diagnostyczny: brak DOI po 10 minutach → sprawdzić spam i logi, nie ponawiać automatycznie. To próg testu, nie SLA dostawcy. Błędny odbiorca/lista, zgoda aktywna przed DOI, niedziałające wypisanie lub błąd doręczania → **NO-GO**. Stan kontaktów testowych po odbiorze (blokada/usunięcie zgodnie z retencją) uzgodnić oddzielnie; nie kasować realnych danych.

## Wynik obecny i protokół

PASS wyłącznie dla konfiguracji w kodzie, wymaganych pól, linków, lokalnej walidacji i dostępności publicznego endpointu. **DOI, wypisanie, doręczenie i skrzynka kontaktowa: NOT RUN.** Publiczny odczyt MX 03.11.2026 potwierdził `mx1/2/3.mail.ovh.net`; SPF `include:mx.ovh.com -all`. Nie potwierdza to istnienia konkretnego adresu. Nie wykonano prób SMTP `VRFY/RCPT`, logowania do poczty ani wysyłki.

Protokół do wypełnienia po zgodzie: commit, origin, data/godzina, osoba zatwierdzająca, identyfikatory T1/T2 zamiast e-maili, status każdego kroku PASS/FAIL, wynik nagłówków (bez tokenów), decyzja GO/NO-GO. Pełne adresy, linki DOI/wypisania i zrzuty kont nie trafiają do publicznego repo.
