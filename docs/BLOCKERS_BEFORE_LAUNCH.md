# BLOCKERS BEFORE LAUNCH

Wszystkie poniższe punkty są otwarte. Właściciel zatwierdza decyzje biznesowe; treści wymagają recenzji prawnej. Data przeglądu: 01.11.2026.

- [ ] Potwierdzić aktualne dane spółki i sąd KRS; wskazać datę wejścia dokumentów w życie.
- [ ] Przetestować obsługę `kontakt@pracowniaform.com`, ustalić telefon sklepu, adres zwrotów i reklamacji. Siedziba nie jest automatycznie adresem zwrotów.
- [ ] Zatwierdzić cztery modele, rzeczywiste zdjęcia i prawa do nich, materiały, wymiary, kolory, SKU, ceny brutto, stany oraz konfiguracje i ceny zestawów 2/4.
- [ ] Ustalić osobno czas wysyłki z magazynu, produkcji standardowego wariantu i transportu; zasady zamówień mieszanych, limity produkcji i kraje dostawy.
- [ ] Zweryfikować bezpieczeństwo produktów i dokumentację GPSR: producent/kontakt, identyfikatory, ocena ryzyka, wyniki odpowiednich testów, ostrzeżenia i instrukcje po polsku, etykiety/opakowania. QR jest dodatkiem. Brak podstaw do deklaracji odporności/ekologiczności.
- [ ] Wybrać hosting sklepu/backend, operatora płatności, metody płatności, kuriera/InPost, koszty i umowy. Zatwierdzić moment zawarcia umowy, treści przycisków, e-maile i zasady faktur. Nie uruchamiać ich w tym PR.
- [ ] Zatwierdzić standardowe 14-dniowe odstąpienie również przy druku katalogowego wariantu na zamówienie, koszty odesłania i procedurę reklamacji bez ograniczania uprawnień ustawowych.
- [ ] Ponownie zbadać implementację funkcji odstąpienia online (UC169 i ewentualne późniejsze akty); wdrożyć backend i potwierdzenia na trwałym nośniku po odrębnej akceptacji. Demo nie obsługuje realnych oświadczeń.
- [ ] Wybrać procesorów i retencję danych, zawrzeć umowy powierzenia, ocenić transfery, uzupełnić politykę zgodnie z faktycznie wdrożonymi usługami.
- [ ] Rozstrzygnąć GA4/Brevo i cookies. Jeśli wrócą: zgody przed uruchomieniem, łatwe wycofanie, dokumentacja zgód, double opt-in/lista wypisów według zatwierdzonego procesu; test sieciowy każdego stanu zgody. Brak włączania analityki w tym draft.
- [ ] Zatwierdzić prawniczo komplet dokumentów i zgodność checkoutu z informacjami przedumownymi; usunąć wszystkie placeholdery oraz komunikaty projektu dopiero po akceptacji.
- [ ] Wykonać osobny odbiór E2E przyszłego sklepu: zamówienie, płatność testowa, e-mail, dostawa, odstąpienie, reklamacja, dostępność, urządzenia, cookies, bezpieczeństwo. Obecne testy dotyczą statycznego podglądu.
- [ ] Uzyskać wyraźną zgodę właściciela na publikację. Dopiero w osobnym wdrożeniu zmienić `noindex`, opublikować zatwierdzony sitemap i ewentualne schema oparte na realnych danych.
