from shop.events import bus
from shop.notify import dispatch


def send_receipt(order):
    dispatch(order.channel, f"Order {order.id}: {order.total:.2f}")


bus.subscribe("order.placed", send_receipt)
