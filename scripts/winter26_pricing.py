"""Internal WINTER 26 PL quotes in gross grosz. No checkout or promotion is activated."""
import json
from pathlib import Path

_POLICY = json.loads((Path(__file__).resolve().parents[1] / "data/winter26-pricing-pl.json").read_text(encoding="utf-8"))


def quote(packs, code=None):
    """One sequence of registered model IDs per selected pack; a single has one slot.

    Keep explicit pack boundaries: four separate singles are not a quartet.
    Caller validates SKU/stock separately. Never supply money from the browser.
    """
    coupon = _POLICY["coupon"]
    if code is not None and (not isinstance(code, str) or code.strip().upper() != coupon["code"]):
        raise ValueError("Nieznany kod rabatowy.")
    if not isinstance(packs, (list, tuple)) or not packs:
        raise ValueError("Pusty lub niepoprawny koszyk.")
    count = regular = discount = 0
    for pack in packs:
        if not isinstance(pack, (list, tuple)) or any(model not in _POLICY["eligibleModelIds"] for model in pack):
            raise ValueError("Wzór poza cennikiem WINTER 26.")
        size = len(pack)
        if size == 1:
            regular += _POLICY["singleGrossGrosz"]
        elif str(size) in _POLICY["setGrossGrosz"]:
            regular += _POLICY["setGrossGrosz"][str(size)]
        else:
            raise ValueError("Nieobsługiwana liczba ozdób w zestawie.")
        if code is not None:
            discount += coupon["discountPerPackGrosz"]
        count += size
    merchandise = regular - discount
    shipping = 0 if count >= _POLICY["freeCourierFromOrnaments"] else _POLICY["smallOrderCourierGrosz"]
    return {"regularGrosz": regular, "discountGrosz": discount, "merchandiseGrosz": merchandise,
            "shippingGrosz": shipping, "totalGrosz": None if shipping is None else merchandise + shipping}
