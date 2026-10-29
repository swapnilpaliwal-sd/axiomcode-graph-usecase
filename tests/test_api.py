from shop.api import place_order
from shop import notify


def test_place_order_sends_email_receipt():
    notify.SENT.clear()
    out = place_order({"sku": "book", "qty": 2, "channel": "email"})
    assert out["total"] == 21.6
    assert notify.SENT == [("email", "Order 1: 21.60")]
