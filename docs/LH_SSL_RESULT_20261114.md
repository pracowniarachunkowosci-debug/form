# Staging LH: SSL działa, prywatny runtime nadal blokuje sklep

14.11.2026, kontynuacja [PR #28](https://github.com/pracowniarachunkowosci-debug/form/pull/28#issuecomment-6876261610), bez merge i publikacji aplikacji. **HTTPS infrastruktury PASS; odbiór sklepu na LH nadal NO-GO.** Zakres: `test.pracowniaform.com`, vhost **1711054**, serwer **533947**, IP **195.2.223.12**, WWW `/public_html/pf-stage-20261114/www`.

## Rzeczywiście wykonane

1. Właściciel osobno zatwierdził dokładny TXT, walidację i sprzątanie. Sprawdzono strefę OVH i zachowano lokalny odczyt 16 istniejących rekordów. Dodano wyłącznie `_acme-challenge.test` TXT z TTL 300. Wartości wyzwania nie zapisano w repo ani komentarzach.
2. Oba autorytatywne OVH (`5.196.41.1`, `5.135.65.21`) i resolvery `1.1.1.1`, `8.8.8.8` potwierdziły oczekiwany TXT. Dopiero wtedy wznowiono istniejące zamówienie ACME. Let’s Encrypt zwróciło **Authorization result: valid**.
3. Na żądanie klienta po poprawnej autoryzacji usunięto własny TXT; następnie klient pobrał certyfikat. Wszystkie cztery DNS potwierdziły NXDOMAIN. Porównanie tabeli OVH: **16/16 wcześniejszych wierszy identycznych**. A stagingu i TXT `lh.pl` pozostały bez zmian. [Dowód cyklu DNS](staging-20261114/dns01-lifecycle.json).
4. PEM zweryfikowano OpenSSL 3.5.8: jeden SAN, zgodność klucza, kolejność dwóch pośrednich, pełny łańcuch, sslserver, nazwa i daty. Trust anchor pobrano osobno z oficjalnego LE. [Wynik prawdziwego certyfikatu](staging-20261114/pem-validation.json).
5. Właściciel osobno zatwierdził konkretny fingerprint i import do vhosta 1711054. Potwierdzono brak SSL, nazwę, katalog i action formularza `/panel/virtual/1711054/ssl`. Wprowadzono leaf / key / chain-only. **LH przyjęło zewnętrzny LE single-SAN bez `www.test`.** [Potwierdzenie panelu](staging-20261114/lh-custom-ssl-installed.jpg).
6. Przeglądarka otwiera HTTPS bez ostrzeżenia certyfikatu, z **403** pustego WWW. Python z domyślnym zaufaniem i weryfikacją hostname również otrzymał 403 Apache. To nie jest test aplikacji lub płatności.
7. Niezależny test SSL Shopper potwierdził IP, nazwę, zaufanie i kompletność łańcucha, issuer YR1, jeden SAN, daty i **ten sam numer seryjny** co lokalny PEM. [Zrzut](staging-20261114/ssl-external-check.jpg), [dane pomiaru](staging-20261114/https-verification.json).

## Certyfikat i granice pomiaru

| Pole | Potwierdzona wartość |
| --- | --- |
| SAN | Tylko `test.pracowniaform.com` |
| Wystawca | Let’s Encrypt YR1 |
| Łańcuch do LH | YR1 → Root YR (cross-signed ISRG Root X1) |
| notBefore | 14.11.2026 10:53:00 UTC |
| notAfter | 12.02.2027 10:52:59 UTC |
| Serial | `06ea3528f6bc89de83e4d07c7df519a64325` |
| SHA-256 wydanego/importowanego leaf | `2ebe179b2837de0a12476c37d111dfaabc054ab77287a01031c15fc0b9dff31a` |

Norton przechwytuje lokalny TLS: klient z zaufaniem **wyłącznie ISRG** odrzuca przedstawiony łańcuch, a klient z zaufaniem systemowym widzi wystawcę Norton i poprawną nazwę stagingu. Nie wyłączono ochrony ani walidacji. **Nie przypisujemy fingerprintu lokalnego połączenia certyfikatowi origin.** Zewnętrzny checker potwierdził issuer/serial/SAN/daty i łańcuch, ale jego UI nie udostępniało DER/fingerprintu. Bezpośrednie porównanie SHA-256 z nieinspekowanego klienta pozostaje dodatkową kontrolą, nie fikcyjnym PASS. Nie wykonano pełnego audytu szyfrów.

Klucze, konto ACME i logi są poza repo, z ACL operator/SYSTEM. Brak sekretów w WWW, Actions, zgłoszeniu i zrzutach. Klient zapisał lokalny opis odnowienia, **bez zadania harmonogramu**. Własny SSL nie odnawia się automatycznie. WACS wskazał termin po **08.01.2027**; operator powinien wtedy rozpocząć ręczne odnowienie i import, najpóźniej 30 dni przed wygaśnięciem (13.01.2027). [Checklista](LH_SSL_IMPORT_CHECKLIST.md).

## Pozostała blokada i działania niezależne

**Prywatny config/SQLite:** PHP-FPM dwukrotnie otrzymał Permission denied poza `public_html`, przy działającym zapisie WWW. Przejrzany panel nie udostępnia kompletnej alternatywy. Rekomendacja: zachować SQLite i uzyskać od LH dedykowany katalog poza wszystkimi webrootami, minimalne prawa odczytu config oraz zapisu data i bezpieczny kanał dostarczenia plików. MySQL nie rozwiązuje przechowania sekretów. [Decyzja i dokładne wymagania](LH_PRIVATE_CONFIG_DECISION.md).

O **13:00 czasu panelu** wysłano uzupełnienie **TKT-KTNHLTAY**: SSL rozwiązane, nie nadpisywać; pozostała prośba o prywatny katalog/config. [Wysłana treść](staging-20261114/lh-followup-ssl-installed.txt), [potwierdzenie](staging-20261114/lh-followup-ssl-sent.jpg). Zgłoszenie nadal otwarte, bez odpowiedzi LH w chwili odczytu. Nie ponawiano HTTP-01; przyczyna jego pierwotnego 404 nadal wymaga logów LH.

- Walidator PEM: **13/13 testów lokalnych PASS**, syntetyczne klucze posprzątane; osobno PASS prawdziwego PEM.
- [Nieaktywna propozycja Actions](LH_ACTIONS_PROPOSAL.md): szablon poza `.github/workflows`, pełne SHA akcji, kontrola pochodzenia paczki, deny-all i trzy blokady wdrożenia. **14/14 testów offline PASS**, actionlint PASS. Bez runu, sekretów i transferu.
- Ceny, stany, SKU, checkout, InPost, zdjęcia i layout nie zmieniły się. Zakupy na LH i fizycznym telefonie pozostają NOT RUN; wcześniejsze lokalne testy Stripe Sandbox to odrębny wynik.

Następny krok: LH potwierdza prywatny zasób, następnie odbiór niesekretną sondą przy zachowanej separacji. Dopiero potem config, baza testowa, ochrona stagingu, świeży build i zatwierdzony upload. **Bez produkcji, merge, Stripe Live i zmian zasobów Pracowni Rachunkowości.**
