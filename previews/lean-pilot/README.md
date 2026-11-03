# Lokalny projekt pilota — bez sprzedaży

Uruchom w katalogu repo: `python -m http.server 8766 --bind 127.0.0.1`.
Otwórz `http://127.0.0.1:8766/previews/lean-pilot/winter-26.html`.

R04 (HTML jako punkt wyjścia, CSS i zoptymalizowane AVIF/WebP bez zmian) pochodzi z PR #5, commit `f97fcd65f2625dcc4f18aabf65c3a8e467a5a947`. Wspólne style i skrypt są odczytywane z root repo. Dodatki dotyczą wyłącznie pilota: cztery karty zapowiedzi z jednym statusem i zapisem na premierę, bez pustych pól, selektorów i przycisków Kup; kurier i informacje przed zakupem. Hero pozostaje neutralnym editorialem bez produktu.

To oddzielny materiał do przeglądu, **nie pliki do wdrożenia**. `noindex`, brak ID analityki i CSP blokujący połączenia/formularze są celowe tylko tutaj. Brak formularza zamówienia, sekretów i linków Stripe. Nie kopiować tych ustawień do produkcji. Link do listy premierowej prowadzi do istniejącej strony — nie używano go do zapisu danych testowych.

Root `index.html`, `script.js`, dokumenty i pozostałe pliki produkcyjne są niezmienione; ich uzupełnienie/migracja wymaga osobnej pracy po zatwierdzeniu. Zachować działające Brevo, double opt-in, zgodę na analitykę i canonical przy przyszłym wdrożeniu.

## Sprawdzenie 03.11.2026

Po recenzji: odczyt DOM przy 1440, 390 i 320 px bez poziomego overflow. Cztery karty, każda z jednym statusem „W przygotowaniu” i linkiem do istniejącej listy premierowej; brak selektorów i przycisków zakupu. Status 13 px; teksty informacyjne, CTA i szczegóły 14 px. Przy 390 px CTA ma 55 px wysokości, summary 54,39 px. Rozwijanie szczegółów sprawdzone klawiszem Enter. Kontrast sprawdzonych par: status/treść 6,16:1, CTA 10,26:1, szczegóły 7,04:1, etykieta fotografii 5,65:1. To kontrola zmienionych kart, nie pełny audyt WCAG. Hero poprawnie załadowany i bez zmian. Brak błędów/ostrzeżeń konsoli. Sprawdzono zgodność CSS/obrazów z R04, poprawność lokalnych odnośników, brak formularza/linków płatniczych oraz niezmienność plików produkcji. Obliczenia prowizji i wydatków 3/6 miesięcy sprawdzono niezależnie z Decimal.

Sandbox Stripe, wysyłki, migracja DNS i prawdziwy zapis Brevo **nie były uruchamiane**. Nie jest to odbiór sprzedaży produkcyjnej.

[Pełny desktop](../../docs/previews/lean-desktop-full.jpg)

![Desktop — R04](../../docs/previews/lean-desktop.jpg)

![Mobile — uproszczona karta i zapis na premierę](../../docs/previews/lean-mobile.jpg)
