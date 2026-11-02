# Lokalny prototyp WooCommerce R04

Bezpłatny, odtwarzalny eksperyment administracji wariantami. Nie jest wdrożeniem sklepu. Motyw używa palety R04 z PR #5; nie zastępuje zatwierdzonej strony ani nie proponuje nowego kierunku wizualnego.

## Uruchomienie

Wymagany Node.js **24.18 lub nowszy** (wymaganie przypiętej paczki Playground), npm i internet do pobrania oficjalnych paczek WordPress/WooCommerce. Bez Dockera, własnego serwera PHP, kont dostawców i abonamentów.

```powershell
cd prototypes/woo
npm ci --ignore-scripts
npm test
npm start
```

Otwórz `http://127.0.0.1:8774/`. Adres edytora produktu jest wypisywany po inicjalizacji. Jeżeli pojawi się ekran logowania, standardowe dane jednorazowej instancji Playground to `admin` / `password`; nie używać ich na żadnym prawdziwym serwerze. Pierwszy start może trwać kilka minut. Zatrzymanie: Ctrl+C. Port musi być wolny; nie uruchamiać dwóch instancji jednocześnie. `node start.mjs --test --keep` wykonuje testy i zachowuje serwer do przeglądu.

Każdy start tworzy świeżą, nietrwałą bazę **SQLite**. Zmiany panelu znikają po zakończeniu procesu. Zrzuty wyników trafiają do ignorowanego `test-results/`. Środowisko ma automatyczne lokalne logowanie administratora i nasłuchuje wyłącznie na `127.0.0.1`. Nie udostępniać przez tunel, proxy ani publiczny hosting. Lokalny użytkownik komputera ma dostęp do tej demonstracji.

Przypięto Playground CLI 3.1.62, WordPress 7.1.4, WooCommerce 11.2.1 i PHP 8.3. Gdy firmowe proxy wymaga własnego zaufanego CA, użyć `NODE_EXTRA_CA_CERTS` z dostarczonym certyfikatem; **nie wyłączać weryfikacji TLS**. Lokalny katalog `.local/` i zależności nie należą do PR.

## Zakres i ograniczenia

- Jeden jawnie syntetyczny produkt, SKU `PF-TEST-PARENT`, warianty A/B, stany 3/0, techniczna cena 1 PLN. Brak rzeczywistych zdjęć, cen i kolorów kolekcji.
- Natywny panel Woo do wariantów i magazynu. Test PHP zapisuje/odczytuje stan i przywraca wartość początkową; test HTTP sprawdza stronę oraz blokadę Store API checkout.
- `local-guard.php` blokuje zakup, bramki, pocztę i żądania WordPress HTTP API. Nie zainstalowano modułów P24/InPost ani nie skonfigurowano sekretów. To zabezpieczenie aplikacji demonstracyjnej, nie systemowa zapora ruchu przeglądarki.
- `noindex`, `DISABLE_WP_CRON`, blokady i automatyczne logowanie są **wyłącznie lokalne**. Nie przenosić ich do strony publikacyjnej PR #5 ani przyszłego sklepu.
- Próba Action Scheduler raportuje oddzielny rzeczywisty wynik; nie zalicza nieuruchomionego zadania. Uruchamiane jest sześć workerów zalecanych przez Playground, ale SQLite nadal nie kwalifikuje produkcyjnego MySQL, blokad, rezerwacji równoległych, HPOS, cron ani wydajności.
- `npm test` sprawdza lokalny model produktu i blokady. Zielony wynik nie oznacza zaliczenia integracji płatności, przewozu lub kolejki. Rzeczywisty wynik próby kolejki odczytać w `test-results/verification.json`.

Przed użyciem produkcyjnym potrzebny osobny etap na MySQL i wybranym hostingu: kolejka bez ruchu, restore, konkurencja ostatniej sztuki, timeouty/retry, integracje sandbox i odbiór bezpieczeństwa. [Plan sandbox](../../docs/WOO_SANDBOX_PLAN.md) opisuje ten etap bez jego uruchamiania.
