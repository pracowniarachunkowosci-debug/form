# Pracownia Form

Statyczna strona HTML/CSS/JS. Gałąź publikacyjna LH zawiera zatwierdzony hybrydowy WINTER AFTER DARK R04; pozostaje draftem bez zgody na wdrożenie.

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
