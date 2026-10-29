from dataclasses import dataclass

from shop.payments import PaymentGateway
from shop.events import EventBus
from shop.pricing import price_for


@dataclass
class Order:
    id: int
    sku: str
    qty: int
    total: float
    channel: str


class OrderService:
    def __init__(self, payment: PaymentGateway, events: EventBus):
        self.payment = payment
        self.events = events
        self._next = 1

    def place(self, sku: str, qty: int, channel: str) -> Order:
        total = price_for(sku) * qty
        self.payment.charge(total)
        order = Order(self._next, sku, qty, total, channel)
        self._next += 1
        self.events.emit("order.placed", order)
        return order
