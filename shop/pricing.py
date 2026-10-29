PRICES = {"book": 12.0, "pen": 1.5}


def price_for(sku: str) -> float:
    return apply_discount(PRICES[sku])


def apply_discount(amount: float) -> float:
    return round(amount * 0.9, 2) if amount > 10 else amount
