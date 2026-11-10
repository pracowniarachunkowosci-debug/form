"""Checks for the policy applied to entire packs, including mixed carts and delivery."""
import json
import unittest
from pathlib import Path
from winter26_pricing import quote

ROOT = Path(__file__).resolve().parents[1]
STAR, VASE, MED = "knitted-star", "full-soft", "knitted-medallion"
CODE = "WINTER10"


class PricingTests(unittest.TestCase):
    def test_agreed_totals(self):
        for size, usual, coded in [(1, 5000, 4000), (2, 8400, 7400), (4, 15000, 14000),
                                   (6, 22000, 21000), (8, 29000, 28000)]:
            with self.subTest(size=size):
                pack = ([VASE, STAR, MED] * 3)[:size]
                self.assertEqual(quote([pack])["merchandiseGrosz"], usual)
                q = quote([pack], CODE)
                self.assertEqual(q["discountGrosz"], usual-coded)
                self.assertEqual(q["merchandiseGrosz"], coded)
                self.assertEqual(q["totalGrosz"], coded if size >= 6 else None)

    def test_two_packs_plus_single(self):
        packs = [[STAR]*4, [MED]*2, [VASE]]
        q = quote(packs, CODE)
        self.assertEqual((q["regularGrosz"], q["discountGrosz"], q["totalGrosz"]), (28400, 3000, 25400))
        self.assertEqual(quote(packs)["shippingGrosz"], 0)
        self.assertEqual(quote([[VASE]] * 6, CODE)["totalGrosz"], 24000)
        self.assertIsNone(quote([[STAR]*4, [VASE]], CODE)["shippingGrosz"])

    def test_separate_singles_versus_duet(self):
        for code, singles, duet in [(None, 10000, 8400), (CODE, 8000, 7400)]:
            self.assertEqual(quote([[VASE], [STAR]], code)["merchandiseGrosz"], singles)
            self.assertEqual(quote([[VASE, STAR]], code)["merchandiseGrosz"], duet)

    def test_bad_code_size_or_model(self):
        for packs, code in [([[VASE]*6], "INVALID"), ([[STAR]*3], CODE), ([["helix", STAR]], CODE),
                            ([], CODE), ([[]], CODE)]:
            with self.assertRaises(ValueError):
                quote(packs, code)

    def test_catalog_model_ids(self):
        catalog = json.loads((ROOT / "data/winter26-products.json").read_text(encoding="utf-8"))
        pricing = json.loads((ROOT / "data/winter26-pricing-pl.json").read_text(encoding="utf-8"))
        allowed = set(pricing["eligibleModelIds"])
        self.assertEqual(allowed, {VASE, STAR, MED})
        self.assertLessEqual(allowed, {p["id"] for p in catalog["products"] if p["type"] == "pojedynczy"})


if __name__ == "__main__":
    unittest.main()
