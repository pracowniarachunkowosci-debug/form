# Pracownia Form

**WINTER 26 / ceny w Polsce:** [cennik regularny, pole na późniejszy kod i dostawa](docs/WINTER26_CENNIK_PL.md).

**Dostawa InPost na LH:** [konfiguracja mapy, wybór automatu i pierwsze ręczne nadanie](docs/INPOST_PACZKOMAT.md).

**Issue #27 / fotografie:** [przegląd pakietu i pytania identyfikacyjne](docs/ISSUE_27_PHOTO_REVIEW.md). Pakiet zawiera 26 zweryfikowanych plików, ale przypisanie do SKU pozostaje zablokowane do potwierdzenia wariantu, koloru i materiału.

**Historia — WINTER 26 / Issue #12:** [katalog, konfiguracja produktów, podglądy i warunki aktywacji](docs/WINTER26_STOREFRONT_HANDOFF.md). Ta gałąź jest draftem sklepu na bazie PR #11. Lokalny podgląd sklepu: port 8772; port 8771 poniżej należy do bazowego PR #11.

**Bieżące wydanie z 11.11.2026:** [zlecenie publikacji i testów #24](https://github.com/pracowniarachunkowosci-debug/form/issues/24) oraz [instrukcja dla operatora](docs/WINTER26_WYDANIE.md). Właściciel zlecił publikację z aktualnymi materiałami. Nie oznacza to przeprowadzenia testów z prawdziwym kontem Stripe ani wykonania przełączenia domeny. Poprzednie raporty poniżej pozostają zapisem starszych wersji.

- [Raport zmian i podglądy](docs/PUBLICATION_REPORT.md)
- [Aktualny hero z otwartą bombką — porównanie desktop/mobile](docs/HERO_CONCEPT_PREVIEW.md)
- [Audyt LH/DNS, plan migracji, rollback i checklista](docs/LH_ORANGE_MIGRATION.md)
- [Odpowiedź na recenzję PR #11 i testy cookies](docs/PR11_REVIEW_RESPONSE.md)
- [Bramki GO/NO-GO i pytania do dostawców](docs/RELEASE_READINESS.md)
- [Plan kontrolowanego testu Brevo — niewykonany](docs/BREVO_ACCEPTANCE_PLAN.md)
- [Zdjęcia produktów — oczekiwanie i plan podmiany](docs/PRODUCT_PHOTO_HANDOFF.md)
- [Commit, ZIP i hash lokalnego kandydata](docs/RELEASE_CANDIDATE.md)

Lokalny podgląd (z katalogu repozytorium):

```sh
python -m http.server 8771 --bind 127.0.0.1
```

Otwórz `http://127.0.0.1:8771/winter-26.html`. Formularz jest rzeczywistym formularzem Brevo — testy wyglądu i walidacji nie wymagają jego wysyłania. W podglądzie odrzuć analitykę.

Weryfikacja i lokalna paczka (bez uploadu):

```sh
python scripts/check_publication.py
node scripts/check_consent.cjs
python scripts/build_release.py
```

Wynik paczki: `.artifacts/pracownia-form-lh.zip`, `manifest.json` i `release.json` z identyfikacją commitu i SHA-256. Nie zawiera dokumentacji, podglądów, Git ani ustawień DNS/serwera. Publikacja wymaga osobnego zatwierdzenia fazy B. Merge do `main` może uruchomić istniejące GitHub Pages.
