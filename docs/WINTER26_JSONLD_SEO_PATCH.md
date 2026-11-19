# WINTER 26 — plan uporządkowanych danych dla ofert Google

**Status: specyfikacja techniczna do wdrożenia; nie wdrożono na produkcji.**  
Źródło audytu: fragment JSON-LD strony `/sklep/winter-knitted-star.html` przekazany przez właściciela 19.11.2026.

## 1. Stan obecnego znacznika KNITTED STAR

Istnieją już:

- `ItemPage`, `Product`, `Offer` i `BreadcrumbList`;
- cena `50.00 PLN`;
- `availability: OnlineOnly`;
- sprzedawca odwołujący się do `https://pracowniaform.com/#organization`;
- materiał PLA i opis wykończeń.

Brakuje:

- `Offer.hasMerchantReturnPolicy`;
- `Offer.shippingDetails`.

W `Offer.description` jest informacja o nadaniu maksymalnie w ciągu 7 dni roboczych od potwierdzenia płatności. To odpowiada zatwierdzonemu maksymalnemu terminowi. Treść widoczna dla klienta powinna dodatkowo komunikować typowy czas realizacji: „Zamówienia nadajemy zazwyczaj w ciągu 3 dni roboczych, maksymalnie w ciągu 7 dni roboczych od potwierdzenia płatności”. Nie zmieniać tego na termin 2–3 dni ani na stałą datę 1 grudnia.

## 2. Wspólna polityka zwrotów

Zdefiniować jeden obiekt `MerchantReturnPolicy` pod istniejącym węzłem `Organization` o identyfikatorze `https://pracowniaform.com/#organization`:

```json
{
  "@type": "MerchantReturnPolicy",
  "@id": "https://pracowniaform.com/#return-policy",
  "applicableCountry": "PL",
  "returnPolicyCountry": "PL",
  "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
  "merchantReturnDays": 14,
  "returnMethod": "https://schema.org/ReturnByMail",
  "returnFees": "https://schema.org/ReturnFeesCustomerResponsibility",
  "customerRemorseReturnFees": "https://schema.org/ReturnFeesCustomerResponsibility",
  "itemDefectReturnFees": "https://schema.org/FreeReturn"
}
```

Znaczenie:
- zwykłe ustawowe odstąpienie: kupujący ponosi bezpośredni koszt odesłania, o ile został o tym poinformowany przed zawarciem umowy;
- reklamacja z tytułu niezgodności towaru z umową: koszt zwrotu/odbioru po stronie sprzedawcy;
- 14-dniowe prawo odstąpienia pozostaje zachowane;
- nie dodawać `returnShippingFeesAmount`, ponieważ sklep nie pobiera od kupującego stałej opłaty za zwrot — kupujący sam organizuje i opłaca przesyłkę.

W każdej ofercie odwołać się do wspólnej polityki:

```json
"hasMerchantReturnPolicy": {
  "@id": "https://pracowniaform.com/#return-policy"
}
```

## 3. Jedyna metoda dostawy — Paczkomat InPost

**Decyzja właściciela z 16.11.2026: Paczkomat InPost pozostaje jedyną metodą dostawy. Kurier InPost został wycofany.**

Dostawa zależy od łącznej liczby ozdób w całym zamówieniu, a nie od wartości koszyka. Google obsługuje `numItems` w `ShippingConditions` typu `ShippingService`; nie zastępować tego progiem wartości zamówienia.

Zdefiniować pod `Organization.hasShippingService` jeden obiekt:

```json
{
  "@type": "ShippingService",
  "@id": "https://pracowniaform.com/#shipping-locker",
  "name": "Paczkomat InPost",
  "fulfillmentType": "https://schema.org/FulfillmentTypeCollectionPoint",
  "shippingConditions": [
    {
      "@type": "ShippingConditions",
      "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "PL"
      },
      "numItems": {
        "@type": "QuantitativeValue",
        "minValue": 1,
        "maxValue": 5,
        "unitCode": "H87"
      },
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": 18.49,
        "currency": "PLN"
      }
    },
    {
      "@type": "ShippingConditions",
      "shippingDestination": {
        "@type": "DefinedRegion",
        "addressCountry": "PL"
      },
      "numItems": {
        "@type": "QuantitativeValue",
        "minValue": 6,
        "unitCode": "H87"
      },
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": 0,
        "currency": "PLN"
      }
    }
  ]
}
```

