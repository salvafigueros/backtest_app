from ..stock import Stock
from ..futures import Futures
import mysql.connector

class Backtesting_Assets():


    def __init__(self, backtesting_id=None, ticker_list=[]):
        self.backtesting_id = backtesting_id
        self.ticker_list = ticker_list



    @staticmethod
    def insert(backtesting_assets):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        for ticker in backtesting_assets.ticker_list:
            conn_cursor = conn_bd.cursor()
            stock = Stock.get_stock_by_ticker(ticker)
            if stock:
                conn_cursor.execute("INSERT INTO backtesting_assets(backtesting_id, asset_id, asset_class) VALUES(%s, %s, %s)", (backtesting_assets.backtesting_id, stock.id, "Stock"))
            else:
                future = Futures.get_futures_by_ticker(ticker)
                conn_cursor.execute("INSERT INTO backtesting_assets(backtesting_id, asset_id, asset_class) VALUES(%s, %s, %s)", (backtesting_assets.backtesting_id, future.id, "Future"))

            conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting_assets
    

    @staticmethod
    def save_backtesting_assets(backtesting_assets):
        return Backtesting_Assets.insert(backtesting_assets)

    @staticmethod
    def create_backtesting_assets(backtesting_id, ticker_list):
        backtesting_assets = Backtesting_Assets(backtesting_id=backtesting_id, ticker_list=ticker_list)

        return Backtesting_Assets.save_backtesting_assets(backtesting_assets)

    @staticmethod
    def get_backtesting_assets_by_backtesting_id(backtesting_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_assets B WHERE B.backtesting_id = %s", (backtesting_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:

            records = conn_cursor.fetchall()
            ticker_list = []
            for row in records:
                asset_class = row[3]
                asset = None
                if asset_class == "Stock":
                    asset = Stock.get_stock_by_id(row[2])
                elif asset_class == "Future":
                    asset = Futures.get_futures_by_id(row[2])

                if asset is not None:
                    ticker_list.append(asset.ticker)
                
            backtesting_assets = Backtesting_Assets(backtesting_id=backtesting_id, ticker_list=ticker_list)
            
            conn_cursor.close()
            conn_bd.close()
            return backtesting_assets
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False
