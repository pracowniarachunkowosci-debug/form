# P0 — harmonogram i dyżur pf26

Status: gotowy plan i pliki instalacyjne. **Nie zainstalowano ani nie uruchomiono na Uberspace. Nie utworzono konta monitora i nie wysłano e-maila.** Właściciel wybrał e-mail przez zewnętrzny monitoring. Nie konfigurujemy poczty domeny ani serwera.

## Konfiguracja do wykonania dopiero po osobnej zgodzie na staging

1. Usługa użytkownika `pf26-reconcile.service` uruchamia istniejący CLI `--once --limit 1`. Timer uruchamia ją na początku każdej minuty. Systemd nie uruchamia równoległych egzemplarzy tej samej usługi; dodatkowo działa `flock` procesu i 120-sekundowa blokada w SQLite. Pojedyncza kontrola ma maksymalnie sześć żądań po 14 s. Limit usługi wynosi 110 s. Przerwanie procesu nie zwalnia rezerwacji; po wygaśnięciu blokady następuje odzyskanie z tym samym kluczem.
2. `OnFailure` wywołuje osobny sygnał awarii. Obejmuje kod 1, kod 2 (eskalacja/kolejka opóźniona ponad 5 minut), timeout, brak PHP lub nieudany start. Nie ustawiamy `SuccessExitStatus=2`. Po zdrowym przebiegu wysyłany jest sygnał sukcesu.
3. Konkretny monitor proponowany dla tego planu: **Healthchecks.io**, projekt właściciela `Pracownia Form`, check `pf26-reconcile-sandbox`. Tryb Simple: **Period 1 minuta, Grace 3 minuty**. Brak heartbeat daje alarm po 4 minutach od ostatniego sukcesu; `/fail` daje alarm od razu po odebraniu. Healthcheck nie zależy od działania samego Uberspace. Nie ustawiamy publicznego endpointu diagnostycznego ani wyjątku Basic Auth.
4. Właściciel dodaje i potwierdza własny adres e-mail w monitorze, przypina integrację do checka i włącza godzinne przypomnienia o trwającym alarmie. Adresu nie publikujemy. Pozostaje do ustawienia w monitorze podczas wdrożenia, nie w kodzie.
5. Prywatne pliki `config/reconcile-monitor-success.curl` i `config/reconcile-monitor-failure.curl`, uprawnienia 0400, zawierają po jednej dyrektywie `url = "…"`. Pierwszy zawiera rzeczywisty HTTPS Ping URL checka, drugi ten sam URL z `/fail`. Są to dane dostępowe monitora — nie trafiają do Git, paczek, argumentów procesów ani logów. Nie dodawać `insecure`, `location`, danych body lub nagłówków autoryzacji Stripe. Do monitora trafia wyłącznie sygnał sukces/awaria, bez zamówień i treści logów.

## Dokładne rozmieszczenie

| Źródło | Cel po zatwierdzeniu stagingu |
|---|---|
| `scripts/reconcile-reservations.php` | `/var/www/virtual/pf26/winter26/app/scripts/reconcile-reservations.php` |
| `ops/p0/reconcile-tick.sh` | `/var/www/virtual/pf26/winter26/app/scripts/reconcile-tick.sh` |
| `ops/p0/reconcile-notify.sh` | `/var/www/virtual/pf26/winter26/app/scripts/reconcile-notify.sh` |
| Trzy pliki `.service`/`.timer` | `/home/pf26/.config/systemd/user/` |
| Konfiguracja aplikacji | Istniejący `/home/pf26/winter26/config/test.json`, bez zmian |
| Blokada procesu | `/home/pf26/winter26/runtime/cache/reconcile.lock` |
| Ostatni wynik | `/home/pf26/winter26/runtime/logs/reconcile-latest.ndjson`, 0600 |

Skrypty są poza `app/public`, katalogi prywatne 0700. Timer używa loginowego środowiska konta i przed pracą wymaga PHP **8.5**. To nie zmienia wybranej wersji PHP ani FPM. Trwała historia każdej rezerwacji pozostaje w `reservation_history`; nadpisywanie ostatniego technicznego wyniku nie usuwa historii zdarzeń.

Po migracji, kopii i kontroli SHA (polecenia **do przyszłego wdrożenia**, nie wykonane teraz):

```sh
systemd-analyze --user verify ~/.config/systemd/user/pf26-reconcile.service ~/.config/systemd/user/pf26-reconcile.timer ~/.config/systemd/user/pf26-reconcile-alert.service
systemctl --user daemon-reload
systemctl --user start pf26-reconcile.service
systemctl --user enable --now pf26-reconcile.timer
systemctl --user list-timers pf26-reconcile.timer
```

