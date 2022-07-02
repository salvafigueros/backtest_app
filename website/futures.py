import mysql.connector
from datetime import datetime, timedelta, date
import pandas as pd
from .asset import Asset

class Futures(Asset):

    def __init__(self, ticker, futures_name, currency, asset_id=None):
        self.ticker = ticker
        self.futures_name = futures_name
        self.currency = currency
        self.id = asset_id

    @staticmethod
    def save_futures(futures):
        if futures.id != None:
            return Futures.update(futures)
        return Futures.insert(futures)

    @staticmethod
    def create_futures(ticker, futures_name, currency):
        #Insert row in table asset_class before inserting in table future
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO asset_class(asset_class) VALUES(%s)", ("Futures",))
        asset_id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()
        
        futures = Futures(ticker, futures_name, currency, asset_id)

        return Futures.insert(futures)


    @staticmethod
    def get_futures_by_id(futures_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM futures F WHERE F.id = %s", (futures_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            futures = Futures(row[1], row[2], row[3])
            futures.id = row[0]

            conn_cursor.close()
            conn_bd.close()

            return futures
        else:
            print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod
    def get_futures_by_ticker(futures_ticker):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM futures F WHERE F.ticker = %s", (futures_ticker,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            futures = Futures(row[1], row[2], row[3])
            futures.id = row[0]

            conn_cursor.close()
            conn_bd.close()

            return futures
        else:
            print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False
    
    
    @staticmethod
    def insert(futures):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO futures(id, ticker, futures_name, currency) VALUES(%s, %s, %s, %s)", (futures.id, futures.ticker, futures.futures_name, futures.currency))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return futures
    
    @staticmethod
    def update(futures):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE futures F SET ticker = %s, futures_name=%s, currency=%s WHERE S.id=%s", (futures.ticker, futures.futures_name, futures.currency, futures.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return futures

    @staticmethod
    def delete(futures):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM futures WHERE id=%s", (futures.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    #Check if that price is already in bd 
    @staticmethod
    def price_already_in_bd(futures_id, date):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT date FROM futures_prices FP WHERE FP.futures_id = %s AND FP.date = %s", (futures_id, date))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            conn_cursor.close()
            conn_bd.close()
            return True
        
        conn_cursor.close()
        conn_bd.close()

        return False

    def upload_historic_data(self, first_date, last_date):
        #print(first_date)
        #print(last_date)
        period1 = int(datetime.strptime(first_date, '%Y-%m-%d').timestamp())
        period2 = int(datetime.strptime(last_date, '%Y-%m-%d').timestamp())
        
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{self.ticker}?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true'    
        
        try:
            df = pd.read_csv(query_string)
        except:
            return False

        df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adjusted_close', 'Volume': 'volume'}, inplace = True)
        df.insert(0, 'futures_id', self.id)
        df = df.dropna()
        

        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        for i, row in df.iterrows():
            if Futures.price_already_in_bd(self.id, df.loc[i, 'date']) == False:
                sql = "INSERT INTO futures_prices(futures_id, date, open, high, low, close, adjusted_close, volume) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                conn_cursor.execute(sql, tuple(row))
                conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True



    def delete_all_historic_data(self):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM futures_prices WHERE futures_id=%s", (self.id,))
        conn_bd.commit()
        
        conn_cursor.close()
        conn_bd.close()

        return True

    def delete_historic_data(self, first_date, last_date):
        first_date_time = datetime.strptime(first_date, '%Y-%m-%d').date()
        last_date_time = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(1)).date()
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        sql = "DELETE FROM futures_prices WHERE futures_id=%s AND date BETWEEN %s AND %s"
        conn_cursor.execute(sql, (self.id, first_date_time, last_date_time))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    def get_futures_prices_dates(self, first_date=None, last_date=None):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()

        if(first_date is None) or (last_date is None):
            sql = "SELECT date, open, high, low, close, adjusted_close, volume FROM futures_prices WHERE futures_id=%s ORDER BY date"
            sql_query = pd.read_sql_query(sql, conn_bd, params=[self.id]) 
        else:
            first_date_time = first_date
            if isinstance(first_date_time, str):
                first_date_time = datetime.strptime(first_date, '%Y-%m-%d').date()
            
            last_date_time = last_date
            if isinstance(last_date_time, str):
                last_date_time = datetime.strptime(last_date, '%Y-%m-%d').date()

            sql = "SELECT date, open, high, low, close, adjusted_close, volume FROM futures_prices WHERE futures_id=%s AND date BETWEEN %s AND %s ORDER BY date"
            sql_query = pd.read_sql_query(sql, conn_bd, params=[self.id, first_date_time, last_date_time]) 

        df = pd.DataFrame(sql_query, columns = ['date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume'])
        df.set_index('date', inplace=True)
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return df