from shop.service import OrderService
from shop.payments import CardGateway
from shop.events import bus


def make_service() -> OrderService:
    return OrderService(CardGateway(), bus)


def place_order(request: dict) -> dict:
    service = make_service()
    order = service.place(request["sku"], request["qty"], request["channel"])
    return {"id": order.id, "total": order.total}
