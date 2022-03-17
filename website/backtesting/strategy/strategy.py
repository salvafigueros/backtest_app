import datetime
import numpy as np
import pandas as pd
import queue
import mysql.connector

from abc import ABCMeta, abstractmethod

class Strategy(object):
    
    #__metaclass__ = ABCMeta

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
        conn_cursor.execute("INSERT INTO strategy(strategy, time_frame, exit_trade, exit_configuration) VALUES(%s, %s, %s, %s)", (strategy.strategy, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration))
        strategy.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy
    
    @staticmethod
    def update(strategy):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE strategy S SET strategy = %s, time_frame=%s, exit_trade=%s, exit_configuration=%s  WHERE S.id=%s", (strategy.strategy, strategy.time_frame, strategy.exit_trade, strategy.exit_configuration, strategy.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy

    @staticmethod
    def delete(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM strategy WHERE id=%s", (strategy_id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_strategy(strategy):
        if strategy.id is not None:
            return Strategy.update(strategy)
        return Strategy.insert(strategy)

    @staticmethod
    def create_strategy(strategy, time_frame, exit_trade, exit_configuration):
        strategy = Strategy(strategy=strategy, time_frame=time_frame, exit_trade=exit_trade, exit_configuration=exit_configuration)

        return Strategy.save_strategy(strategy)

    @staticmethod
    def get_strategy_by_id(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM strategy S WHERE S.id = %s", (strategy_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            strategy = Strategy(strategy=row[1], time_frame=row[2], exit_trade=row[3], exit_configuration=row[4])
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
    def get_strategy_name_by_id(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT strategy FROM strategy S WHERE S.id = %s", (strategy_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            strategy_name = row[0]
            
            conn_cursor.close()
            conn_bd.close()
            return strategy_name
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")