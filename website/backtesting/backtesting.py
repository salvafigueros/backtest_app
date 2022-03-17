import queue 
from .backtesting_assets import Backtesting_Assets
from .data.historicDBDataHandler import HistoricDBDataHandler
from .conservativePortfolio import ConservativePortfolio
from .simulatedExecutionHandler import SimulatedExecutionHandler
from .strategy.buyMaxStrategy import BuyMaxStrategy
from .strategy.buyMinStrategy import BuyMinStrategy
from .strategy.shortMaxStrategy import ShortMaxStrategy
from .strategy.shortMinStrategy import ShortMinStrategy
from .strategy.strategy import Strategy

import mysql.connector

class Backtesting():


    def __init__(self, backtesting_id=None, user_id=None, strategy_id=None, starting_cash=None, currency=None, shared=False):
        self.id = backtesting_id
        self.user_id = user_id 
        self.strategy_id = strategy_id
        self.starting_cash = starting_cash
        self.currency = currency
        self.saved = False
        self.shared = shared

    @staticmethod
    def insert(backtesting):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO backtesting(user_id, strategy_id, starting_cash, currency, shared) VALUES(%s, %s, %s, %s, %s)", (backtesting.user_id, backtesting.strategy_id, backtesting.starting_cash, backtesting.currency, backtesting.shared))
        backtesting.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting
    
    @staticmethod
    def update(backtesting):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE backtesting B SET user_id = %s, strategy_id=%s, starting_cash=%s, currency=%s, shared=%s WHERE B.id=%s", (backtesting.user_id, backtesting.strategy_id, backtesting.starting_cash, backtesting.currency, backtesting.shared, backtesting.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting

    @staticmethod
    def delete(backtesting):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM backtesting WHERE id=%s", (backtesting.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_backtesting(backtesting):
        if backtesting.id is not None:
            return Backtesting.update(backtesting)
        return Backtesting.insert(backtesting)

    @staticmethod
    def save_backtesting_in_bd(user_id, starting_cash, currency, ticker_list, strategy_name, time_frame, exit_trade, exit_configuration):
        strategy = Strategy.create_strategy(strategy_name, time_frame, exit_trade, exit_configuration)
        backtesting = Backtesting.create_backtesting_from_user(user_id, strategy.id, starting_cash, currency, ticker_list, strategy.strategy, time_frame, exit_trade, exit_configuration)
        backtesting = Backtesting.save_backtesting(backtesting)
        backtesting.saved = True
        backtesting.backtesting_assets = Backtesting_Assets.create_backtesting_assets(backtesting.id, ticker_list)

        return backtesting
        

    @staticmethod
    def create_backtesting(user_id, strategy_id, starting_cash, currency, shared):
        backtesting = Backtesting(user_id=user_id, strategy_id=strategy_id, starting_cash=starting_cash, currency=currency, shared=shared)

        return Backtesting.save_backtesting(backtesting)

    @staticmethod
    def get_backtesting_by_id(backtesting_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting B WHERE B.id = %s", (backtesting_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            backtesting = Backtesting(user_id=row[1], strategy_id=row[2], starting_cash=row[3], currency=row[4], shared=row[5])
            backtesting.id = row[0]
            backtesting.saved = True

            conn_cursor.close()
            conn_bd.close()
            return backtesting
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod
    def get_list_backtesting_by_user_id(user_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting B WHERE B.user_id = %s", (user_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_backtesting = []
            for row in records:
                backtesting = Backtesting.create_backtesting_from_db(row[0])
                list_backtesting.append(backtesting)
            
            conn_cursor.close()
            conn_bd.close()
            return list_backtesting
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []

    @staticmethod
    def get_list_backtesting_by_asset(asset):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_assets B WHERE B.asset_id = %s", (asset.id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:

            records = conn_cursor.fetchall()
            list_backtesting = []
            for row in records:
                backtesting = Backtesting.create_backtesting_from_db(row[1])
                list_backtesting.append(backtesting)
            
            conn_cursor.close()
            conn_bd.close()
            return list_backtesting
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod 
    def create_backtesting_from_user(user_id, strategy_id, starting_cash, currency, ticker_list, strategy, time_frame, exit_trade, exit_configuration):
        backtesting = Backtesting(user_id=user_id, strategy_id=strategy_id, starting_cash=starting_cash, currency=currency)
        backtesting.backtesting_assets = Backtesting_Assets(ticker_list=ticker_list)
        backtesting.events = queue.Queue()
        backtesting.bars = HistoricDBDataHandler(backtesting.events, backtesting.backtesting_assets.ticker_list)
        backtesting.port = ConservativePortfolio(backtesting.bars, backtesting.events, backtesting.bars.get_start_date(), backtesting.starting_cash)
        backtesting.simulator = SimulatedExecutionHandler(backtesting.events)

        if strategy == "buymax":
            backtesting.strategy = BuyMaxStrategy(backtesting.bars, backtesting.events, time_frame, exit_trade, exit_configuration)
        elif strategy == "shortmax":
            backtesting.strategy = ShortMaxStrategy(backtesting.bars, backtesting.events, time_frame, exit_trade, exit_configuration)
        elif strategy == "buymin":
            backtesting.strategy = BuyMinStrategy(backtesting.bars, backtesting.events, time_frame, exit_trade, exit_configuration)
        elif strategy == "shortmin":
            backtesting.strategy = ShortMinStrategy(backtesting.bars, backtesting.events, time_frame, exit_trade, exit_configuration)

        return backtesting

    @staticmethod
    def create_backtesting_from_db(backtesting_id):
        backtesting = Backtesting.get_backtesting_by_id(backtesting_id)
        backtesting.backtesting_assets = Backtesting_Assets.get_backtesting_assets_by_backtesting_id(backtesting.id)
        backtesting.events = queue.Queue()
        backtesting.bars = HistoricDBDataHandler(backtesting.events, backtesting.backtesting_assets.ticker_list)
        backtesting.port = ConservativePortfolio(backtesting.bars, backtesting.events, backtesting.bars.get_start_date(), backtesting.starting_cash)
        backtesting.simulator = SimulatedExecutionHandler(backtesting.events)

        strategy = Strategy.get_strategy_by_id(backtesting.strategy_id)
        if strategy.strategy == "buymax":
            backtesting.strategy = BuyMaxStrategy(backtesting.bars, backtesting.events, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration)
        elif strategy.strategy == "shortmax":
            backtesting.strategy = ShortMaxStrategy(backtesting.bars, backtesting.events, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration)
        elif strategy.strategy == "buymin":
            backtesting.strategy = BuyMinStrategy(backtesting.bars, backtesting.events, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration)
        elif strategy.strategy == "shortmin":
            backtesting.strategy = ShortMinStrategy(backtesting.bars, backtesting.events, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration)

        return backtesting
    
    def execute_backtesting(self):

        while True:
                if self.bars.continue_backtest == True:
                    self.bars.update_bars()
                else: 
                    break

                while True:
                    try:
                        event = self.events.get(False)
                    except queue.Empty:
                        break
                    else:
                        if event is not None:
                            if event.type == 'MARKET':
                                self.strategy.calculate_signals(event)
                                self.port.update_timeindex(event)

                            elif event.type == 'SIGNAL':
                                self.port.update_signal(event)

                            elif event.type == 'ORDER':
                                self.simulator.execute_order(event)

                            elif event.type == 'FILL':
                                self.port.update_fill(event)

                            
    def output_results_backtesting(self):
        self.port.create_equity_curve_dataframe()
        return self.port.output_summary_stats()

    def plot_equity_curve(self):
        return self.port.plot_equity_curve()



    def info_backtesting(self):
        info_backtesting = {
            "user_name": User.get_user_by_id(self.user_id).user_name,
            "ticker_list": self.backtesting_assets.ticker_list,
            "strategy": "hola",
            "exit_trade": "hola",
            "exit_configuration": "hola"
        }

        return info_backtesting