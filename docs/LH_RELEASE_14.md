# Wydanie katalogu WINTER 26 na LH Orange — 04.11.2026

**GO do odbioru kandydatu; NO-GO do publicznego przełączenia.** Zbudowano całą stronę. Nie wykonano uploadu, zmiany hostingowej, DNS, mailingu, publikacji ani merge. Lokalny podgląd [strony głównej](http://127.0.0.1:8776/) i [WINTER 26](http://127.0.0.1:8776/winter-26.html) serwuje zawartość rozpakowanego ZIP na komputerze właściciela. To nie jest adres LH. Brak cen i piątkowych zdjęć nie blokuje uruchomienia **katalogu**.

## Wydanie i dowody

| Pole | Wartość |
|---|---|
| Baza / źródło plików RC | PR #13 `1665d196c6bf` (z PR #11) → `20bc512e8b80be6de469eadf4aa0849fa3659355`. Kolejny commit dokumentacyjny nie zmienia payloadu. |
| Budowa | Z osobnego, świeżego checkoutu na Windows i z czystej gałęzi: identyczne archiwum i manifest. `python scripts/build_release.py` (Python + Node, historia Git z bazami testów). Skrypt odrzuca brudny checkout. |
| Artefakty lokalne | `.artifacts/lh-20bc512e8b80/{pracownia-form-lh.zip,manifest.json,release.json}`. ZIP 9 169 919 B, 109 plików, 9 415 187 B przed kompresją. [Manifest](release14/manifest.json) i [metryka](release14/release.json) w PR. |
| SHA-256 ZIP | `952f91afea3c5e50fd94484e2df362924104264242ea881777d3303549b26985` |
| SHA-256 manifestu | `76cc1203f042300639fc1d757b1c9d8d7f907478c44b54bd9c7e8c9fb3f7498a` |
| Backup obecnej strony | Lokalny `.artifacts/backup-pages-38e0bd9.zip`, SHA-256 `8eb69ac03969a451c40335c27bbec041b9a1b0b189a207d4d0dfcdeb77789d4a`. Kopia **źródeł** wskazanego przez Pages `main` (`38e0bd9b`), nie kopia skrzynek, strefy ani konfiguracji panelu. Zachować również działający Pages. |

- Generator porównuje znormalizowane końce CRLF/LF, nie ignoruje zmian tekstu. Regresja potwierdza zgodność obu wariantów i wykrywa celową zmianę CTA. Polityka Git i normalizacja tekstu na wejściu do ZIP stabilizują SHA. Po pominięciu samych końców linii nie ma różnic w treści stron, CSS, JS ani grafik względem #13. Hero i jego pliki zamrożone.
- 16 stron i 596 referencji/zakotwiczeń; Brevo i inicjalizacja GA zgodne z bazą, zgody/odmowa/cofnięcie/reload, Escape/fokus i propagacja między kartami PASS. Produkcyjne canonical dla 14 stron; techniczne strony DOI pozostają świadomie `noindex`. Robots i sitemap zachowane. Test bramek wariantów i nieaktywnych zakupów PASS; 4 karty, 2 zestawy, zero adresów checkoutu Stripe w HTML.
- Każdy z 109 plików pobrano przez lokalny HTTP i porównano z SHA manifestu; AVIF/WebP z właściwym MIME, brakujący URL 404. Transport lokalny miewał timeouty większych plików: w końcowym przebiegu sześć ponowień, żadnego brakującego lub niezgodnego pliku. Warunek oddzielnego odbioru na LH: cały zestaw plików, bez powtarzalnych timeoutów. CRC/PASS ZIP nie zastępuje tego pomiaru.
- Chrome: [desktop 1440](previews/release14-desktop.jpg), [mobile 390](previews/release14-mobile.jpg), hero załadowane, cztery modele, bez poziomego przewijania. HELIX: Enter → dialog, Escape → fokus na tym samym odnośniku; „Powiadom mnie” prowadzi na listę. Pełna macierz wcześniejszego odbioru UI w [raporcie #13](WINTER26_STOREFRONT_HANDOFF.md).

## LH, DNS i poczta: stan zaobserwowany

04.11: DNS publiczny (Google DoH), rzeczywiste połączenia HTTPS z walidacją nazw i łańcucha, HTTP bez automatycznego wykonania redirectu oraz FTPS AUTH TLS bez logowania. Strona działa dziś z GitHub Pages, `main:/`, wymuszony HTTPS. HTTP apex i www oraz HTTPS www zwracają 301 na HTTPS apex; HTTPS apex 200, serwer GitHub. TLS obu nazw ważny do 28.01.2027. Techniczny host `serwer533947.lh.pl`: HTTPS 200 Apache, poprawny certyfikat do 10.12.2026; FTPS TLS 1.3. Próba SNI dla **obu** nazw produkcyjnych bezpośrednio na LH `195.2.223.12`: **hostname mismatch**. Certyfikat technicznego hosta nie obejmuje domeny sklepu.

[Odczyt panelu 03.11](LH_ORANGE_MIGRATION.md): Orange 5 GB, serwer533947, 1000 MB dla WWW, wtedy bez strony i bez skrzynek LH. Dziś panel LH w przeglądarce wymaga loginu; nie zweryfikowano ponownie listy katalogów, uprawnień transferu ani routingu. Nie uzyskano uwierzytelnionego eksportu strefy OVH. Dostępność publicznego serwera nie jest uprawnieniem do uploadu.

| Element | Dzisiaj / dokładny rollback | Projekt po zgodzie |
|---|---|---|
| apex A | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; TTL 3600 | Zastąpić wszystkie cztery jednym `195.2.223.12`, po ponownym potwierdzeniu IP w LH |
| www CNAME | `pracowniarachunkowosci-debug.github.io.`; TTL 3600 | `pracowniaform.com.` tylko jeśli LH potwierdzi obsługę aliasu dla certyfikacji; jeśli wymaga bezpośredniego A, przedstawić do GO wariant zamiany CNAME na A `195.2.223.12` |
| apex AAAA / CAA | NODATA / NODATA | Bez zmian |
| NS, MX | `dns106.ovh.net.`, `ns106.ovh.net.`; MX 1/5/100 odpowiednio `mx1/2/3.mail.ovh.net.` | **Bez zmian** |
| SPF, DKIM, DMARC i reszta | SPF `v=spf1 include:mx.ovh.com -all`; selektory DKIM nieustalone; `_dmarc` NXDOMAIN; SOA serial `2092386159` | Zachować wszystkie TXT/CNAME uwierzytelnienia, SRV, pozostałe rekordy i subdomeny. Nic nie importować do strefy. |

**Bezpieczeństwo poczty obecnie:** nie zmieniono żadnego rekordu ani ustawienia poczty; routing publicznego MX nadal do OVH. Nie jest to gwarancja działania po dodaniu domeny na LH. Eksport całej strefy do prywatnej kopii, SHA, selektory DKIM i potwierdzenie zewnętrznego routingu również dla poczty inicjowanej na serwerze są warunkami GO. [Multipoczta LH](https://www.lh.pl/pomoc/doc/multipoczta-co-to-jest/) opisuje organizację skrzynek; jej ustawienie samo nie potwierdza zewnętrznej dostawy. Nie testowano dostarczania wiadomości do realnych adresów.

## Katalog i konfiguracja przygotowane lokalnie

Docelowy, **proponowany** katalog wersji produkcyjnej: `/public_html/pf-release-20bc512e8b80/`. Osobny katalog techniczny `/public_html/pf-review-20bc512e8b80/`. Zawartość do przeniesienia: wyłącznie pliki z manifestu, po rozpakowaniu; archiwum, dokumentacja, Git i skrypty nie są webrootem. Ani katalogów, ani konfiguracji nie założono na serwerze.

1. Po uzyskaniu właściwego dostępu sprawdzić brak kolizji katalogu, istniejące vhosty i zrobić prywatną kopię zastanej konfiguracji. Nie nadpisywać istniejącej strony. W nowych katalogach najpierw ustawić blokadę dostępu **przed** przesłaniem treści. Skonfigurować FTPS explicit TLS z walidacją certyfikatu i `PROT P`.
2. Dla preview: [szablon Apache](../ops/lh/preview.htaccess) jako `.htaccess`, plik haseł z silnym hasłem poza public_html, poprawna pełna ścieżka. Sprawdzić, czy LH honoruje dyrektywy: HTTPS bez hasła **401**, HTTP bez dostępu, również dla bezpośredniego URL grafiki, brak listowania. Jeśli serwer ignoruje reguły lub zwraca 500, nie przesyłać treści. Dopiero potem FTPS plików i pełna weryfikacja po uwierzytelnieniu. `noindex` nie jest ochroną dostępu.
3. Dla produkcji: [oddzielny szablon](../ops/lh/production.htaccess); bez Basic Auth/noindex, ograniczenie hostów, typy AVIF/WebP, wyjątek ACME, przekierowania na kanoniczny HTTPS. Wymaga sprawdzenia modułów, AllowOverride i sposobu terminacji TLS na prawdziwym vhoście (pętle redirectów). Nie stosować w głównym public_html technicznego serwera ani nie kopiować konfiguracji preview na produkcję.
4. Paczka zawiera **jawne projekty** polityki i zasad. Publiczna instalacja bieżącego ZIP jest **zablokowana**, również pod niezabezpieczonym hostem technicznym. Po akceptacji wpisać realną datę, usunąć oznaczenia projektu zgodnie z zatwierdzonym tekstem, zmienić test wymagający wersji roboczej na sprawdzenie zaakceptowanych wersji, odbudować ZIP z nowego czystego commitu i przedstawić **nowe SHA** do GO.

## G1–G8: decyzja właściciela

| Bramka | Stan | Co domyka bramkę |
|---|---|---|
| G1 — UI | PASS dla katalogu | Zatwierdzone R04/hero, publikacja wizualizacji jako poglądowych. Sesja foto i parametry przyszłej sprzedaży nie blokują katalogu. |
| G2 — teksty i dane | OPEN | Zatwierdzić dwie konkretne strony i realną datę. W [polityce](../polityka-prywatnosci.html) §§1,3–5,7–10: administrator i obsługiwany kontakt; cel/podstawa zgody na listę, rejestr wycofania; retencja kontaktów, logów, kopii i ustawienie GA; umowy z Brevo, LH, OVH i Google, odbiorcy/podwykonawcy i podstawy transferów poza EOG. Potwierdzić opis cookies względem faktycznej konfiguracji. W [zasadach](../zasady-premiery.html) §§1–8: dobrowolna lista, DOI, faktyczny sposób wypisania i kontakt, brak rezerwacji/płatności/terminu, zdjęcia poglądowe. Nie wymaga zatwierdzenia regulaminu **sprzedaży** dla katalogu. |
| G3 — Brevo/kontakt | OPEN | Identyczny formularz i obsługa cookies. Automatyczny GET endpointu w tej sesji: 403; to nie jest wynik próby POST ani DOI. [Protokół](BREVO_ACCEPTANCE_PLAN.md): opiekun zatwierdza adresy T1/T2 i kontrolowany test bez kampanii do klientów. Weryfikacja nadawcy, zgody, pending przed DOI, strony potwierdzenia, wypisania i blokady ponownej wysyłki; odbiór i odpowiedź kontaktu. NOT RUN na rzeczywistej liście. |
| G4 — DNS i backup | OPEN | Backup źródeł i rollback WWW przygotowane; brak uwierzytelnionego pełnego eksportu OVH, potwierdzonych selektorów DKIM i porównania wszystkich rekordów. Zachować eksport poza repo i zanotować hash, datę i serial. |
| G5 — hosting/poczta | OPEN | Dostęp do technicznego katalogu, skuteczna ochrona, odbiór wszystkich plików na LH i potwierdzenie zewnętrznego routingu OVH. Nie zmieniać skrzynek, NS/MX ani Multipoczty w ciemno. |
| G6 — SSL | OPEN | A i www na IP LH nie mają poprawnego certyfikatu. Preferowana wcześniejsza instalacja/odnawianie dla obu nazw za zgodą; jeśli wyłącznie [panelowe LE po wskazaniu domeny](https://www.lh.pl/pomoc/doc/jak-uruchomic-certyfikat-ssl-lets-encrypt-na-serwerze-w-lh-pl/), wymagana akceptacja okna możliwej przerwy oraz limit czasu na rollback. |
| G7 — artefakty | PASS dla RC | Dwa czyste buildy, te same SHA, HTTP i podglądy lokalne. Po zmianie tekstu prawnego powtórzyć i odebrać nową paczkę. |
| G8 — przełączenie | OPEN | Pisemne GO właściciela dla końcowego SHA, wariantu DNS/SSL, okna i osoby uprawnionej do rollbacku. Brak zgody na przełączenie teraz. |

## Jedna checklista przełączenia po GO

1. Zakończyć G1–G7; zachować prywatny eksport OVH i backup dotychczasowych plików/konfiguracji. Ustalić operatora DNS/SSL/rollback, czas, końcowy SHA i uzyskać G8. Nie scalać do main. Nie usuwać GitHub Pages.
2. Przed T0 sprawdzić jeszcze raz strefę. Opcjonalnie obniżyć **wyłącznie WWW** do TTL 300 co najmniej poprzedni TTL + bufor przed T0. Preinstalować i zweryfikować TLS/SNI dla obu nazw na IP LH albo uzgodnić okno awaryjne. Zatwierdzić techniczny preview, zawartość katalogu i routing poczty.
3. W OVH zmienić tylko apex A i rekord www zgodnie z powyższym diffem; żadnego NS/MX/SPF/DKIM/DMARC, innego TXT/SRV ani masowego importu. Dla wariantu LE wystawić certyfikat po skierowaniu obu nazw; potwierdzić łańcuch, SAN i odnowienie. Sprawdzić z dwóch resolverów oraz authoritative, 301 → HTTPS apex, 200 na 16 stronach, 404, grafiki z SHA manifestu, formularz i cookies.
4. Sprawdzić pocztę po uzgodnieniu testowych adresów: wiadomość, odpowiedź i nagłówki; porównać całą strefę z backupem. Przy awarii TLS, poczty, plików lub formularza zatrzymać start. Dla scenariusza LE: kontrola T+5 min; przy braku prawidłowego TLS na T+10 min rollback, chyba że właściciel jawnie zatwierdzi inne okno.
5. Rollback strony: jeśli błąd tylko w plikach LH, przełączyć na wcześniejszy odebrany katalog, jeśli istnieje. Rollback DNS: przywrócić dokładnie wcześniejsze cztery A oraz CNAME www i TTL z eksportu. Nie „przywracać” całej strefy ani nie zmieniać poczty. Cache wygasa według TTL; utrzymać oba hostingi co najmniej 48 h i do potwierdzenia stabilności. Kontrole po 1 h i 24 h, potem przywrócić normalny TTL WWW.

[Stripe #16](https://github.com/pracowniarachunkowosci-debug/form/pull/16): karta i BLIK zaliczone w Sandbox. Końcowy status pełnego zwrotu BLIK i doręczenie potwierdzenia e-mail nadal otwarte. Nie są bramkami wydania katalogu. Stripe Live, sprzedaż, ceny, stock, linki testowe i rzeczywiste „Kup” pozostają wyłączone.
