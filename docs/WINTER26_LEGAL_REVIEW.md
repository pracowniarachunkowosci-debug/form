# WINTER 26 — projekty prawne, 14.11.2026

**DO AKCEPTACJI / NIEPUBLIKOWANE. Komplet siedmiu projektów do przeglądu; brakujące dane i decyzje nie pozwalają uznać ich za zatwierdzone dokumenty Live.**

Otwórz [pakiet HTML](legal-draft/index.html). Jedyna skonsolidowana lista dla właściciela: [D1–D7 — dane znane i brakujące](legal-draft/index.html#dane). Nie trzeba ponownie dostarczać cennika ani rozpoznawać potwierdzonych geometrii zdjęć.

## Zakres i adaptacja źródeł

Zmiany wyłącznie w `docs/legal-draft/*` i niniejszym raporcie. Bez zmian aktywnych stron prawnych, checkoutu, flag, konfiguracji, katalogu, cen, stanów i fotografii; bez commit/push/deploy lub wysyłania wiadomości. Nie używano CUA. Git odczytywano z metadanych `C:/Users/lsolt/.codex/visualizations/2026/09/04/01a06d6a-faec-75d1-a6c5-9a6946b9c460/form-git` i drzewa `C:/sklep/form`, bez użycia repozytorium nadrzędnego i plików działalności rachunkowej.

Przeczytano najnowszy załącznik `Wklejony tekst.txt`, [dane sprzedaży](WINTER26_SPRZEDAZ_DANE.md), źródła PR4 oraz komentarze PR28/Issue24 przez odczyt `gh api`. Konektor GitHub był niedostępny; CLI zakończyło odczyt powodzeniem. Z informacji zadania nadrzędnego: rzeczywiste testy Stripe Sandbox karta+BLIK i podpisanych webhooków CLI zakończono z lokalnym PHP — **nie na LH, nie w Live**. W tej podpracy nie powtarzano testów płatności.

Odczytano `git show` dla [źródeł PR4, commit f6e218fe9cfa2772e805b9e62b8d86ae2dec91ba](https://github.com/pracowniarachunkowosci-debug/form/tree/f6e218fe9cfa2772e805b9e62b8d86ae2dec91ba/content), bez checkout/fetch. Zachowano przydatne zapisy i układ merytoryczny; nie przeniesiono dawnego layoutu ani prototypu pozorującego wysłanie odstąpienia.

| Źródło / blob | Projekt i adaptacja |
| --- | --- |
| `content/regulamin-sklepu.html` · `91547f90175f63179827ceddd580bd3943344715` | [Regulamin](legal-draft/regulamin-sklepu.html): zachowane §§1–8, aktualna oferta, koszyk, pełne koszty, trwały nośnik; moment zawarcia umowy jawnie do decyzji. |
| `content/dostawa-i-platnosci.html` · `4c48b652fa893c620c08e0437dae37f9eb204445` | [Dostawa/płatności](legal-draft/dostawa-i-platnosci.html): stawki, próg, Stripe i start nadań; bez wymyślonego SLA. |
| `content/zwroty-i-reklamacje.html` · `5d84d0c600489ef02bbf82e2e4f9b507ad4c9f01` | [Zwroty/reklamacje](legal-draft/zwroty-i-reklamacje.html): odrębne procedury i terminy, przykład refundacji dostawy, decyzja o częściowych zwrotach. |
| `content/formularz-odstapienia.html` · `58f289caa421c70bc6fe9e6d566e829d6f66e9f1` | [Wzór odstąpienia](legal-draft/formularz-odstapienia.html): zachowany wzór do skopiowania/wydruku, bez niewysyłającego demo. |
| `content/polityka-prywatnosci.html` · `76a870e77168c2fd84bce4930ea5f757b129309a` | [Prywatność](legal-draft/polityka-prywatnosci.html): zamówienia, płatności, przewóz, reklamacje, odbiorcy, retencja i transfery. [Cookies/zgody](legal-draft/cookies-i-zgody.html): rozwinięcie §§3, 5 i 6 źródła w konkretne komunikaty. |
| `docs/LEGAL_RESEARCH.md` z PR4 + aktualne dane sprzedaży | [GPSR](legal-draft/gpsr.html): nowa karta na podstawie istniejących ustaleń; oferta, oznaczenia, dokumentacja i 12 wariantów. Nie wpisano producenta, materiału ani ostrzeżeń bez dowodów. |

## Dane i decyzje zastosowane w tekstach

- 1/2/4/6/8 ozdób = 50/84/150/220/290 PLN brutto; kurier 20,49 zł, Paczkomat 18,49 zł. Od 6 ozdób łącznie obie metody 0 zł. **2 + 4 = 234 zł + 0 zł dostawy**, bez automatycznego przeliczenia na zestaw 6 za 220 zł. Nie ma aktywnego kodu.
- 23.11.2026 to planowany początek nadań, nie gwarancja doręczenia ani pełny SLA. Brakuje maksymalnych terminów i zasad mieszanej realizacji.
- Dane spółki przeniesiono z PR4 jako **niezatwierdzone**. Nie odczytywano aktualnego KRS. Nie wykorzystano telefonu/godzin z innej marki. Adres siedziby nie został uznany za magazyn zwrotów ani adres producenta.
- Proponowany w PR4 model umowy: przyjęcie e-mailem sprzedawcy. Wymaga decyzji D4 i uzgodnienia z faktycznym pobraniem płatności, wiadomościami i czasem przyjęcia. To nie twierdzenie o wdrożonym backendzie. Inny spójny model jest możliwy po równoczesnej zmianie tekstów i procesu.
- Koszt zwykłego odesłania po stronie klienta to propozycja, dopuszczalna po prawidłowej informacji przed zakupem. Można zaoferować darmowy zwrot. Koszty ustawowej reklamacji ponosi sprzedawca niezależnie od tej decyzji.
- Proporcjonalny zwrot części kompletu i brak wstecznego naliczania darmowej dostawy są jawnie **propozycją polityki**, nie twierdzeniem o bezwzględnym nakazie dzielenia zestawów. Ustawowe pełne odstąpienie pozostaje zachowane.
- Dodatkowa gwarancja, godziny obsługi, stałe zobowiązanie do ADR, analityka i newsletter są wyborami. Double opt-in opisano jako rekomendację dowodową, nie ogólny wymóg ustawowy. Rzeczywisty kontakt i telefon wymagają uzupełnienia.
- Nie żąda się zgody RODO na wykonanie zamówienia ani marketingu jako warunku zakupu. Bez opcjonalnych technologii nie należy tworzyć fikcyjnego banera. Wzór odstąpienia jest dobrowolny; nie wymaga PESEL, skanu dokumentu ani konta klienta.

## Prawo i źródła urzędowe sprawdzane 14.11.2026

| Zakres | Ustalenie i źródło |
| --- | --- |
| Prawa konsumenta | Odczytano [Dz.U. 2026 poz. 1244 — tekst jednolity](https://api.sejm.gov.pl/eli/acts/DU/2026/1244/text/O/D20261244.pdf), ogłoszony 23.09.2026, stan ujednolicenia 02.09.2026; [metryka ELI](https://eli.gov.pl/eli/DU/2026/1244/ogl). To nowsza podstawa niż 2024/1796 z PR4. Przed Live trzeba sprawdzić także późniejsze zmiany. |
| Informacje i zakup | Art. 12, 17 i 21: cechy i pełne koszty przed zamówieniem, jednoznaczny obowiązek zapłaty, potwierdzenie na trwałym nośniku. Sam zmienny link nie zastępuje przekazanej wersji dokumentów. |
| Odstąpienie | Art. 27–34, 38 ust. 1 pkt 3: 14 dni od odbioru, przedłużenie przy braku pouczenia, osobne 14 dni na odesłanie. Standardowy wybór koloru/druk po zamówieniu nie jest automatycznie indywidualną specyfikacją. [UOKiK — odstąpienie](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/). |
| Zwrot płatności | Art. 32–34: do 14 dni od otrzymania oświadczenia, najtańsza zwykła oferowana dostawa, możliwość wstrzymania do rzeczy lub dowodu odesłania, chyba że zaproponowano odbiór; pierwotna metoda bez kosztów, chyba że wyraźnie uzgodniono inną. [UOKiK — skutki](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/skutek/), [pytania o odstąpienie i dostawę](https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/odstapienie-od-umowy/). |
| Reklamacje | Art. 43c–43f: co do zasady niezgodność istniejąca przy dostarczeniu i ujawniona w ciągu 2 lat; naprawa/wymiana, warunki obniżenia/odstąpienia, koszty sprzedawcy. Art. 7a: odpowiedź konsumentowi na trwałym nośniku w 14 dni, brak odpowiedzi oznacza uznanie. Nie pomylono odpowiedzi z czasem naprawy ani okresu ujawnienia z terminem zgłoszenia roszczenia. Art. 7aa rozszerza rozdziały 4, 5a i 5b na określonych przedsiębiorców-osoby fizyczne; nie rozszerzono automatycznie art. 7a. [UOKiK — niezgodność](https://prawakonsumenta.uokik.gov.pl/reklamacja/niezgodnosc/). |
| Funkcja odstąpienia online | [Dyrektywa 2023/2673](https://eur-lex.europa.eu/legal-content/PL/ALL/?uri=CELEX%3A32023L2673): art. 11a dyrektywy 2011/83/UE, transpozycja do 19.12.2025, stosowanie przepisów krajowych od 19.06.2026. [Urzędowy wykaz UC169](https://www.gov.pl/web/premier/projekt-ustawy-o-zmianie-ustawy-o-prawach-konsumenta-oraz-ustawy-o-konsumenckiej-pozyczce-lombardowej) opisuje **projekt**. [Odpowiedź MF z 29.09.2026](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDYFJB7/i19620-o1.pdf), znana z PR4, zawiera harmonogram 2027, nie pewną datę obowiązywania. W odczytanym tekście 2026/1244 nie ma docelowej funkcji art. 11a; istnieje art. 30 ust. 3–4 o elektronicznym oświadczeniu i potwierdzeniu. Nie uzyskano dowodu ogłoszenia późniejszego aktu wdrażającego tę funkcję. Przed Live sprawdzić Dziennik Ustaw i [RCL UC169](https://legislacja.gov.pl/projekt/12414453); termin UE sam nie dowodzi zakończenia polskiej implementacji. |
| Prawo do naprawy | Oficjalny [porządek Stałego Komitetu RM z 05.11.2026](https://www.gov.pl/web/premier/5-listopada-2026-r3) wymienia UC154 jako projekt. Nie dopisano projektowanego przedłużenia odpowiedzialności o 12 miesięcy jako już obowiązującego przepisu PL. |
| GPSR | [Rozporządzenie 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj?locale=pl), art. 9, 13, 16, 19–21 i 52: bezpośrednie stosowanie od 13.12.2024, dane producenta i kontaktu, identyfikacja i właściwe ostrzeżenia w ofercie, analiza ryzyka/dokumentacja przed obrotem; techniczna dokumentacja 10 lat. [Konsolidacja 29.05.2026](https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX%3A02023R0988-20260529) uwzględnia 2024/2748. QR nie zastępuje wymaganych informacji. [UOKiK — obowiązki](https://www.uokik.gov.pl/public/bezpieczenstwo-produktow-obowiazki-przedsiebiorcow), [UOKiK — pytania, rękodzieło i ocena bezpieczeństwa](https://www.uokik.gov.pl/public/bezpieczenstwo-produktow-pytania-i-odpowiedzi). |
| Nadzór krajowy GPSR | [Ustawa 07.11.2025, Dz.U. 2025 poz. 1826](https://eli.gov.pl/eli/DU/2025/1826/ogl/pol) nie jest projektem; jej późniejsze wejście w życie nie odracza stosowania samego GPSR. Pakiet nie obejmuje wyliczania sankcji. |
| ODR / ADR | [Rozporządzenie 2024/3228](https://eur-lex.europa.eu/eli/reg/2024/3228/oj/pol/pdf) uchyla podstawę platformy ODR od 20.07.2025. Nie dodano starego odsyłacza do skarg ODR; pozostawiono [ADR UOKiK](https://polubowne.uokik.gov.pl/). |
| Prywatność i marketing | [PKE](https://api.sejm.gov.pl/eli/acts/DU/2024/1221/text.html), art. 398 (uprzednia zgoda marketingowa), art. 399 (informacja/zgoda na urządzeniu z wyjątkiem niezbędności). RODO: art. 6, 7, 13–22 i rozdział V; [UODO — obowiązek informacyjny](https://uodo.gov.pl/pl/676/4255), [UODO — przejrzysta retencja](https://uodo.gov.pl/pl/676/4260). Nie wpisano arbitralnych czasów logów, kopii ani zgód. |

**Ograniczenie weryfikacji:** PDF aktualnego tekstu ustawy i strony UOKiK/ELI były dostępne. Część bezpośrednich odczytów EUR-Lex zwracała stronę główną/challenge; pełny UC169, RCL i załącznik MF — timeout/błąd dostępu. Podstawowe artykuły GPSR i daty dyrektywy sprawdzono również w indeksowanych fragmentach oficjalnego EUR-Lex; status „projekt” UC169 w indeksowanej stronie urzędowej. Historyczny harmonogram MF pochodzi z odczytanych źródeł PR4. Nie jest to pełna kontrola wszystkich późniejszych zmian do końca 14.11.2026. Przed Live pozostaje ponowny odczyt stanu legislacyjnego. Wyjaśnień Komisji C/2025/6233 nie zaliczono jako ponownie przeczytanej pełnej podstawy (challenge). Ustalenia nie opierają się na komercyjnych omówieniach.

## Weryfikacja lokalna i przekazanie

**PASS:** 8 stron HTML, 57 lokalnych odwołań; 40 pomiarów ekranowych (8 × 5 szerokości) bez overflow; 8 kontroli print i wygenerowanych wydruków A4. Obejrzano zrzut indeksu na 390 px oraz formularza w emulacji print. To weryfikacja projektu dokumentów, nie akceptacja prawna ani test checkoutu. Pierwsze uruchomienie headless w sandboxie zakończyło się timeoutem; kontrola w osobnym procesie po eskalacji zakończyła się powodzeniem.

Wyniki: [kontrola struktury i linków](legal-draft/qa/links.json), [układ i druk](legal-draft/qa/layout.json). Polecenia z `C:/sklep/form`:

```powershell
python docs/legal-draft/verify.py
node --experimental-websocket docs/legal-draft/verify-layout.mjs
```

Kontrola lokalna obejmuje zagnieżdżenie HTML, ID, pliki i kotwice, znacznik projektu/noindex, brak skryptów/formularzy/osadzonych zasobów zewnętrznych. Nie jest testem dostępności wszystkich linków urzędowych. Kontrola układu korzysta z osobnego procesu headless Chrome i nowego profilu tymczasowego, bez przeglądarki/CUA użytkownika: 320/360/390/430/1100 px, `scrollWidth <= clientWidth`, widoczny status, brak żądań sieciowych, emulacja print i generowanie A4. Zrzuty print nie są renderami stron PDF; nie zaliczać ich jako pełnej inspekcji każdego wydruku.

Pakiet nie jest podlinkowany z witryny. Odczytany `scripts/build_release.py` wybiera HTML z katalogu głównego, nie z `docs/legal-draft`. Nie uruchamiano build/deploy. Przy wdrożeniu zachować ten zakres; ręczna kopia całego repo może ujawnić szkice, a noindex nie jest kontrolą dostępu.

Do integracji gotowy jest **wewnętrzny pakiet do akceptacji**. Braki i wybory właściciela są w [D1–D7](legal-draft/index.html#dane). Po ich rozstrzygnięciu uzgodnić dokumenty z rzeczywistą obsługą zamówień i doręczaniem potwierdzenia, ponownie sprawdzić prawo, nadać wersję/datę oraz usunąć uwagi redakcyjne przed publikacją. Status stagingu, płatności na LH i InPost raportuje zadanie nadrzędne.
