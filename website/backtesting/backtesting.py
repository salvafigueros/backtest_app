import queue 
from .backtesting_assets import Backtesting_Assets
from .data.historicDBDataHandler import HistoricDBDataHandler
from .portfolioBacktesting import PortfolioBacktesting
from .simulatedExecutionHandler import SimulatedExecutionHandler
from .strategy.buyMaxStrategy import BuyMaxStrategy
from .strategy.buyMinStrategy import BuyMinStrategy
from .strategy.shortMaxStrategy import ShortMaxStrategy
from .strategy.shortMinStrategy import ShortMinStrategy
from .strategy.buyAndHoldStrategy import BuyAndHoldStrategy
from .strategy.strategy import Strategy
from .strategy.strategy_factory import StrategyFactory
from .strategy.buyMaxStrategy_builder import BuyMaxStrategyBuilder
from .strategy.strategyType import StrategyType
from ..utils import get_strategy_conf_by_strategy_type_id

import mysql.connector
import pandas as pd

class Backtesting():


    def __init__(self, backtesting_id=None, user_id=None, name=None, strategy_id=None, starting_cash=None, currency=None, start_dt=None, end_dt=None, shared=False, saved=False, date=None):
        self.id = backtesting_id
        self.user_id = user_id 
        self.name = name
        self.strategy_id = strategy_id
        self.starting_cash = starting_cash
        self.currency = currency
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.saved = saved
        self.shared = shared
        self.date = date

    @staticmethod
    def insert(backtesting):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO backtesting(user_id, name, strategy_id, starting_cash, currency, start_dt, end_dt, shared, saved) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (backtesting.user_id, backtesting.name, backtesting.strategy_id, backtesting.starting_cash, backtesting.currency, backtesting.start_dt, backtesting.end_dt, backtesting.shared, backtesting.saved))
        backtesting.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting
    
    @staticmethod
    def update(backtesting):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE backtesting B SET user_id = %s, name=%s, strategy_id=%s, starting_cash=%s, currency=%s, start_dt=%s, end_dt=%s, shared=%s, saved=%s WHERE B.id=%s", (backtesting.user_id, backtesting.name, backtesting.strategy_id, backtesting.starting_cash, backtesting.currency, backtesting.start_dt, backtesting.end_dt, backtesting.shared, backtesting.saved, backtesting.id))
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
    def create_backtesting(user_id, name, strategy_id, starting_cash, currency, start_dt, end_dt, shared=False, saved=False):
        backtesting = Backtesting(user_id=user_id, name=name, strategy_id=strategy_id, starting_cash=starting_cash, currency=currency, start_dt=start_dt, end_dt=end_dt, shared=shared, saved=saved)

        return Backtesting.save_backtesting(backtesting)

    def set_strategy(self, strategy_factory):
        strategy_conf = get_strategy_conf_by_strategy_type_id(self.strategy_id)

        if hasattr(self, "strategy_type"):
            self.strategy = strategy_factory.get(self.strategy_type.strategy_type, **strategy_conf)
        elif hasattr(self, "strategy_id"):
            self.strategy_type = StrategyType.get_strategy_type_by_id(self.strategy_id)
            self.strategy = strategy_factory.get(self.strategy_type.strategy_type, **strategy_conf)

        return



    @staticmethod
    def create_backtesting_from_user(user_id, name, starting_cash, currency, start_dt, end_dt, ticker_list, strategy_type):
        backtesting = Backtesting.create_backtesting(user_id, name, strategy_type.id, starting_cash, currency, start_dt, end_dt)
        backtesting.saved = True
        backtesting.backtesting_assets = Backtesting_Assets.create_backtesting_assets(backtesting.id, ticker_list)

        return backtesting
     

    @staticmethod
    def get_backtesting_by_id(backtesting_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting B WHERE B.id = %s", (backtesting_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            backtesting = Backtesting(user_id=row[1], 
                                      name=row[2], 
                                      strategy_id=row[3], 
                                      starting_cash=row[4], 
                                      currency=row[5], 
                                      start_dt=row[6], 
                                      end_dt=row[7], 
                                      shared=row[8], 
                                      saved=row[9])
            backtesting.id = row[0]
            
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
    def create_backtesting_from_db(backtesting_id):
        #Create Backtesting
        backtesting = Backtesting.get_backtesting_by_id(backtesting_id)

        #Set BacktestingAssets
        backtesting.backtesting_assets = Backtesting_Assets.get_backtesting_assets_by_backtesting_id(backtesting.id)

        #Set StrategyType
        backtesting.strategy_type = StrategyType.get_strategy_type_by_id(backtesting.strategy_id)

        return backtesting
    
    def execute_backtesting(self):
        #Prepare Backtesting
        self.events = queue.Queue()
        self.bars = HistoricDBDataHandler(self.events, self.backtesting_assets.ticker_list, self.start_dt, self.end_dt)
        self.port = PortfolioBacktesting(self.bars, self.events, self.bars.get_start_date(), self.starting_cash, self.currency)
        self.simulator = SimulatedExecutionHandler(self.events)
        self.strategy.events=self.events
        self.strategy.set_bars(self.bars, self.backtesting_assets.ticker_list)

        #Run Backtesting
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

    @property
    def equity_curve(self):
        equity_curve = self.port.equity_curve
        equity_curve = equity_curve["equity_curve"]
        
        equity_curve.drop(index=equity_curve.index[0], 
                axis=0, 
                inplace=True)

        equity_curve.drop(equity_curve.tail(1).index,inplace=True) # drop last row


        return pd.DataFrame(equity_curve)



    
    def benchmark_backtesting(self):
        #Prepare Backtesting
        events = queue.Queue()
        bars = HistoricDBDataHandler(events, self.backtesting_assets.ticker_list, self.start_dt, self.end_dt)
        port = PortfolioBacktesting(bars, events, bars.get_start_date(), self.starting_cash, self.currency)
        simulator = SimulatedExecutionHandler(events)
        strategy = BuyAndHoldStrategy(bars, events)

        #Run Backtesting
        while True:
            if bars.continue_backtest == True:
                bars.update_bars()
            else: 
                break

            while True:
                try:
                    event = events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            strategy.calculate_signals(event)
                            port.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            port.update_signal(event)

                        elif event.type == 'ORDER':
                            simulator.execute_order(event)

                        elif event.type == 'FILL':
                            port.update_fill(event)
        

        port.create_equity_curve_dataframe()
        return port.output_summary_stats()