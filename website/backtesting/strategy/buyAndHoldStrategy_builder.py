from .buyAndHoldStrategy import BuyAndHoldStrategy


class BuyAndHoldStrategyBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        self._instance = BuyAndHoldStrategy()

        return self._instance