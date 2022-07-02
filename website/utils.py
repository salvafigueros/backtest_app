from .backtesting.strategy.strategyType import StrategyType
from .backtesting.strategy.strategyBuyShortMaxMin import StrategyBuyShortMaxMin


def get_strategy_conf_by_strategy_type_id(strategy_id):
    #Query the table called "Strategy"
    strategy_type = StrategyType.get_strategy_type_by_id(strategy_id)

    #Query the table of the strategy type found in the previous query
    strategy_conf = {}

    if strategy_type:
        if strategy_type.strategy_type == "buymax":
            strategy_conf = StrategyBuyShortMaxMin.get_strategy_conf_by_id(strategy_type.id)
        elif strategy_type.strategy_type == "shortmax":
            strategy_conf = StrategyBuyShortMaxMin.get_strategy_conf_by_id(strategy_type.id)
        elif strategy_type.strategy_type == "buymin":
            strategy_conf = StrategyBuyShortMaxMin.get_strategy_conf_by_id(strategy_type.id)
        elif strategy_type.strategy_type == "shortmin":
            strategy_conf = StrategyBuyShortMaxMin.get_strategy_conf_by_id(strategy_type.id)
        elif strategy_type.strategy_type == "buyandhold":
            pass 


    

    return strategy_conf