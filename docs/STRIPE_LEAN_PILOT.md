# WINTER 26 — budżetowy pilot sprzedaży

**Issue #9 · 03.11.2026 · projekt do zatwierdzenia, sprzedaż nieaktywna.**

## Decyzja

Rekomenduję **statyczny R04 + Stripe Payment Links + ręczną realizację, początkowo tylko kurier w Polsce**. Bez Next.js, Vercela, własnego koszyka, API i bazy zamówień. Cztery modele pozostają w przygotowaniu: KNITTED STAR, KNITTED MEDALLION, HELIX, FULL SOFT. Żadna cena, kolor ani SKU nie zostały zatwierdzone. [Payment Links](https://docs.stripe.com/payment-links) działa jako strona Stripe otwierana ze zwykłego odnośnika.

Hosting: proponuję **LH Mango za 37,50 zł netto / 46,13 zł brutto płatne za pierwszy rok z góry**, o ile promocja nadal obowiązuje przy zakupie. Odnowienie 399 / 490,77 zł rocznie; nie przedstawiać promocyjnej ceny jako stałej. Można później rozważyć Woo pod `/sklep/`, lecz zasoby, cron i obsługa Woo wymagają ponownej oceny. Tańszy w odnowieniu LH Orange kosztuje 50 / 61,50 zł na start i 199 / 244,77 zł rocznie później. Mango wygrywa koszt pierwszego pilota; Orange wygrywa koszt dwóch lat (249 vs 436,50 zł netto). [Aktualny cennik LH](https://www.lh.pl/hosting).

**Minimum wydatku na hosting: Netlify Free, 0 zł**, dopuszczający projekty komercyjne. Jednak nowy plan ma 300 kredytów/mies.; wyczerpanie zatrzymuje strony. To opcja tylko po akceptacji limitu i monitorowania ruchu, nie równie niezawodny odpowiednik płatnego hostingu. Nie kupowałbym dodatkowej platformy dla oszczędności 46,13 zł w całym pierwszym roku. [Użytek komercyjny](https://www.netlify.com/blog/introducing-netlify-free-plan/), [cennik](https://www.netlify.com/pricing/), [zużycie i wstrzymanie](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/how-credits-work/).

GitHub Pages wykluczamy jako docelowy hosting sklepu zgodnie z [ograniczeniami GitHub](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). Vercel Hobby wykluczamy ze względu na [użytek niekomercyjny](https://vercel.com/docs/plans/hobby). Wybór LH/Netlify, zakup i DNS wymagają osobnej decyzji właściciela.

## Co uruchomić po zatwierdzeniu

- Jeden produkt Stripe i jeden link na **fizyczny wariant SKU**, nie wybór koloru jako niezobowiązujące pole tekstowe. Cena jednorazowa brutto w PLN, zgodna z zatwierdzoną stawką VAT. Wyłączyć napiwki, upsell, subskrypcje i zbędne metody. W pilocie ilość **sztywno 1**; opcja zmiany ilości istnieje, ale limit sesji nie liczy sztuk. Zestaw tylko jako osobne, wcześniej skompletowane SKU z odseparowanym zapasem. [Tworzenie linku](https://docs.stripe.com/payment-links/create), [obiekt Payment Link](https://docs.stripe.com/api/payment-link/object).
- **BLIK i karty:** BLIK ma oficjalne wsparcie Payment Links, PLN i polskich klientów; jego dostępność na konkretnym koncie wymaga aktywacji/uprawnień i testu. Nie zakładamy, że każda metoda zawsze się wyświetli. Po otwarciu konta przez właściciela sprawdzić oba sposoby zapłaty, język polski i brak niezamierzonego przewalutowania. [BLIK](https://docs.stripe.com/payments/blik).
- Zbierać e-mail, **wbudowany adres wysyłki ograniczony do Polski** i wymagany telefon. Jedna jawna stawka kurierska i realny termin. Włączyć akceptację zatwierdzonego regulaminu i odnośnik do polityki prywatności. Branding Checkout dopasować w dostępnych granicach; nie obiecywać identycznego R04 poza stroną marki. [Konfiguracja](https://docs.stripe.com/payment-links/customize), [opłaty dostawy](https://docs.stripe.com/payments/no-code/charge-shipping).
- Cena, dostawa, termin, dane sprzedawcy, zwroty i GPSR muszą być dostępne **przed CTA „Kup”**, nie dopiero po płatności. Po zapłacie użyć potwierdzenia Stripe; nie budować strony, która na podstawie redirectu ogłasza „opłacono”. Realizować dopiero po sprawdzeniu skutecznej płatności w Dashboard. [Obsługa po płatności](https://docs.stripe.com/payment-links/post-payment).

## Dostawa: uczciwe ograniczenia

Payment Links pozwala dodać wymagane pole tekstowe, numeryczne lub listę; maksymalnie trzy pola własne. Lista w panelu ma do 10 opcji, w API do 200. Nie jest to wyszukiwarka sieci InPost. Pole „Kod Paczkomatu” nie sprawdza istnienia, dostępności, zgodności usługi ani poprawnego punktu wskazanego przez klienta. Nie wykazano warunkowej walidacji takiego pola zależnie od wybranej dostawy. **Nie włączamy Paczkomatów w pilocie.** Dane osoby zbieramy w dedykowanych polach adresu/telefonu, nie w custom fields. [Pola własne](https://docs.stripe.com/payment-links/customize#add-custom-fields).

Kurier: właściciel ręcznie przepisuje dane z Dashboard do Managera Paczek, sprawdza adres, telefon, gabaryt i wagę, opłaca etykietę i zapisuje numer przesyłki. Konto/uprawnienia, sposób nadania, ewentualny podjazd i aktualny cennik trzeba ustalić przed sprzedażą. Nie ma integracji InPost ani API. [Regulamin Managera Paczek](https://inpost.pl/sites/default/files/docs/regulaminy/regulamin-aplikacji-manager-paczek-obowiazujacy-od-24072025-2090007.pdf).

Przy błędnym adresie wstrzymać nadanie, poprosić kupującego o korektę przez kontakt z zamówienia i zapisać uzgodnienie w ograniczonym rejestrze obsługi. Nie zgadywać adresu. Jeśli później dopuszczamy punkty: najpierw test wyboru i weryfikacji; błędny kod wymaga potwierdzenia klienta, bez samowolnego wyboru innego punktu. Nie pobierać dopłaty inną metodą bez uzgodnienia; brak rozwiązania kończy się obsługą anulowania/zwrotu.

## Stany i codzienna obsługa

**Payment Links nie zapewnia rezerwacji magazynowej.** Limit ukończonych sesji jest obecnie dostępny **także w Dashboard**; nie tylko w API. Nie dowodzi zapłaty metodą asynchroniczną ani nie odejmuje współdzielonych składników. Link dezaktywować również u operatora — usunięcie CTA nie unieważnia zapisanego wcześniej URL. [Limit sesji](https://docs.stripe.com/payment-links/customize#limit-the-number-of-times-a-payment-link-can-be-paid).

1. Jedna osoba prowadzi rejestr: SKU, gotowe sztuki po kontroli, odseparowany bufor, limit aktywnego linku, sprzedane, zarezerwowane ręcznie, wysłane, zwrócone. Limit ustala poniżej gotowego zapasu; bufor nie ma gwarantowanej ochrony przy współbieżności. Bez potwierdzonego zapasu link pozostaje wyłączony. Zakaz wspólnego stanu pojedynczych sztuk i zestawów oraz nieograniczonego made-to-order.
2. Otwierać mały nakład wyłącznie w okresie, gdy operator może obserwować zamówienia; włączyć powiadomienia i regularnie przeglądać Dashboard. Przed każdą wysyłką sprawdzić status, SKU, kwotę, walutę, zwrot/spór i to, czy zamówienie już zrealizowano. Powiadomienie e-mail ani success URL nie zastępują tej kontroli.
3. Przy płatności oczekującej nie wydawać jej sztuki innemu zamówieniu do uzgodnienia wyniku. Przy współbieżnym przekroczeniu zapasu: natychmiast wyłączyć link, uzgodnić wszystkie sesje/płatności, wykorzystać wyłącznie rzeczywisty bufor; przy niedoborze kontakt i zwrot, bez obietnicy automatycznego dodruku. Jeśli taki model ryzyka jest nieakceptowalny, nie otwierać publicznej sprzedaży przez Payment Links — potrzebny system rezerwacji.
4. Rekord operacyjny: wewnętrzny numer, identyfikator płatności/sesji, SKU, ilość, status, numer przesyłki, identyfikator zwrotu. Adresy/e-mail/telefon przechowywać w Stripe i narzędziu przewoźnika, bez ich kopiowania do ogólnego arkusza. Identyfikatory też mogą być danymi osobowymi: dostęp ograniczony, MFA, kopie i okres retencji uzgodniony z księgowością/polityką prywatności.
5. Zwrot pełny/częściowy wykonywać z Dashboard, zapisać wynik i uzgodnić saldo. Pierwotna prowizja Stripe pozostaje kosztem. Stan magazynu przywracać dopiero po odbiorze i kontroli towaru, nie po samym zwrocie pieniędzy. [Zwroty](https://docs.stripe.com/refunds).

## Cash-out: pierwsze 3 i 6 miesięcy

**Opłaty platform, nie kompletny budżet produkcji.** Kurs planistyczny 4 zł/USD, jeden użytkownik Pro, brak nadwyżek. Nie zaliczamy czasu Codexa do faktur. LH wymaga zapłaty za cały rok już na początku; nie dzielimy tej kwoty przez 12 przy wyliczaniu wydatku pilota.

| Wariant | Wydatek przed VAT: 3 mies. | 6 mies. | Wariant z 23% VAT: 3 / 6 mies. |
| --- | ---: | ---: | ---: |
| A: LH Mango + Payment Links | 37,50 zł | 37,50 zł | **46,13 / 46,13 zł** |
| A: LH Orange + Payment Links | 50,00 zł | 50,00 zł | 61,50 / 61,50 zł |
| A: Netlify Free + Payment Links, w limitach | 0 zł | 0 zł | 0 / 0 zł |
| B: Vercel Pro 20 USD + budżet Neon 5 USD + kopie 10 zł/mies. | 330 zł | 660 zł | 405,90 / 811,80 zł |

Źródła: [LH](https://www.lh.pl/hosting), [Netlify](https://www.netlify.com/pricing/), [Vercel](https://vercel.com/pricing), [Neon](https://neon.com/pricing). **Neon 5 USD to założenie niskiego zużycia, nie gwarantowany abonament**; cennik wskazuje rozliczenie użycia. Przy budżecie 20 USD zamiast 5 USD B rośnie o 180/360 zł przed VAT. Kopie 10 zł to rezerwa, nie zakupiona usługa. Darmowa baza może obniżyć rachunek, lecz trwałość i odtwarzanie nadal trzeba zapewnić.

Dla zagranicznych usług VAT może być rozliczany jako import usług, zamiast zostać pobrany przez dostawcę. Kolumna 23% to scenariusz, **nie pewna kwota obciążenia karty**; potwierdzić NIP-UE, fakturę, odliczenie, kurs i opłatę bankową z księgowością. LH brutto to rzeczywisty wydatek nawet przy późniejszym odliczeniu VAT.

Stripe Payment Links jest w standardowym Payments, bez osobnego abonamentu. BLIK 1,6% + 1 zł; standardowa karta EOG 1,5% + 1 zł. Założenie zaokrąglenia HALF_UP od każdej płatności. [Cennik Stripe](https://stripe.com/en-pl/pricing).

| Pełna kwota pobrana, z dostawą | BLIK / karta | Średnia 70% BLIK, 30% kart |
| --- | ---: | ---: |
| 39 zł | 1,62 / 1,59 zł | 1,611 zł |
| 78 zł | 2,25 / 2,17 zł | 2,226 zł |
| 156 zł | 3,50 / 3,34 zł | 3,452 zł |

To **przykłady obliczeń, nie ceny produktów**. Przy 20 płatnościach/mies. × pełna kwota 78 zł opłaty wyniosą 133,56/267,12 zł przez 3/6 miesięcy. A Mango z hostingiem brutto: **179,69 / 313,25 zł**; B przed VAT od infrastruktury: **463,56 / 927,12 zł** (wariant 23%: 539,46 / 1 078,92 zł). Przy 100 płatnościach prowizje to 667,80/1 335,60 zł. Te same prowizje w A i B — własny backend nie daje rabatu Stripe. Karty premium/zagraniczne i FX mogą kosztować więcej; brak założenia o gratisowych zwrotach prowizji.

Do realnego cash-out **dodać**: produkcję, odpady, opakowania, etykiety InPost i podjazdy, zwroty, dokumenty/księgowość, ewentualne odnowienie domeny, pocztę oraz przekroczenie istniejącego planu Brevo. Kwoty są nieznane przed próbami i ofertą przewoźnika; nie przyjmujemy ich jako zero. Wypłata Stripe może nastąpić później niż zakup etykiety — potrzebna rezerwa gotówki. Nie włączamy płatnych Tax/Invoicing, domeny Checkout ani automatyzatorów do bazowego planu.

Nakład własny, **szacunek do planowania**: A 12–24 h przygotowania po dostarczeniu kompletu danych + 1–2 h/mies. utrzymania technicznego i 5–10 min/zamówienie ręcznej administracji (bez pakowania/produkcji). B 60–120 h minimalnego backendu, rezerwacji, webhooków i panelu + 2–4 h/mies., nadal ręczne nadania. To różne zakresy; nie są ofertą wykonawcy ani obowiązkowym wydatkiem. Dla testu popytu A jest wystarczające przy świadomej akceptacji obsługi i ryzyka stanów.

## Przed pierwszą sprzedażą

- [ ] Właściciel potwierdza fizyczne modele, zdjęcia, wymiary, materiał, kolory, SKU, cenę brutto, zapas, opakowanie, bezpieczeństwo i realny termin; bufory i zestawy oddzielone.
- [ ] Pełne dane spółki, NIP/KRS, adres, telefon, adres zwrotów i działający e-mail. Audyt `main` wykazał NIP `[uzupełnij]` i `kontakt@pracowniaform.pl` w polityce, choć kontakt główny używa `.com`. Uzupełnienie wymaga danych właściciela, nie zgadywania.
- [ ] Recenzja regulaminu, prywatności, reklamacji i formularza odstąpienia z PR #4. **Standardowe ozdoby drukowane po zamówieniu nie stają się automatycznie produktem personalizowanym**; stosować 14 dni odstąpienia co do zasady od otrzymania. Potwierdzenie umowy i jej warunków na trwałym nośniku; sam zmienny link do regulaminu nie wystarczy. [UOKiK — odstąpienie](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/), [informacje przed umową](https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/prawo-do-informacji/).
- [ ] GPSR: ustalić producenta, adres pocztowy i elektroniczny, identyfikację produktu/partii, ocenę ryzyka, instrukcje i ostrzeżenia oraz dane wymagane w ofercie; QR nie zastępuje oznakowania. [UOKiK — obowiązki](https://www.uokik.gov.pl/public/bezpieczenstwo-produktow-obowiazki-przedsiebiorcow).
- [ ] Księgowość ustala VAT, dokument sprzedaży, ewidencję/kasę i obowiązek KSeF dla **całej spółki**, nie tylko małego pilota. Stripe receipt jest potwierdzeniem płatności, nie automatycznie polską fakturą ani dokumentem KSeF. B2C nie ma obowiązku KSeF; przejściowy limit 10 tys. zł dla faktur poza KSeF kończy się z końcem 2026 r. — nie zakładać, że spółka go spełnia. [MF — KSeF](https://ksef.podatki.gov.pl/ponizej-10-000-zl/).
- [ ] Zatwierdzić hosting, umowę Stripe/KYC i nadania InPost; przetestować eksport i odtwarzanie rejestru. Konta należą do spółki, MFA, minimalne uprawnienia, bez sekretów w repo.
- [ ] Zachować domenę i `.html` URL-e, HTTPS i przekierowania; formularz Brevo, double opt-in, strony potwierdzeń, zgody i analitykę po zgodzie. Migracja hostingu nie może podmienić formularza na płatny formularz platformy. Osobno sprawdzić canonical/sitemap oraz usunąć zabezpieczenia **mocka** z przyszłego pakietu produkcyjnego. Ten PR nie jest takim pakietem.

## Sandbox i późniejsza migracja

**Plan testów, niewykonany:** po osobnej zgodzie na konto/sandbox utworzyć testowy produkt i link, bez prawdziwych danych ani środków. Sprawdzić kartę/BLIK: sukces, odmowę, anulowanie, przerwanie i późny wynik; komplet adresu/telefonu, granicę PL, cenę z dostawą, brak zmiany ilości, regulamin i wiadomość po zamknięciu nakładu. W dwóch równoległych sesjach sprawdzić limit i niedobór; bez zaliczenia tego testu nie obiecywać ochrony stanu. Sprawdzić pełny/częściowy zwrot, duplikat ręcznej realizacji oraz eksport. InPost: tylko próbny formularz/etykieta dostępna bez zakupu; żadnych realnych nadań. [Stripe — testowanie](https://docs.stripe.com/testing).

Rejestr produktów: `model → wariant → sku → product_id → price_id → payment_link_id → URL karty`. SKU jest stabilne i odrębne od partii; schemat do zatwierdzenia: `PF-W26-{MODEL}-{KOLOR}-{ROZMIAR}`. Teraz żadnego kodu nie przypisujemy fikcyjnemu wariantowi. Przy zmianie ceny zachować historyczne mapowanie. Rejestr zamówień zawiera identyfikatory i statusy; eksport Stripe dla księgowości przechowywać z kontrolą dostępu, nie w Git. [Eksport płatności](https://support.stripe.com/questions/exporting-payment-data?locale=en-GB).

Wiosną 2027 sprawdzić popyt i nakład obsługi; Woo nie jest automatycznym następnym zakupem. W Woo zachować SKU, domenę i linki do kart (`winter-26.html#knitted-star` itd.); ewentualne nowe URL-e pod `/sklep/` z mapą przekierowań. Import produktów i uzgodnienie stanów są osobnym zadaniem. **Eksport Stripe nie oznacza automatycznej migracji zamówień do Woo**; historię można pozostawić w archiwum Stripe i księgowości, a nowe zamówienia kierować do Woo po kontrolowanym zamknięciu starych linków i uzgodnieniu płatności oczekujących.

## Dostarczony projekt

[Lokalna makieta](../previews/lean-pilot/winter-26.html) wykorzystuje R04 z PR #5, commit `f97fcd6`, z czterema nieaktywnymi CTA, polami wariantów i sekcją informacji przed zakupem. [Instrukcja podglądu](../previews/lean-pilot/README.md). Root strony, Brevo i skrypt zgód pozostają identyczne z bazowym `main` `38e0bd9`. Brak live/test Payment Links i danych osobowych. PR #4/#5/#7/#8, hosting i DNS bez zmian; nic nie opublikowano.

Walidacja: desktop 1440 px / mobile 390 px bez poziomego overflow, poprawny hero, 4 wyłączone CTA, brak błędów konsoli. Zgodność plików R04 i niezmienność produkcji sprawdzona; kwoty przeliczone niezależnie. [Podglądy i granice testów](../previews/lean-pilot/README.md#sprawdzenie-03112026).
