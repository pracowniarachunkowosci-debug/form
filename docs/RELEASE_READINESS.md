# PR #11 — decyzje operacyjne i GO/NO-GO

**Aktualny odbiór 04.11.2026:** [wydanie #14 — 16 stron, paczka, G1–G8 i rollback](LH_RELEASE_14.md). Poniżej zachowano historyczny stan PR #11.

Stan: 03.11.2026, **NO-GO / faza A**. Nie przeprowadzono uploadu, dodawania domeny, zmian DNS/SSL ani kontaktu z dostawcami. [Audyt bazowy i rekordy rollback](LH_ORANGE_MIGRATION.md). Ten dokument doprecyzowuje warunki wykonania, nie jest zgodą na migrację.

## Bramka decyzji

| ID | Warunek GO | Stan / kto zamyka |
|---|---|---|
| G1 | Akceptacja dokładnej wersji strony i statusu zdjęć | Oczekiwanie na fotografie oraz późniejszą akceptację hero przez właściciela |
| G2 | Zatwierdzone dokumenty, rzeczywista data wejścia w życie, retencja i umowy | Projekt 03.11.2026 do decyzji właściciela; nie publikować jako zatwierdzonego |
| G3 | Brevo DOI/wypisanie/doręczanie i działający kontakt | NOT RUN; [osobny zakres zgody](BREVO_ACCEPTANCE_PLAN.md) |
| G4 | Pełny eksport DNS, znane DKIM i zależności, zatwierdzony minimalny diff WWW | Eksport OVH niepozyskany; właściciel/operator DNS |
| G5 | Odpowiedź LH o poczcie zewnętrznej i Multipoczcie dla serwera | Niepotwierdzone; potrzebna odpowiedź LH, bez zgadywania checkboxa |
| G6 | Potwierdzony certyfikat przed zmianą lub zaakceptowane okno ryzyka | Niepotwierdzone; LH + właściciel. Bez tego brak zmiany DNS |
| G7 | Czysty commit, ZIP, manifest i zgodny SHA-256 | Poprzednia paczka w `RELEASE_CANDIDATE.md` jest archiwalna po podmianie hero; przed wdrożeniem zbudować i odebrać nową z zatwierdzoną grafiką i dokumentami |
| G8 | Osobna zgoda fazy B, termin, operator i osoba decydująca o rollback | Brak; akceptacja PR/zdjęcia nie zastępuje zgody na hosting/DNS |

Wszystkie G1–G8 muszą być zamknięte. Obecna paczka jest kandydatem do przeglądu, nie do wgrania. Zatwierdzenie zapowiedzi nie uruchamia sprzedaży. Fotografie/parametry/SKU/GPSR/płatności mają odrębny odbiór przed sprzedażą.

## Pytania do LH — gotowe do przekazania po zgodzie

Kontekst: Orange `serwer533947`, strona statyczna, IP `195.2.223.12`, domena `pracowniaform.com`, NS/MX pozostają w OVH, brak skrzynek LH.

1. Jaka dokładna opcja dodania domeny i ustawienie Multipoczty zapewnią **zewnętrzną obsługę poczty OVH**, również dla wiadomości inicjowanych na serwerze LH? Czy wymagane jest wyłączenie lokalnego routingu domeny przez support? Prosimy o instrukcję dla tego pakietu i potwierdzenie braku automatycznej zmiany MX/SPF.
2. Czy Orange pozwala zainstalować certyfikat dla apex i www **przed przełączeniem A**, np. przez DNS-01 albo import istniejącego certyfikatu z własnym kluczem? Jaki dokładny tryb i sposób odnawiania? Nie mamy klucza certyfikatu GitHub Pages i nie zakładamy jego eksportu.
3. Jeżeli tylko panelowe Let's Encrypt po zmianie DNS: jaki typowy czas, sposób diagnostyki, ponawiania i ograniczenia? Czy `www CNAME → apex` jest obsługiwane, czy panel wymaga osobnego A? Potrzebna odpowiedź przed finalizacją diffu DNS.
4. Czy techniczny HTTPS dla podkatalogu wydania działa z poprawnym certyfikatem i czy można chronić podgląd oraz wyłączyć listowanie bez wpływu na ACME/produkcyjną domenę? Potwierdzić explicit FTPS i szyfrowanie kanału danych.
5. Jakie są rzeczywiste okresy logów WWW, kopii i tryb powierzenia danych dla zakupionego Orange?

Wynik ma zawierać datę, numer zgłoszenia i jednoznaczną instrukcję, bez danych dostępowych. **Nie wysłano tych pytań.** Publiczna [instrukcja Multipoczty](https://www.lh.pl/pomoc/doc/multipoczta-co-to-jest/) opisuje organizację skrzynek, a nie gwarancję routingu remote-mail. [Instrukcja Let's Encrypt](https://www.lh.pl/pomoc/doc/jak-uruchomic-certyfikat-ssl-lets-encrypt-na-serwerze-w-lh-pl/) wymaga wskazania apex/www na LH przed wystawieniem; nie potwierdza dla tego konta wcześniejszego DNS-01/importu.

## Pełny eksport OVH — odczyt przed fazą B

Właściciel loguje się osobiście do właściwego konta. W Web Cloud → domena `pracowniaform.com` → strefa DNS należy pobrać pełny eksport albo skopiować pełną reprezentację tekstową i zamknąć bez zapisu. Alternatywa dla wcześniej uprawnionego operatora: odczyt `GET /domain/zone/pracowniaform.com/export` w API OVH; bez tworzenia nowych kluczy na potrzeby tego zadania. [Dokumentacja OVH](https://docs.ovhcloud.com/en/guides/web-cloud/domains/faq-domain-dns) rozróżnia rekordy strefy i serwery nazw.

Eksport zapisać w prywatnym katalogu poza repo/WWW; obliczyć SHA-256, odnotować SOA serial, datę, liczbę rekordów i operatora. W raporcie wystarczą metadane i zredagowana tabela. Nie usuwać nieznanych rekordów. Zebrać NS, SOA, A, AAAA, CNAME, MX, TXT, CAA, SRV oraz wszystkie subdomeny. Rekordy SPF mogą być na subdomenach; DKIM może być TXT lub CNAME, z wieloma selektorami. Selektory dodatkowo ustalić z `DKIM-Signature: d=...; s=...` kontrolowanej wiadomości OVH i Brevo. Jeśli brak eksportu/selektorów, G4 pozostaje NO-GO; zgadywanie `default` nie jest audytem DKIM.

Z zatwierdzonego eksportu przygotować diff dopuszczający wyłącznie: cztery apex A GitHub → jeden A LH; www CNAME GitHub → uzgodniony z LH CNAME/apex lub A; opcjonalnie czasową zmianę TTL tych rekordów. Każdy diff MX/SPF/DKIM/DMARC/NS/innego TXT/SRV oznacza STOP. Ponownie porównać pełną strefę tuż przed i po zmianie. Nie używać importu całej strefy do zmiany dwóch nazw.

## SSL i kontrolowane okno — wariant do zatwierdzenia

**Preferowany wariant:** LH potwierdza wcześniejsze wystawienie/instalację certyfikatu; po zgodzie fazy B sprawdzić SNI/łańcuch/nazwy dla `pracowniaform.com` i `www.pracowniaform.com` na IP LH przed publiczną zmianą DNS. Weryfikować certyfikat, bez `-k`/ignorowania ostrzeżeń. Bez pisemnego potwierdzenia nie zakładamy, że ten wariant jest możliwy.

**Wariant z ryzykiem:** jeśli dostępne jest wyłącznie panelowe LE po DNS, właściciel musi świadomie zaakceptować możliwą przerwę HTTPS. Propozycja (nie SLA): operator i osoba decydująca dostępni przez całe okno; stary GitHub działa; pełny eksport i gotowe wartości rollback pod ręką; TTL WWW 300 ustawione co najmniej poprzedni TTL 3600 + bufor wcześniej. Kontrola przed T0: techniczny preview, katalog, FTPS, poczta remote, testy i komplet danych.

- T0: minimalny zatwierdzony diff DNS, zapis godziny. Sprawdzenie authoritative oraz 1.1.1.1/8.8.8.8.
- Gdy LH widzi oba hosty na właściwym IP: jedna próba wystawienia zgodnie z panelem; nie wykonywać serii automatycznych ponowień.
- T+5 min: jeśli certyfikatu brak, diagnoza komunikatu/statusu, operator informuje właściciela.
- T+10 min: jeśli którekolwiek HTTPS nadal ma niepoprawny certyfikat lub brak jednoznacznej ścieżki naprawy, decyzja o rollback według wcześniej zaakceptowanej reguły. Nie przedłużać okna bez zgody.
- Przywrócenie dawnych A/CNAME **nie kończy awarii od razu**: cache może nadal kierować na LH przez pozostały TTL, a klient z istniejącą sesją dłużej. Nie wyłączać LH/starego Pages w trakcie mieszanego ruchu. Jeśli takie ryzyko nie jest akceptowalne, nie wykonywać wariantu z DNS→SSL.

Przekierowanie na HTTP, obejście błędu certyfikatu czy sam HTML „przerwa techniczna” nie rozwiązują problemu HTTPS. Pełne NS/MX nie są elementem rollback WWW. Nie obiecywać zerowej przerwy.

## Po zatwierdzonym przełączeniu — checklista odbioru

- [ ] Publiczne A/AAAA/CNAME na obu nazwach i dwóch resolverach zgodne; strefa poza zatwierdzonym WWW identyczna z eksportem.
- [ ] Poprawny TLS/SAN/łańcuch/data na apex i www, bez pętli przekierowań; jeden kanoniczny host; odnowienie certyfikatu udokumentowane.
- [ ] Wszystkie pliki ZIP/manifestu na właściwym katalogu; 16 stron i zasoby 200, nieistniejąca ścieżka 404, AVIF/WebP poprawne MIME, brak listowania.
- [ ] R04 desktop/mobile, brak overflow, menu/klawiatura, zdjęcia zgodne z odbiorem; żadnego checkoutu/Stripe.
- [ ] Produkcja bez testowej autoryzacji/noindex; canonical/sitemap/robots właściwe; techniczna kopia chroniona osobno.
- [ ] Cookies: nowy profil bez GA; odmowa i refresh bez GA; akceptacja/cofnięcie i drugi tab w uzgodnionym teście; wycofanie nie kasuje danych formularza.
- [ ] Minimalny zatwierdzony test Brevo na docelowym origin; DOI, potwierdzenie, wypisanie i wykluczenie z wysyłki.
- [ ] Kontrolowana poczta przychodząca/odpowiedź, SPF/DKIM/DMARC z nagłówka, brak routingu do lokalnej pustej poczty LH.
- [ ] Zapis protokołu: operator, czas, commit, hash ZIP, wyniki i decyzja; monitorowanie po 1 h/24 h, stare wydanie minimum 48 h; TTL przywrócone po stabilizacji.

Wystąpienie błędu TLS, routingu poczty, zapisu/zgód albo rozbieżności plików oznacza NO-GO do zamknięcia odbioru, diagnozę i wykonanie zatwierdzonej reguły rollback. Ta lista nie została wykonana na produkcji.
