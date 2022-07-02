from ...object_factory import ObjectFactory

class StrategyFactory(ObjectFactory):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(StrategyFactory, cls).__new__(cls)
        return cls._instance


    def get(self, strategy_id, **kwargs):
        return self.create(strategy_id, **kwargs)

