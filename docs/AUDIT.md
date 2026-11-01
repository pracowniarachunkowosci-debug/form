# Audyt przed przebudową — issue #3

Data: 1 listopada 2026. Repozytorium: `pracowniarachunkowosci-debug/form`.
Baza: `38e0bd9` (main). Gałąź robocza: `codex/issue-3-winter26-draft`.

## Stan zastany i zakres

| Obszar | Ustalenie | Decyzja w projekcie |
| --- | --- | --- |
| Architektura | Statyczne HTML/CSS/JS, bez package.json, bez backendu | Zachować; Python stdlib jedynie do generowania statycznych plików |
| Hosting | CNAME `pracowniaform.com`; API Pages: `build_type=legacy`, branch `main`, path `/` | Nie zmieniać main ani ustawień hostingu; brak deploy |
| Workflow | Tylko dynamiczny `pages-build-deployment`; brak repozytoryjnego `.github/workflows` | Push wyłącznie osobnej gałęzi, draft PR |
| WINTER 26 | SOLIS, HELIX, VINE WAVE CAST, SOLIS DISH; historyczne wizualizacje | Cztery modele wymagane w #3; historyczne koncepty w osobnej sekcji archiwum |
| Strona główna | Sprzeczne wykluczenie sezonowości i zapowiedź pierwszego pre-orderu NORD/STONE/KINTSUGI | WINTER 26 jako przygotowywana kolekcja; pozostałe jako przyszłe koncepty |
| Prywatność | Placeholdery firmy i daty, `.pl` zamiast `.com`, brak zgodnego opisu analityki | Pełny projekt z rozdzieleniem podglądu, produkcji zastanej i przyszłego sklepu |
| Dokumenty | „Zasady premiery” nie są regulaminem sprzedaży | Osobne projekty regulaminu, zwrotów, dostawy, formularza; lista ma osobne zasady |
| Nawigacja | Na kontakt/polityce brak identyfikatorów `menuBtn`/`siteNav` wymaganych przez JS | Wspólna nawigacja, obsługa klawiatury i stopka |
| Zasoby | index odsyła do nieistniejących favicon.ico i apple-touch-icon.png | Usunąć nieistniejące odniesienia; zachować favicon.svg |
| SEO | Stare koncepcje w JSON-LD i marketingowych opisach | Zgodne metadane, bez Product/Offer i fikcyjnych cen; draft `noindex` |
| Assets | Brak zatwierdzonych fotografii czterech modeli i źródłowych kart R03A w repo | Neutralne miejsca na zdjęcia; nie generować fotografii oferty |

## Analityka i formularze — dowody i granice

Odczyt `script.js` na bazie 38e0bd9: GA4 jest ładowane dynamicznie dopiero po `accepted` w localStorage `pf_cookie_consent`. Identyfikator: G-58YFJ2RHNZ. Domyślne zgody analytics/ad są denied. Zapis nie zawiera daty, wersji ani terminu ważności; nie ma ponownego otwarcia ustawień/wycofania zgody. Odczyt localStorage nie obsługuje wyjątku przy zablokowanej pamięci.

Kontrola działającej strony w przeglądarce: na WINTER 26 przed wyborem i po „Odrzuć” lista `script[src]` zawierała wyłącznie `script.js`; baner po odmowie zniknął. To dowód stanu DOM skryptów, nie pełny HAR ani test przyjęcia zgody. Nie akceptowano analityki i nie generowano celowo zdarzeń testowych do produkcyjnego GA4.

Na stronie głównej po odmowie nadal znajdują się zewnętrzne CSS i JS Brevo z `sibforms.com` oraz rzeczywisty `form action` do `ad958d5f.sibforms.com/serve/...`. Nie wysłano formularza. Nie potwierdzono działania double opt-in, dostarczalności ani konfiguracji kont dostawców. Nie wolno opisywać tego stanu jako „brak integracji/analityki”.

W wersji roboczej skrypty GA4/Brevo i formularz są usunięte z wykonania. CSP blokuje `connect-src`, `frame-src` i `form-action`, a skrypty/zasoby są lokalne. Nie jest to zmiana produkcji ani gotowy CMP. Przed uruchomieniem wybranych usług potrzebna jest osobna konfiguracja zgód i zgodna polityka.

## Dane spółki i kontakt

Oficjalne API KRS: odpis aktualny pobrany 01.11.2026, stan 07.07.2026, ostatni wpis 11. Potwierdzono nazwę, adres Trawowa 19/1, 54-614 Wrocław, NIP 8943197084, kapitał 5000 PLN. REGON API: 52340878500000; dziewięciocyfrowy numer podmiotu 523408785 zgodny ze specyfikacją i Rejestr.io.

Nagłówek aktualnego odpisu wskazuje sąd ostatniego wpisu jako `SYSTEM` (RDF). Nie potraktowano tego jako nazwy sądu. W odpisie pełnym wpisy 1 i 6 wskazują Sąd Rejonowy dla Wrocławia-Fabrycznej we Wrocławiu, VI Wydział Gospodarczy KRS. Taką nazwę przyjęto do projektu; wymagana ponowna kontrola aktualności przed publikacją.

Rekordy MX pracowniaform.com: mx1.mail.ovh.net / mx2.mail.ovh.net / mx3.mail.ovh.net. To potwierdza routowanie domeny, nie istnienie ani obsługę skrzynki kontakt@pracowniaform.com. Nie wysyłano wiadomości testowej. Telefon sklepu i adres zwrotów pozostają decyzją właściciela; nie wykorzystano telefonu biura rachunkowego.

## Propozycja podziału prac / PR-ów

1. WINTER 26, model danych wariantów, archiwum, korekty strony głównej i layout responsive.
2. Dokumenty prawno-zakupowe, dane spółki, wspólne linkowanie, izolacja integracji w review oraz blokery uruchomienia.

W tym zadaniu oba pakiety trafiają do jednego draft PR, aby można było ocenić spójność całej propozycji. Żaden z nich nie jest zatwierdzeniem uruchomienia sklepu. Dalszy PR uruchomieniowy musi rozstrzygnąć wszystkie blokery i uzyskać oddzielną zgodę.

Źródła: [issue #3](https://github.com/pracowniarachunkowosci-debug/form/issues/3), [produkcja](https://pracowniaform.com/), [WINTER 26](https://pracowniaform.com/winter-26.html), [odpis aktualny KRS](https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/0000997294?rejestr=P&format=json), [odpis pełny KRS](https://api-krs.ms.gov.pl/api/krs/OdpisPelny/0000997294?rejestr=P&format=json), [Rejestr.io](https://rejestr.io/krs/997294/pracownia-rachunkowosci), [strona spółki](https://pracowniarachunkowosci.pl/).
