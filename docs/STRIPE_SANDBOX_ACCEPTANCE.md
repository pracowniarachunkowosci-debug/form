# WINTER 26 — odbiór Stripe Sandbox, 4 listopada 2026

**Wynik: karta i BLIK działają dla jednego fizycznego produktu z kurierem w Polsce. Nie uruchamiać jeszcze sprzedaży.** Oba zamówienia testowe po 15 PLN miały status `Succeeded` w Dashboardzie. Zwrot częściowy karty został potwierdzony, pełny zwrot BLIK przyjęty do przetwarzania. Nie zweryfikowano końcowego rozliczenia tego zwrotu ani dostarczenia e-maila.

Test [#15](https://github.com/pracowniarachunkowosci-debug/form/issues/15) wykonano w zalogowanym **Pracownia Form sandbox [Test]** przez przeglądarkę, bez API. Użyto wyłącznie fikcyjnych danych zamawiającego, testowych kart i kodów Stripe. Testowy URL był przekazywany w pamięci przez prywatną kartę „Kup TEST” na loopback; pliki pomocnicze zostały w ignorowanym `.artifacts`. Nie zmieniono rejestru sklepu, statusu `sandboxPassed`, bramek zakupu ani PR #11/#13.

## Co skonfigurowano

| Parametr | Sprawdzony stan |
|---|---|
| Produkt | Istniejący KNITTED STAR — TEST, `prod_VZFxe7RCCOIJna`, cena jednostkowa 10 PLN, bez tworzenia duplikatu. Kategoria **General – Tangible Goods**. Automatic tax wyłączony; to nie jest test stawek VAT. |
| Payment Link | Sandbox `plink_1UY7eMH7sElYuMPYN3mJ1afJ`. Jedna sztuka, ilość niemodyfikowalna. Limit **dwóch ukończonych zakupów**, żeby sprawdzić obie metody. |
| Dostawa | Nowa stawka **Kurier Polska — TEST**, `shr_1UY7e0H7sElYuMPYM7Q7LtGx`, 5 PLN. Jedyny kraj: Polska. W Checkout pole kraju było nieedytowalne. |
| Dane | Obowiązkowe dane kontaktowe, nazwa odbiorcy, telefon, adres wysyłki; adres rozliczeniowy domyślnie taki sam. Brak dosprzedaży i zapisywania karty. |
| Metody i wygląd | Karta i BLIK widoczne i skutecznie użyte. Stripe oferował także Klarna i Link; nie testowano ich ani nie zmieniano ustawień całego konta. Sprawdzono polski interfejs, oznaczenie piaskownicy i nazwę Pracownia Form sandbox. |

[Ustawienia dostawy i telefonu](previews/sandbox-shipping.jpg) · [Checkout po wyczerpaniu limitu](previews/sandbox-link-limit.jpg). Zrzuty nie zawierają danych kupujących ani adresu testowego Payment Link.

## Wyniki prób

| Próba | Wynik | Dowód / zakres obserwacji |
|---|---|---|
| Karta odrzucona | PASS | Oficjalna testowa karta odmowy, końcówka 0002. Checkout pokazał odmowę i umożliwił ponowienie; w historii próby widoczny `generic_decline`. |
| Karta udana | PASS | Testowa Visa z końcówką 4242: ekran podziękowania, następnie w Dashboardzie `Succeeded`, 15 PLN, ukończona Checkout Session. PaymentIntent `pi_3UY7ivH7sElYuMPY0vpE4eZg`. |
| BLIK odmowa klienta | PASS | Testowy wzorzec e-maila `customer_declined` i sześciocyfrowy kod: najpierw oczekiwanie, potem „The customer declined this payment”. Można ponowić. |
| BLIK timeout | PASS dla zachowania Checkout | Wzorzec `customer_timeout`: oczekiwanie na potwierdzenie, potem niepowodzenie i powrót do formularza. UI wyświetlił ogólny komunikat o odrzuceniu karty, mimo wyboru BLIK. Dashboard pokazuje nieudaną próbę BLIK; nie potwierdzono osobnego kodu przyczyny timeoutu w API. |
| BLIK sukces | PASS | Kod testowy 123456; w Dashboardzie „Payment using BLIK succeeded”, 15 PLN, ukończona sesja oraz zdarzenie sukcesu płatności asynchronicznej. PaymentIntent `pi_3UY7hCH7sElYuMPY052xCok3`. Nieudane próby z tej sesji nie są osobnymi zamówieniami. |
| Anulowanie / porzucenie | PASS dla porzucenia | Otworzono trzeci Checkout i zamknięto przed zatwierdzeniem; nie powstała trzecia opłacona transakcja. Nie czekano na techniczne wygaśnięcie tej sesji. |
| PL, telefon, adres, ilość | PASS | Polska jako jedyna opcja; brak selektora ilości; obowiązek telefonu w Dashboardzie. Po zakupie: odbiorca, ulica, kod, miasto, kraj, telefon i e-mail widoczne w szczegółach. |
| Dwie sesje i wyczerpany limit | PASS | Dwie sesje równocześnie otwarte, płatności kończone kolejno. Po dwóch sukcesach Dashboard: **Deactivated, 2 of 2 used**. Nowe wejście: „The link is no longer active”. Nie testowano wyścigu dwóch autoryzacji w tej samej chwili. |
| Zwrot częściowy karty | PASS | 5 z 15 PLN. Dashboard potwierdził udany zwrot 5 PLN. |
| Zwrot pełny BLIK | PASS przyjęcie / PENDING rozliczenie | Zlecono zwrot całych 15 PLN w Sandbox. Ostatni stan: **Refund pending due to bank processing**. Nie uznawać za zakończony, dopóki szczegóły zwrotu tego nie potwierdzą. |
| Potwierdzenie / e-mail | PASS ekran i historia / NOT RUN dostarczenie | Oba ekrany podziękowania i dostępna historia potwierdzeń w Dashboardzie; „No receipts sent”. Nie wysyłano maila ani rzeczywistej przesyłki. |

**Kontrola granicy wydania:** sprawdzono istniejący lokalny ZIP z bazowej gałęzi PR #13: 109 plików, bez adresu testowego Checkout, dokumentacji i prywatnej karty. Nowa próba budowy na osobnym checkout Windows zatrzymała się na `Stale generated page: winter-26.html` przed pakowaniem (Git pokazuje LF w indeksie i CRLF na dysku). Nie jest to potwierdzenie świeżego builda; odtworzyć i wyjaśnić różnicę w ramach #14 przed publikacją. Nie regenerowano sklepu na tej gałęzi.

## Jak obsłużyć ręcznie

1. W odpowiednim środowisku: **Payment Links → konkretny link → Payments and analytics → płatność** (albo **Transactions** po ID). W **Checkout summary** porównać produkt, ilość ×1, 10 PLN, dostawę 5 PLN i sumę 15 PLN. Zobaczyć komplet danych nadawczych; nie kopiować danych klientów do GitHuba.
2. W osi zdarzeń sprawdzić Checkout Session i końcowy status płatności. Przy BLIK widać kolejno oczekiwanie, ukończenie sesji i wynik asynchroniczny. Wysyłać dopiero przy opłaconej transakcji bez zwrotu; przekierowanie, screen kupującego ani sam wpis o ukończeniu sesji nie wystarczają.
3. Operacyjnie oznaczyć **opłacone → do spakowania → nadane** raz na identyfikator płatności. Porównać link i produkt z zatwierdzoną mapą handlowego SKU; test pokazał nazwę i ID produktu, nie potwierdził rzeczywistego SKU ani koloru. Przy niezgodności, zwrocie lub braku zapasu wstrzymać wysyłkę. Numer przesyłki wpisać w prywatnej ewidencji; test nie tworzy etykiety.
4. Zwroty: otworzyć konkretną płatność → **Refund**, sprawdzić kwotę i powód. Śledzić status w szczegółach transakcji do wyniku końcowego. Przed ponowieniem sprawdzić już zwróconą kwotę. Potwierdzenia: **Receipt history**; dostępność przycisku wysłania nie dowodzi doręczenia.

## Warunki decyzji przed Live — plan, nie wykonane działania

- Najpierw sprawdzić stan zwrotu BLIK z raportu oraz wykonać kontrolowany test doręczenia potwierdzenia na adres przeznaczony do prób. Zatwierdzić metody płatności i branding; zdecydować, czy ograniczyć dodatkowe metody z domyślnej konfiguracji.
- Właściciel/osoba uprawniona: potwierdzić właściwą spółkę, przedstawiciela, KYC, rachunek wypłat i warunki Stripe. Z księgowością uzgodnić VAT produktu i dostawy, sposób prezentacji kwot brutto oraz dokument sprzedaży. Cena 10 PLN i kurier 5 PLN są wyłącznie danymi testowymi.
- Zatwierdzić realne fotografie, warianty, SKU, stan przeznaczony na każdy link, dane GPSR, koszt i termin kuriera, regulamin, polityki zwrotów i reklamacji. Zestawy wymagają wydzielonego zapasu. Limit linku nie rezerwuje wspólnego magazynu dla singli i zestawów; nie oferować Paczkomatów bez sprawdzonego wyboru punktu.
- Dopiero po osobnej zgodzie na Live: utworzyć **nowe** Product/Price/Payment Link dla rzeczywistego SKU, ręcznie sprawdzić link, cenę, ilość, kraj, kontakt i dostawę; druga osoba porównuje z kartą sklepu. Zgoda na uruchomienie i publikację jest osobną decyzją. Do tego czasu wszystkie bramki sklepu pozostają zamknięte.
- [Issue #14](https://github.com/pracowniarachunkowosci-debug/form/issues/14) dotyczy zapowiedzi, którą można ocenić niezależnie od Live. Do jej wydania nie dodawać testowych URL-i, prywatnej karty ani danych transakcji. Ten PR zawiera wyłącznie dokumentację.

Źródła Stripe: [tworzenie Payment Links](https://docs.stripe.com/payment-links/create), [ustawienia Checkout](https://docs.stripe.com/payment-links/customize), [karty testowe](https://docs.stripe.com/testing), [kody i scenariusze BLIK](https://docs.stripe.com/payments/blik/accept-a-payment?payment-ui=checkout), [weryfikacja po płatności](https://docs.stripe.com/payment-links/post-payment), [statusy zwrotów](https://docs.stripe.com/refunds).
