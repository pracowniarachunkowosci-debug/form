# LH Orange — audyt i plan migracji

**Aktualny odbiór 04.11.2026:** [wydanie #14 — 16 stron, paczka, G1–G8 i rollback](LH_RELEASE_14.md). Poniżej zachowano historyczny stan PR #11.

Stan odczytany 3 listopada 2026. **Faza A: przygotowanie; brak zgody na wykonanie fazy B.**
Zadanie: [komentarz właściciela w PR #10](https://github.com/pracowniarachunkowosci-debug/form/pull/10#issuecomment-6606701517).
Gałąź publikacyjna powstała z `main` / `38e0bd9bc8296b70ac68d92753d63f447d70df3e`.

## Wniosek

Uzupełnienie po recenzji PR #11: [operacyjne bramki GO/NO-GO, pytania do LH, eksport OVH i warianty SSL](RELEASE_READINESS.md) oraz [plan testów Brevo](BREVO_ACCEPTANCE_PLAN.md). Poniższy audyt dokumentuje odczyt; nie stanowi potwierdzenia konfiguracji, której jeszcze nie wdrożono.

Obecna statyczna strona mieści się w modelu hostingu Orange. Nie wymaga WordPressa, Node.js, bazy danych ani nowego abonamentu. Rekomendowana metoda późniejszego transferu: **FTPS explicit TLS**, ponieważ panel Orange nie udostępnia SSH. Nie wykonano logowania FTP, uploadu, dodania domeny, wystawienia certyfikatu, zmian DNS ani publikacji.

Pozostają warunki przed wdrożeniem: pełny eksport strefy i selektory DKIM, potwierdzenie zewnętrznej obsługi poczty przy podpinaniu domeny do LH, ustalenie sposobu zapewnienia SSL podczas przełączenia oraz zatwierdzenie dokumentów i test double opt-in. Publiczne DNS nie pozwalają wykluczyć wszystkich dodatkowych subdomen/usług.

## 1. DNS i działające usługi — fakty

Źródła pomiaru: `Resolve-DnsName` przez 1.1.1.1 oraz autorytatywny `dns106.ovh.net`; dodatkowo Google DNS-over-HTTPS dla CAA. NODATA oznacza brak rekordu danego typu przy istniejącej nazwie, NXDOMAIN — brak badanej nazwy.

| Nazwa / typ | Stan aktualny | Uwagi do migracji |
|---|---|---|
| apex / NS | `dns106.ovh.net`, `ns106.ovh.net` | DNS obsługuje OVH; zachować NS, bez przenoszenia całej strefy |
| apex / A | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` | GitHub Pages; TTL 3600 s |
| apex / AAAA | NODATA | Nie dodawać IPv6 bez potwierdzonego adresu LH |
| apex / CNAME | NODATA | Bez zmian |
| www / CNAME | `pracowniarachunkowosci-debug.github.io` | TTL 3600 s; dziś wskazuje GitHub Pages |
| www / A i AAAA po rozwiązaniu CNAME | IPv4 GitHub powyżej; IPv6 `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153` | To odpowiedzi celu CNAME, nie dowód osobnych rekordów AAAA w strefie |
| apex / MX | `1 mx1.mail.ovh.net`, `5 mx2.mail.ovh.net`, `100 mx3.mail.ovh.net` | Poczta przychodząca OVH; TTL 3600 s; **bez zmian** |
| apex / TXT SPF | `v=spf1 include:mx.ovh.com -all` | Zachować; nie dodawać IP WWW do SPF bez potrzeby wysyłki |
| apex / TXT | `1\|www.pracowniaform.com`; obecny `google-site-verification=…` | Zachować dokładne wartości z eksportu; tokenu nie powielamy w raporcie |
| DKIM | Nieustalone selektory | Nie stwierdzono braku DKIM; potrzebny eksport strefy lub nagłówek podpisanej wiadomości |
| `_dmarc` / TXT | NXDOMAIN | Brak publicznego rekordu pod tą nazwą; nie wdrażać samowolnie polityki `reject` |
| apex / CAA | NODATA, odpowiedź NOERROR | Nie wykryto ograniczenia wystawcy na apex; powtórzyć przed SSL także dla docelowego www |

Panel/API GitHub Pages potwierdza źródło **`main`, katalog `/`**, domenę `pracowniaform.com` i wymuszanie HTTPS. Odczyt HTTP strony głównej przez www i `/winter-26.html` zwrócił 200 z `Server: GitHub.com`. Treść strony głównej odpowiada bieżącemu `main` po normalizacji końców linii.

Potwierdzone zależności: GitHub Pages, DNS i MX OVH, formularz Brevo, GA4 uruchamiane po zgodzie oraz rekord weryfikacji Google. Publiczny adres formularza Brevo odpowiada 200 i udostępnia rzeczywisty formularz. Nie wykonano POST, zapisu adresu ani testowej wysyłki. Nie sprawdzono konta Brevo, stanu listy, double opt-in ani doręczania poczty. **HTTP 200 nie jest dowodem pełnej sprawności procesu newslettera.**

Odczyt pełnej strefy OVH nie został wykonany. Przed migracją właściciel powinien udostępnić eksport DNS lub zalogowaną sesję do odczytu: potrzebne są również subdomeny, SRV, autodiscover, DKIM i uwierzytelnienie domeny nadawczej Brevo. Nie zmieniać tych rekordów w ramach migracji WWW. Instrukcja [OVH dotycząca DKIM](https://docs.ovhcloud.com/en/guides/web-cloud/domains/dns-zone-dkim) opisuje rekord zależny od selektora; sam odczyt apex TXT go nie wykrywa.

## 2. LH Orange — odczyt panelu i test transportu

Odczyt zalogowanej sesji wykonano po wyraźnej zgodzie właściciela „Tak — wyłącznie odczyt konfiguracji”. Nie zapisano formularzy. Podgląd formularza dodawania strony został anulowany.

| Element | Potwierdzony stan |
|---|---|
| Pakiet / serwer | Orange 5 GB / `serwer533947` |
| IPv4 WWW | `195.2.223.12` |
| Aktywność | utworzony 03.11.2026, aktywny do 03.11.2027 |
| WWW | przydział 1000 MB, użycie 0 MB, 0 stron |
| Poczta LH | przydział 0, 0 skrzynek; nie oznacza braku skrzynek w OVH |
| Pozostałe | 1 główne konto FTP, 0 baz MySQL, 0 cron, 0 aplikacji |
| SSH / SFTP | SSH niedostępne w tym pakiecie według panelu; nie zakładamy SFTP/rsync |
| Host transferu | `serwer533947.lh.pl` |
| Katalog WWW | formularz proponuje prefiks `/public_html/` i osobny katalog strony; domena nie jest jeszcze przypięta |
| Dodawanie strony | dostępna opcja dodania samej domeny bez WordPressa; domyślnie PHP 8.5, niepotrzebne do HTML |
| SSL | dostępna opcja Let's Encrypt; certyfikat dla domeny nie został skonfigurowany |
| Multipoczta | domyślnie zaznaczona w formularzu; nie zapisywano ustawienia |

Bez uwierzytelnienia sprawdzono port 21: serwer ProFTPD odpowiedział, `AUTH TLS` zakończył się sukcesem, TLS 1.3 i walidacja certyfikatu hosta przeszły. To potwierdza szyfrowanie kanału sterującego, **nie uprawnienia do katalogu ani transfer danych**. Podczas zatwierdzonego wdrożenia wymagać explicit FTPS, `PROT P` dla kanału danych, trybu pasywnego i poprawnego certyfikatu; nie akceptować automatycznego powrotu do zwykłego FTP. Dane dostępowe pozostają wyłącznie w menedżerze haseł/kliencie właściciela.

[Multipoczta LH](https://www.lh.pl/pomoc/doc/multipoczta-co-to-jest/) dotyczy rozdzielania skrzynek domen. Nie jest potwierdzonym przełącznikiem „poczta zewnętrzna”. Przed dodaniem domeny należy ustalić z LH właściwy wariant dla istniejących MX OVH i lokalnego routingu poczty; nie utworzono zgłoszenia do dostawcy.

[Dokumentacja domeny technicznej](https://www.lh.pl/pomoc/doc/jak-zablokowac-dostep-do-katalogu-z-domeny-technicznej/) opisuje `serwerXXXXX.lh.pl` wskazujące `public_html`. Stąd planowany podgląd w podkatalogu; jego HTTPS i dostępność konkretnej ścieżki trzeba sprawdzić po zatwierdzonym uploadzie. [LH opisuje codzienne kopie do 30 dni](https://www.lh.pl/pomoc/doc/jak-przywrocic-strone-z-backupu-w-lh-pl/); własna kopia wydania nadal jest wymagana.

## 3. Plan fazy B — do osobnej akceptacji, niewykonany

### B0. Bramka zgody i zamrożenie wydania

1. Zatwierdzić konkretny commit PR, checklistę niżej, okno przełączenia i osobę decyzyjną. **Merge do `main` może od razu opublikować stronę na GitHub Pages.** Nie używać merge jako niewinnego kroku przygotowawczego; ustalić go oddzielnie z właścicielem.
2. Ponownie odczytać DNS, wyeksportować pełną strefę i zapisać kopię poza publicznym katalogiem WWW. Zapisać SHA dotychczasowego wydania. Nie usuwać GitHub Pages ani domeny przypisanej do niego podczas migracji.
3. Zbudować lokalne ZIP skryptem `scripts/build_release.py`, sprawdzić manifest SHA-256 i wielkość. Dokumentacja, podglądy, `.git`, `CNAME`, skrypty i pliki robocze nie trafiają do paczki. Paczka nie zawiera konfiguracji serwera ani sekretów.

### B1. Pliki → techniczny podgląd

4. Po zgodzie przesłać FTPS do nowego, jednoznacznego katalogu np. `/public_html/pf-release-<SHA>/`. Wcześniej sprawdzić zakres konta, ochronę kanału danych, wolne miejsce i brak nadpisywania innych usług. Sam upload tworzy zasoby dostępne z serwera, dlatego też wymaga zgody fazy B.
5. Podgląd: `https://serwer533947.lh.pl/pf-release-<SHA>/`. Najpierw zweryfikować certyfikat, bez obchodzenia ostrzeżeń. Ograniczyć dostęp do podglądu (autoryzacja w konfiguracji serwera) oraz indeksowanie nagłówkiem `X-Robots-Tag: noindex` **tylko na technicznym hoście/ścieżce**. `noindex` nie zastępuje kontroli dostępu. Nie kopiować tych blokad do produkcyjnego HTML, robots.txt ani konfiguracji finalnej domeny.
6. Sprawdzić pliki, wielkość, typy MIME AVIF/WebP/SVG, brak listowania katalogów, 404, ścieżki względne, desktop/mobile, linki, brak aktywnych płatności. Przy testach zachować odrzucenie analityki; nie wysyłać formularzy na produkcyjną listę bez uzgodnionego testu. Produkcyjne canonical pozostają zgodne z domeną docelową.

### B2. Domena → DNS → SSL

7. Przypiąć tylko stronę WWW do zatwierdzonego katalogu. Nie instalować WordPressa, nie tworzyć skrzynek, nie zmieniać NS ani automatycznie MX. Zweryfikować konfigurację poczty zewnętrznej i brak konfliktu Multipoczty przed zapisaniem.
8. Opcjonalnie obniżyć TTL **wyłącznie zmienianych rekordów WWW** z 3600 do 300 s co najmniej 3600 s plus bufor przed przełączeniem. Obniżenie TTL nie usuwa starych wpisów z cache. Bez wcześniejszego obniżenia zakładać co najmniej godzinę mieszanych odpowiedzi i możliwe opóźnienia resolverów.
9. Docelowo zastąpić cztery apex A jednym `195.2.223.12`; zastąpić www CNAME wartością `pracowniaform.com.` (albo zatwierdzonym przez LH rekordem A na ten sam IP). Nie pozostawić części starych A. Nie dodawać niesprawdzonego AAAA. Sprawdzić wynik A/AAAA dla www po rozwiązaniu nowego aliasu. **NS, MX, SPF, DKIM, DMARC, pozostałe TXT, SRV i inne subdomeny bez zmian.**
10. Wystawić SSL obejmujący apex i www. [Instrukcja LH Let's Encrypt](https://www.lh.pl/pomoc/doc/jak-uruchomic-certyfikat-ssl-lets-encrypt-na-serwerze-w-lh-pl/) wymaga, aby obie nazwy wskazywały już hosting. Występuje więc **ryzyko przerwy HTTPS pomiędzy zmianą DNS a gotowym certyfikatem**. Certyfikatu GitHub nie można przenieść bez klucza prywatnego, którego nie mamy. Przed przełączeniem potwierdzić z LH możliwość wcześniejszego wystawienia (np. DNS-01) lub przyjąć uzgodnione okno i natychmiastowy rollback przy błędzie. Nie obiecywać migracji bez przerwy i nie wyłączać weryfikacji TLS. Nie wykonano kontaktu z LH.
11. Dopiero z działającym certyfikatem sprawdzić przekierowania HTTP→HTTPS i www→apex bez pętli, canonical, odnowienie certyfikatu i datę ważności. Konfigurację przekierowań przygotować do przeglądu zgodnie z rzeczywistym panelem LH; ten PR jej nie wgrywa.

### B3. QA po przełączeniu

12. Porównać DNS autorytatywny i co najmniej dwa resolvery. Sprawdzić HTTPS obu nazw, 16 stron, statusy i nagłówki, robots/sitemap, brak testowego noindex/autoryzacji na produkcji, grafikę i formularz. Zweryfikować formularz na docelowym origin, przekierowanie po zapisie, double opt-in i wypisanie na adresie testowym zatwierdzonym przez właściciela.
13. Sprawdzić przychodzącą i wychodzącą pocztę OVH na kontrolowanych adresach oraz SPF/DKIM/DMARC z nagłówka wiadomości. Dopiero osobno planować zmianę polityki DMARC/uwierzytelnienie Brevo.
14. Po stabilizacji przywrócić TTL 3600. Utrzymać dotychczasowe Pages i stare wydanie minimum 48 godzin i do potwierdzenia stabilnej propagacji. Zablokować indeksowanie/dostęp do technicznej kopii, nie naruszając ACME ani produkcji. Zapisać protokół odbioru.

## 4. Rollback

| Wyzwalacz | Działanie po decyzji osoby zatwierdzającej |
|---|---|
| Nieprawidłowy/niegotowy SSL, niedostępna strona, błędny katalog | Przywrócić dokładny zestaw czterech GitHub A i www CNAME `pracowniarachunkowosci-debug.github.io` z eksportu; nie zmieniać NS/MX |
| Błąd samego wydania przy sprawnym LH/TLS | Przestawić katalog WWW na poprzednie zweryfikowane wydanie; nie usuwać bieżącej kopii przed diagnozą |
| Problem z pocztą | Porównać pełną strefę z eksportem i routing LH; nie „naprawiać” przez przeniesienie MX do LH. Wstrzymać przełączenie/wycofać zmiany WWW według planu |

Rollback DNS też podlega TTL i nie jest natychmiastowy. W mieszanym okresie obie lokalizacje powinny serwować bezpieczną stronę i kierować na ten sam formularz Brevo. Nie usuwać starego hostingu/certyfikatu ani nie zmieniać działającej gałęzi Pages przed zamknięciem okna rollback. W fazie A nie uruchomiono żadnego z tych działań.

## 5. Checklista do zatwierdzenia

### Przed publikacją zapowiedzi i listy premierowej

- [x] Osobna gałąź, brak checkoutu i płatności; jawne placeholdery; zachowany hybrydowy R04.
- [x] Administrator wskazany przez właściciela: PRACOWNIA RACHUNKOWOŚCI sp. z o.o., ul. Trawowa 19/1, 54-614 Wrocław, NIP 8943197084, KRS 0000997294. [ALEO wskazane przez właściciela](https://aleo.com/pl/firma/pracownia-rachunkowosci-spolka-z-ograniczona-odpowiedzialnoscia-wroclaw); nazwa, adres i NIP potwierdzone 03.11.2026 w [aktualnym odpisie API KRS](https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/0000997294?rejestr=P&format=json). Adres siedziby nie oznacza automatycznie adresu zwrotów.
- [x] Ustawienia cookies w stopce każdej strony i w polityce: ponowny wybór, wycofanie, odmowa po odświeżeniu; testy lokalne opisane w PR11_REVIEW_RESPONSE.
- [ ] Właściciel zatwierdza projekt polityki z 03.11.2026 i ustala datę obowiązywania. Do potwierdzenia rzeczywiste retencje, umowy, odbiorcy, transfery i obsługa kontaktu; test kodu nie potwierdza kompletności prawnej.
- [x] Projekt zasad premiery przepisany na listę WINTER 26 i przygotowywaną przedsprzedaż bez przyjmowania zamówień ani płatności; planowane nadania od 23.11.2026; stopki 2026.
- [ ] Merytoryczna akceptacja zasad i treści strony; nie traktować ich jako gotowego regulaminu sprzedaży WINTER.
- [ ] Kontrolowany test zapisu, double opt-in, wypisania i dostarczalności Brevo na docelowym origin. GET i walidacja formularza już sprawdzone, wysyłki nie wykonano.
- [ ] Pełny eksport DNS, DKIM, usługi subdomen, zewnętrzna poczta LH, plan SSL i rollback potwierdzone.
- [ ] Osobna zgoda na fazę B, dokładny commit i termin. Jawne placeholdery pozostają wyłącznie zapowiedzią, bez możliwości zakupu.

### Przed pierwszą sprzedażą — poza zakresem tego PR

- [ ] Realne fotografie każdego modelu i wariantu, wymiary, materiał, kolory, ceny brutto; zatwierdzone identyfikatory SKU, zapas i sposób ewidencji. Żadnego wymyślania parametrów po zdjęciu.
- [ ] Dane producenta/osoby odpowiedzialnej, identyfikacja/partia produktu, ocena ryzyka i właściwe ostrzeżenia/instrukcje; przegląd GPSR z osobą odpowiedzialną. Spółka jako sprzedawca nie przesądza automatycznie roli producenta. Punkt odniesienia: [rozporządzenie UE 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj?locale=pl), w szczególności informacje w ofercie na odległość; zob. także [obowiązki przedsiębiorców według UOKiK](https://www.uokik.gov.pl/public/bezpieczenstwo-produktow-obowiazki-przedsiebiorcow).
- [ ] Regulamin sprzedaży, prawa konsumenta, zwroty, reklamacje i rzeczywisty adres zwrotów zatwierdzone; nie stosować automatycznego wyłączenia odstąpienia tylko dlatego, że przedmiot jest drukowany po zamówieniu. [UOKiK opisuje wyjątek dotyczący specyfikacji konsumenta lub jego zindywidualizowanych potrzeb](https://prawakonsumenta.uokik.gov.pl/prawo-odstapienia-od-umowy/wylaczenia-prawa-do-odstapienia/); zastosowanie wymaga osobnej oceny.
- [ ] Potwierdzone czasy nadania, metoda InPost, cena dostawy, ewentualny próg darmowej wysyłki, obszar dostaw, opakowanie i procedura uszkodzeń. Ostateczny wariant dostawy nie jest jeszcze przesądzony.
- [ ] Osobna decyzja i testy operatora płatności, płatności/zwrotów/zapasów. **Stripe ani inny operator nie są aktywowane w tym zadaniu.**

Dokument jest planem technicznym i checklistą odbioru. Nie stanowi zatwierdzenia publikacji ani potwierdzenia kompletności dokumentów prawnych.
