# Strona główna — teksty do akceptacji

Propozycja do [strony głównej](../../index.html) z wydania `79a788f`. Wersja pokazywana na LH pozostaje wydaniem z manifestu PR #20. Poniższe teksty można przyjąć jako jeden pakiet, a następnie sprawdzić w nowej wersji strony.

| Miejsce | Proponowana treść |
|---|---|
| Dopisek pod przyciskiem w otwarciu | Poznaj WINTER 26, zimową kolekcję czterech ozdób Pracowni Form. |
| Nagłówek nad kartami Nord, Stone i Kintsugi | Trzy kierunki Pracowni Form |
| Wstęp nad trzema kartami | Nord czerpie z architektury, Stone z faktury kamienia, a Kintsugi ze śladu łączenia. W zimowej kolekcji WINTER 26 przyglądamy się mniejszej skali — czterem formom świątecznych ozdób. |
| Dopisek przy próbnikach wykończenia | Próbki pokazują kierunki pracy z powierzchnią. Kolory ozdób WINTER 26 pokażemy po zakończeniu prób. |
| Etykieta i nagłówek formularza | **Lista premierowa** · **Dowiedz się o premierze WINTER 26** |
| Opis formularza | Zostaw adres e-mail, jeśli chcesz dostać wiadomość o premierze WINTER 26. W katalogu możesz już obejrzeć cztery modele i ułożyć własny zestaw. |
| Pole zgody | Wyrażam zgodę na otrzymywanie od Pracowni Form e-maili o kolekcjach i ich premierach. Mogę wycofać zgodę w każdej chwili. |
| Dopisek pod formularzem | Wiadomości dotyczą kolekcji i ich premier. [Przeczytaj politykę prywatności](../../polityka-prywatnosci.html). |
| Nagłówek i opis obok formularza | **Co Cię interesuje?** Możesz zaznaczyć, jakie obiekty Pracowni Form chcesz poznawać. Odpowiedź jest dobrowolna. |
| FAQ o charakterze kolekcji | **Co obejmuje WINTER 26?** Cztery modele ozdób: KNITTED STAR, KNITTED MEDALLION, HELIX i FULL SOFT. Nord, Stone i Kintsugi to odrębne kierunki Pracowni Form. |
| FAQ o zapisie i zakupie | **Czy mogę już zamówić ozdoby?** Obecnie możesz obejrzeć modele i skomponować zestaw. Zapis na listę służy otrzymywaniu wiadomości o premierze. Nie przyjmujemy zamówień, rezerwacji ani przedpłat. |

Wstęp do trzech kart zastępuje cały dotychczasowy akapit o pierwszej premierze. FAQ o WINTER 26 można umieścić w miejscu obecnego porównania trzech kolekcji. Wzmianka o obiektach do ogrodu w pozostałym FAQ odnosi się do oferty marki i nie powinna sugerować, że ozdoby sezonowe mają potwierdzoną odporność na warunki zewnętrzne. Pytanie o preferencje obok formularza dotyczy zainteresowań marką; wartości wysyłane do Brevo wymagają odrębnego uzgodnienia, jeśli zmieni się zakres odpowiedzi.

## Wyszukiwarki i zgodność formularza

- Opis meta i opis `WebPage` w JSON-LD: „Poznaj WINTER 26 — cztery ozdoby Pracowni Form. Obejrzyj modele, skomponuj zestaw i zapisz się na wiadomość o premierze.”
- `ItemList` dla trzech istniejących kart: nazwa „Kierunki Pracowni Form”, opis „Nord, Stone i Kintsugi to trzy kierunki projektowe marki”. Zachować adresy właściwych kart. Kolekcja sezonowa ma osobną stronę.
- W `FAQPage` zastosować identyczne pytania i odpowiedzi jak w widocznym FAQ. Usunąć obietnicę wcześniejszych zamówień i deklarację premiery trzech kolekcji jednocześnie. Pozostałe wpisy FAQ również muszą mieć widoczny odpowiednik na stronie.
- Zachować techniczną kotwicę `#preorder` dla działających odnośników. Tekst wyświetlany klientowi to „Lista premierowa”.
- Po zatwierdzeniu zgody uzgodnić jej treść w Brevo i HTML. Zachować historyczne wersje dla wcześniejszych zapisów. Zaktualizować test zgodności formularza tak, by dopuszczał wyłącznie zaakceptowany tekst i nadal sprawdzał endpoint, pola oraz obowiązkową zgodę. Przed publikacją przebudować i ponownie odebrać manifest.
