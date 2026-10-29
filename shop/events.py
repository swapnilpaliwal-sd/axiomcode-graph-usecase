from collections import defaultdict


class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, topic: str, fn):
        self._subs[topic].append(fn)

    def emit(self, topic: str, payload):
        for fn in self._subs[topic]:
            fn(payload)


bus = EventBus()

from shop import receipts  # noqa: E402  (registers its subscribers)
