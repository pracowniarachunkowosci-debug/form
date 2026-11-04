# WINTER 26 — wydanie katalogu do odbioru

Wydanie zbudowano z czystego checkoutu `79a788f2e899c3e66058a4fac10c9ae9bf94886e` (PR #19). Zamrożony katalog obejmuje R04, konfigurator R02 dla 4/6/8 i poprawkę LF/CRLF z PR #18. Ten draft dodaje tylko metrykę, manifest i publiczne podsumowanie odbioru.

| Artefakt | Wynik |
|---|---|
| ZIP | 9 177 395 B, 111 plików, SHA-256 `67f380f309fa0b82b913aeeb4e0385b6fd2fc55e295c02229d1d96259cd69766` |
| [Manifest](manifest.json) | SHA-256 `c76c4dc051966f674ea12850956f7b157bdee9d60d25d4bf9888592d7a1fb3c9` |
| [Metryka](release.json) | Zgodność sum każdego elementu archiwum. Powtarzalna budowa z tego samego źródła #19, oddzielna od historycznej paczki #18. |

## Wyniki

- Generator, test LF/CRLF, rejestr wariantów, bramki zakupowe i scenariusze 4/6/8 przeszły. Sprawdzono nagłówek, hero, formularz, 16 stron i 589 lokalnych odnośników oraz odwołań do zasobów. Testy zgody, odmowy i wycofania analityki przeszły.
- Po rozpakowaniu pobrano przez lokalny HTTP 111/111 plików i sprawdzono ich SHA, w tym 16/16 stron HTML. Potwierdzono MIME WebP/AVIF, stronę główną i HTTP 404 dla brakującej strony. Pierwszy lokalny serwer wymagał poprawnego mapowania MIME. Przy dużych grafikach zaobserwowano lokalne timeouty. Ostateczna kontrola zakończyła się zgodnością wszystkich plików.
- W Chrome przy 1440/390/320 px konfigurator zachował HELIX przy zmianie rozmiaru zestawu 8 → 6 → 4. Licznik wskazał jeden model i zero kolorów, bez przewijania w poziomie. Drugie ujęcie HELIX otworzyło się klawiaturą, Escape przywrócił fokus. Paczka używa listy premierowej i nie zawiera aktywnych linków do płatności.
- 4 listopada 2026 zakończono odbiór podglądu na LH. Przez HTTPS wszystkie 111 plików, w tym 16 stron, zwróciły 401 bez hasła i 200 po autoryzacji. Każdy pobrany plik miał SHA-256 zgodny z manifestem. Sprawdzono odpowiedź dla błędnego hasła, zakaz indeksowania i buforowania, ochronę formularzy, typy WebP/AVIF, stronę startową i 404.
- Na rzeczywistym adresie LH Chrome przeszedł test przy szerokościach 1440, 390 i 320 px. Sprawdzono cztery galerie, zmianę ujęcia klawiaturą, powiększenie i Escape oraz wybór rozmiarów 4/6/8, powtórzenie modelu, edycję pozycji i wyczyszczenie zestawu. Na badanych stronach nie wystąpiło przewijanie w poziomie. Wąskie ekrany sprawdzono przez emulację w Chrome.

## Warunki przed publikacją

| Bramka | Stan |
|---|---|
| G2 — dokumenty | Obie strony w ZIP są projektami. Administrator zatwierdza kontakt, retencję, odbiorców, transfery, tekst zgody i datę. Do rozstrzygnięcia wzmianka o pre-orderze w aktualnym formularzu. |
| G3 — Brevo | Do uzgodnienia izolowana próba z kontrolowanymi adresami: zapis, brak marketingu przed DOI, doręczenie, potwierdzenie, duplikat, wypisanie, nagłówki i odpowiedź skrzynki kontaktowej. Próby na rzeczywistych kontaktach nie przeprowadzono. |
| G4 — strefa i backup | Potwierdzono źródło bieżącej strony i kopię źródeł. Potrzebny prywatny eksport pełnej strefy i weryfikacja faktycznych selektorów nadawców. |
| G5 — hosting i poczta | Odebrano chroniony podgląd i wszystkie zasoby. Pozostaje potwierdzenie dostarczania do OVH, także dla wiadomości inicjowanej na LH. |
| G6 — SSL | Docelowy hosting wymaga certyfikatu dla apex i www. Osobno zatwierdzić wariant i czas na wycofanie. |
| G7 — paczka | Odebrano paczkę katalogową na chronionym hostingu. Po zatwierdzeniu dokumentów ponownie zbudować i odebrać końcowy ZIP z nowym SHA. |
| G8 — przełączenie | Wymagana ostateczna zgoda właściciela na wersję, okno i rollback. |

Po domknięciu G2–G7 wykonać prywatny backup strefy i plików, sprawdzić certyfikaty obu nazw oraz ustalić punkt wycofania. Po G8 zmienić tylko rekordy WWW dla apex i www, sprawdzić HTTPS, przekierowania, 16 stron, listę i pocztę. Przy błędzie odtworzyć poprzednie rekordy WWW z eksportu i zweryfikować wynik z niezależnych resolverów. Utrzymać poprzedni hosting przez propagację i okres kontroli. Pełny operacyjny protokół i dokumenty do akceptacji przekazano właścicielowi lokalnie.

**Rekomendacja: GO dla prywatnego pokazu. Publiczne przełączenie pozostaje NO-GO do zamknięcia bramek i decyzji właściciela.**
