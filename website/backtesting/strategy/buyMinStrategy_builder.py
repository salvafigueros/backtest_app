from .buyMinStrategy import BuyMinStrategy


class BuyMinStrategyBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, time_frame, exit_trade, exit_configuration, **_ignored):
        self._instance = BuyMinStrategy(time_frame=time_frame, exit_trade=exit_trade, exit_configuration=exit_configuration)

        return self._instance
