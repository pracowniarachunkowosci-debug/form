"""Checks for the policy applied to entire packs, including mixed carts and delivery."""
import json
import unittest
from pathlib import Path
from winter26_pricing import quote

ROOT = Path(__file__).resolve().parents[1]
STAR, VASE, MED = "knitted-star", "full-soft", "knitted-medallion"
CODE = "WINTER10"


class PricingTests(unittest.TestCase):
    def test_regular_prices_and_no_active_coupon(self):
        for n, price in [(1,5000),(2,8400),(4,15000),(6,22000),(8,29000)]:
            packs = [([VASE, STAR, MED] * 3)[:n]]
            with self.subTest(size=n):
                for code in (None, ""):
                    q = quote(packs,code)
                    self.assertEqual(q["merchandiseGrosz"],price)
                    self.assertEqual(q["discountGrosz"],0)
                    self.assertEqual(q["totalGrosz"],price if n>=6 else None)
                with self.assertRaises(ValueError):
                    quote(packs,CODE)

    def test_mixed_basket_and_delivery(self):
        self.assertEqual(quote([[STAR]*4, [MED]*2, [VASE]])["totalGrosz"],28400)
        self.assertEqual(quote([[STAR]*4, [MED]*2])["totalGrosz"],23400)
        self.assertEqual(quote([[VASE],[VASE]])["merchandiseGrosz"],10000)
        self.assertEqual(quote([[VASE,VASE]])["merchandiseGrosz"],8400)
        self.assertIsNone(quote([[STAR]*4,[VASE]])["shippingGrosz"])

    def test_bad_code_size_or_model(self):
        for packs, code in [([[VASE]*6], "INVALID"), ([[STAR]*3], None), ([["helix", STAR]], None),
                            ([], None), ([[]], None)]:
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
