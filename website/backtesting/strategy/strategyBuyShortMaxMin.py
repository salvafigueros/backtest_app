import mysql.connector
from .strategyDAO import StrategyDAO

class StrategyBuyShortMaxMin(StrategyDAO):

    def __init__(self, strategy_id=None, strategy=None, time_frame = None, exit_trade = None, exit_configuration = None):
        self.id = strategy_id
        self.strategy = strategy
        self.time_frame = time_frame
        self.exit_trade = exit_trade
        self.exit_configuration = exit_configuration


    @staticmethod
    def insert(strategy):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO strategy_buy_short_max_min(id, strategy, time_frame, exit_trade, exit_configuration) VALUES(%s, %s, %s, %s, %s)", (strategy.id, strategy.strategy, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy
    
    @staticmethod
    def update(strategy):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE strategy_buy_short_max_min S SET strategy = %s, time_frame=%s, exit_trade=%s, exit_configuration=%s  WHERE S.id=%s", (strategy.strategy, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration, strategy.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy

    @staticmethod
    def delete(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM strategy_buy_short_max_min WHERE id=%s", (strategy_id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_strategy(strategy):
        if strategy.id is not None:
            return strategy.update(strategy)
        return strategy.insert(strategy)

    @staticmethod
    def create_strategy(strategy_id, strategy, time_frame, exit_trade, exit_configuration):
        strategy = StrategyBuyShortMaxMin(strategy_id=strategy_id,
                                          strategy=strategy, 
                                          time_frame=time_frame,
                                          exit_trade=exit_trade, 
                                          exit_configuration=exit_configuration)

        return StrategyBuyShortMaxMin.insert(strategy)


    @staticmethod
    def get_strategy_by_id(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM strategy_buy_short_max_min S WHERE S.id = %s", (strategy_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            strategy = StrategyBuyShortMaxMin(strategy=row[1], time_frame=row[2], exit_trade=row[3], exit_configuration=row[4])
            strategy.id = row[0]
            
            conn_cursor.close()
            conn_bd.close()
            return strategy
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False


    @staticmethod
    def get_strategy_conf_by_id(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM strategy_buy_short_max_min S WHERE S.id = %s", (strategy_id,))
        conn_bd.commit()

        strategy_conf = {}

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()

            strategy_conf["time_frame"] = int(row[2])
            strategy_conf["exit_trade"] = row[3]
            strategy_conf["exit_configuration"] = int(row[4])
            
            conn_cursor.close()
            conn_bd.close()
            return strategy_conf
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return strategy_conf
