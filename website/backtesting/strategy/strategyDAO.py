from abc import ABCMeta, abstractmethod

class StrategyDAO(object):
    
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def insert(strategy):
        raise NotImplementedError("Should implement insert()")

    
    @staticmethod
    @abstractmethod
    def update(strategy):
        raise NotImplementedError("Should implement update()")


    @staticmethod
    @abstractmethod
    def delete(strategy_id):
        raise NotImplementedError("Should implement delete()")


    @staticmethod
    @abstractmethod
    def save_strategy(strategy):
        raise NotImplementedError("Should implement save_strategy()")


    @staticmethod
    @abstractmethod
    def create_strategy():
        raise NotImplementedError("Should implement create_strategy()")



    @staticmethod
    @abstractmethod
    def get_strategy_by_id(strategy_id):
        raise NotImplementedError("Should implement get_strategy_by_id()")



    @staticmethod
    @abstractmethod
    def get_strategy_conf_by_id(strategy_id):
        raise NotImplementedError("Should implement get_strategy_conf_by_id()")
