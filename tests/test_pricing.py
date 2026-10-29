from shop.pricing import price_for, apply_discount


def test_discount_over_ten():
    assert apply_discount(20.0) == 18.0


def test_pen_has_no_discount():
    assert price_for("pen") == 1.5
