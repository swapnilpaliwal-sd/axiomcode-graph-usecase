import sys

SENT = []


def notify_email(message: str) -> None:
    SENT.append(("email", message))


def notify_sms(message: str) -> None:
    SENT.append(("sms", message[:160]))


def dispatch(channel: str, message: str) -> None:
    handler = getattr(sys.modules[__name__], f"notify_{channel}")
    handler(message)