W każdej ofercie dodaj jedno odwołanie:

```json
"shippingDetails": {
  "@type": "OfferShippingDetails",
  "hasShippingService": {
    "@id": "https://pracowniaform.com/#shipping-locker"
  }
}
```

`ShippingConditions.numItems` opisuje liczbę ozdób łącznie, nie liczbę pozycji koszyka. Zestawy 2 + 4 oznaczają 6 sztuk i kwalifikują się do bezpłatnej dostawy.

Nie twórz obiektu dla kuriera ani nie pozostawiaj kuriera jako alternatywnej metody w JSON-LD, widocznej stronie dostawy lub opisie checkoutu.

## 4. Czas nadania — nie mylić z czasem przewozu

Decyzja właściciela z 16.11.2026:
- typowy czas komunikowany klientowi: zazwyczaj 3 dni robocze;
- maksymalny termin nadania: 7 dni roboczych od potwierdzenia płatności.

To czas przygotowania i nadania, nie gwarantowany czas doręczenia przez InPost.

Widoczny tekst strony i `Offer.description` powinny być spójne. Zalecane brzmienie:

„Zamówienia nadajemy zazwyczaj w ciągu 3 dni roboczych, maksymalnie w ciągu 7 dni roboczych od potwierdzenia płatności.”

Nie używać:
- daty startu 1 grudnia jako ogólnej zasady;
- obietnicy nadania w 2–3 dni robocze;
- niepotwierdzonego czasu doręczenia;
- `deliveryTime`, `handlingTime` ani `transitTime`, dopóki ich semantyka i dokładny zakres nie zostaną potwierdzone dla aktualnego procesu. Nie kodować typowych 3 dni jako minimalnego terminu gwarantowanego.

## 5. Miejsce implementacji

Google zaleca standardową politykę zwrotów i dostawy na poziomie `Organization`, a z poziomu `Offer` — odwołania przez `@id`. Wspólne obiekty powinny być zdefiniowane na jednej kanonicznej stronie/znaczniku Organization, a oferty powinny się do nich odwoływać.

**Blokada źródłowa:** w bieżących gałęziach repozytorium `form` nie znaleziono pliku źródłowego odpowiadającego opublikowanemu adresowi `/sklep/winter-knitted-star.html` ani znacznika `application/ld+json` z przekazanego fragmentu. Plik `winter-knitted-star.html` w PR #28 jest inną, chronioną wersją stagingową z `noindex`; nie wolno traktować go jako źródła produkcyjnej strony `/sklep/`. Nie edytować go w celu pozornego naprawienia aktualnego raportu Search Console.

Przed wdrożeniem trzeba odzyskać właściwe źródła produkcyjne:
- pełny plik strony `/sklep/winter-knitted-star.html`;
- pełny plik strony `/sklep/winter-knitted-medallion.html`;
- istniejący kanoniczny znacznik `Organization` z `https://pracowniaform.com/#organization` (np. ze strony głównej lub strony polityk).

Następnie dodać wspólne obiekty Organization, odwołanie do polityki zwrotów i jedynej metody dostawy w obu ofertach oraz uzgodnić widoczne opisy dostawy/zwrotów. Zachować pozostałe dane Product, Offer, ItemPage i BreadcrumbList bez niepotrzebnego przepisywania.

## 6. Walidacja i publikacja

1. Walidować składnię JSON-LD i relacje `@id`.
2. Sprawdzić zgodność tekstów widocznych na stronie z polityką, stawką i terminem nadania.
3. Uruchomić Google Rich Results Test dla obu adresów.
4. Po zatwierdzonym wdrożeniu uruchomić sprawdzenie adresów w Search Console i poprosić o ponowne indeksowanie / weryfikację.
5. Oczekiwać na ponowne pobranie stron przez Google; zniknięcie ostrzeżeń nie następuje natychmiast.

Źródła Google:
- Merchant listings: https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- Merchant shipping policy / `ShippingService`: https://developers.google.com/search/docs/appearance/structured-data/shipping-policy
- Merchant return policy: https://developers.google.com/search/docs/appearance/structured-data/return-policy

**Zakres nie obejmuje** dopisywania opinii, ocen, niepotwierdzonych czasów doręczenia ani zmiany cen, dostępności, SKU, zdjęć, checkoutu lub statusu Live.
