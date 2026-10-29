from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> str: ...


class CardGateway(PaymentGateway):
    def charge(self, amount: float) -> str:
        return f"card:{amount:.2f}"