Nie nadpisywać istniejących jednostek o tych nazwach bez porównania. Nie włączać równolegle drugiego crona dla tego samego zadania. Pakiet nie uruchamia tych poleceń sam.

## Odbiór monitoringu — warunek wznowienia checkoutu

| Próba | Oczekiwany dowód |
|---|---|
| Zdrowy przebieg bez aktywnych rezerwacji | Exit 0, monitor Up, PHP 8.5 |
| Osobny test sygnału `/fail` (bez żądania do Stripe) | E-mail odebrany przez właściciela, zapis czasu |
| Brak sygnałów przez 4 minuty | E-mail o braku heartbeat, także gdy proces nie startuje |
| Ponowny zdrowy sygnał | Powiadomienie o odzyskaniu, monitor Up |
| Lokalna syntetyczna eskalacja | CLI exit 2, bez sygnału sukcesu |
| Kolejka syntetyczna spóźniona >300 s | `backlogAlert=true`, exit 2 |

Pierwsze trzy testy zewnętrzne są **NOT RUN** do osobnej zgody na monitoring/staging. Nie testujemy awarii przez zmianę prawdziwego klucza Stripe ani wpisy w rzeczywistym ledgerze. Check zewnętrzny musi zostać odebrany przed otwarciem checkoutu. Test zatrzymania timera wykonywać w oknie serwisowym z wstrzymanymi nowymi checkoutami.

## Operator i kolejność obsługi

- Odbiorca i właściciel incydentu: właściciel Pracowni Form. Podczas uzgodnionych godzin testów sprawdza alarm w ciągu 15 minut; poza nimi checkout nie powinien być udostępniony bez wyznaczonego zastępstwa. Nie zakładamy nieistniejącego dyżuru 24/7. Zastępca: osoba wyznaczona przez właściciela (przy przekazaniu projektu może to być Dawid).
- Najpierw odczyt statusu: `php /var/www/virtual/pf26/winter26/app/scripts/reconcile-reservations.php --config /home/pf26/winter26/config/test.json --status`. Potem dla konkretnej rezerwacji `--status --order IDENTYFIKATOR --history`. Nie wklejać pełnych prywatnych wyników do publicznych Issue.
- Przy awarii procesu: `systemctl --user status pf26-reconcile.service` i `journalctl --user -u pf26-reconcile.service`; sprawdzić wersję PHP, dostęp do prywatnych plików i bazę. Nie seedować, nie resetować, nie zerować blokad ręcznie. Najpierw ustalić przyczynę.
- Przy nieznanym Stripe: w Sandbox Dashboard odnaleźć próbę po zapisanym Request-Id oraz metadanych `orderId`/`client_reference_id`. Gdy istnieje sesja, użyć `--once --order IDENTYFIKATOR --session cs_test_…`. CLI wykonuje GET i sprawdza kwotę, walutę, tryb, powiązanie zamówienia oraz punkt odbioru. Polecenie nie tworzy sesji.
- Jeśli sesja jest opłacona, uzgodnienie zapisze paid. Gdy terminalnie expired/unpaid, zwolni raz. Pending/open pozostają zarezerwowane. Sprzeczność po wcześniejszym zwolnieniu wymaga review i decyzji operatora; nie wykonuje się kolejnego ruchu magazynowego.
- Po 23 h pierwszej próby nie wysyłamy już POST. Po co najmniej 24 h Stripe może usunąć klucz. Ani stary, ani nowy klucz nie służy do zgadywania wyniku. Pusta lista lub odpowiedź 404 nie wystarcza. Przy nierozstrzygniętym wyniku: kontakt operatora z pomocą Stripe, bez przekazywania sekretów; rezerwacja pozostaje widoczna i monitorowana. Brak `force release`.
- Gdy alarm nie daje się rozstrzygnąć w 30 minut, właściciel przekazuje go osobie technicznej i rozważa wstrzymanie nowych checkoutów. Nie kasować historii, nie zamykać alarmu ręcznie jako zdrowego. Po rozwiązaniu zanotować dowód i czas, sprawdzić status oraz prawidłowe powiadomienie recovery.

## Źródła zweryfikowane 2026-11-15

- [Uberspace 8 — systemd użytkownika i timery](https://u8manual.uberspace.de/services_systemd/)
- [Healthchecks — harmonogram i czas tolerancji](https://healthchecks.io/docs/configuring_checks/)
- [Healthchecks — sygnał awarii](https://healthchecks.io/docs/signaling_failures/)
- [Healthchecks — e-mail i godzinne przypomnienia](https://healthchecks.io/docs/configuring_notifications/)
- [Stripe — retencja i identyczne parametry](https://docs.stripe.com/api/idempotent_requests)
- [Stripe — uzgodnienie po nieznanym wyniku](https://docs.stripe.com/error-low-level)
