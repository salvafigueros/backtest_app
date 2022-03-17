import mysql.connector
from datetime import datetime, timedelta, date
import pandas as pd
from .asset import Asset
import yfinance as yf
import numpy as np
from decimal import *
from pandas_datareader import data


class Stock(Asset):

    def __init__(self, ticker, company_name, market, currency, metric=0):
        self.ticker = ticker
        self.company_name = company_name
        self.market = market
        self.currency = currency
        self.metric = metric

    def __str__(self):
        """
        String representation of the Stock Object.
        """
        return ("'%s' ('%s')" % (
                self.company_name, self.ticker
            )
        )

    def __repr__(self):
        """
        Stock Object Representation in string format.
        """
        return ("Stock(ticker='%s', copmany_name='%s', market=%s)" % (
                self.ticker, self.company_name, self.market
            )
        )


    @staticmethod
    def insert(stock):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO stocks(ticker, company_name, market, currency) VALUES(%s, %s, %s, %s)", (stock.ticker, stock.company_name, stock.market, stock.currency))
        stock.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return stock
    
    @staticmethod
    def update(stock):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE stocks S SET ticker = %s, company_name=%s, market=%s, currency=%s WHERE S.id=%s", (stock.ticker, stock.company_name, stock.market, stock.currency, stock.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return stock

    @staticmethod
    def delete(stock):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM stocks WHERE id=%s", (stock.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True


    @staticmethod
    def save_stock(stock):
        if hasattr(stock, 'id') == True:
            return Stock.update(stock)
        return Stock.insert(stock)

    @staticmethod
    def create_stock(ticker, company_name, market, currency):
        stock = Stock(ticker, company_name, market, currency)

        return Stock.save_stock(stock)


    @staticmethod
    def get_stock_by_id(stock_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM stocks S WHERE S.id = %s", (stock_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            stock = Stock(row[1], row[2], row[3], row[4])
            stock.id = row[0]

            conn_cursor.close()
            conn_bd.close()

            return stock
        else:
            print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod
    def get_stock_by_ticker(stock_ticker):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM stocks S WHERE S.ticker = %s", (stock_ticker,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            stock = Stock(row[1], row[2], row[3], row[4])
            stock.id = row[0]

            conn_cursor.close()
            conn_bd.close()

            return stock
        else:
            print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False
    

    #Check if that price is already in bd 
    @staticmethod
    def price_already_in_bd(stock_id, date):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT date FROM stock_prices SP WHERE SP.stock_id = %s AND SP.date = %s", (stock_id, date))
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
        df = pd.read_csv(query_string)

        df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adjusted_close', 'Volume': 'volume'}, inplace = True)
        df.insert(0, 'stock_id', self.id)
        df = df.dropna()
        

        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        for i, row in df.iterrows():
            if Stock.price_already_in_bd(self.id, df.loc[i, 'date']) == False:
                sql = "INSERT INTO stock_prices(stock_id, date, open, high, low, close, adjusted_close, volume) VALUES (" + "%s,"*(len(row)-1) + "%s)"
                conn_cursor.execute(sql, tuple(row))
                conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True



    def delete_all_historic_data(self):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM stock_prices WHERE stock_id=%s", (self.id,))
        conn_bd.commit()
        
        conn_cursor.close()
        conn_bd.close()

        return True

    def delete_historic_data(self, first_date, last_date):
        first_date_time = datetime.strptime(first_date, '%Y-%m-%d').date()
        last_date_time = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(1)).date()
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        sql = "DELETE FROM stock_prices WHERE stock_id=%s AND date BETWEEN %s AND %s"
        conn_cursor.execute(sql, (self.id, first_date_time, last_date_time))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True


    def get_stock_prices_dates(self, first_date=None, last_date=None):

        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()

        if(first_date is None) or (last_date is None):
            sql = "SELECT date, open, high, low, close, adjusted_close, volume FROM stock_prices WHERE stock_id=%s ORDER BY date"
            sql_query = pd.read_sql_query(sql, conn_bd, params=[self.id]) 
        else:
            first_date_time = datetime.strptime(first_date, '%Y-%m-%d').date()
            last_date_time = datetime.strptime(last_date, '%Y-%m-%d').date()
            sql = "SELECT date, open, high, low, close, adjusted_close, volume FROM stock_prices WHERE stock_id=%s AND date BETWEEN %s AND %s ORDER BY date"
            sql_query = pd.read_sql_query(sql, conn_bd, params=[self.id, first_date_time, last_date_time]) 

        df = pd.DataFrame(sql_query, columns = ['date', 'open', 'high', 'low', 'close', 'adjusted_close', 'volume'])
        df.set_index('date', inplace=True)
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return df

    @staticmethod
    def get_last_quote(ticker):
        ticker_yahoo = yf.Ticker(ticker)
        data = ticker_yahoo.history()
        last_quote = (data.tail(1)['Close'].iloc[0])

        return Decimal(last_quote.item())


    @staticmethod
    def get_all_stocks():
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM stocks S")
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_stocks = []
            for row in records:
                stock = Stock(row[1], row[2], row[3], row[4], row[5])
                stock.id = row[0]
                list_stocks.append(stock)
            
            conn_cursor.close()
            conn_bd.close()
            return list_stocks
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []


    @staticmethod
    def update_metric(stock):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE stocks S SET metric=%s WHERE S.id=%s", (stock.metric, stock.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return stock

    @staticmethod
    def get_list_stocks_by_metric(metric):
        list_stocks = Stock.get_all_stocks()
        list_stocks_with_metric = []

        list_tickers = []
        for stock in list_stocks:
            list_tickers.append(stock.ticker)

        """
        df = data.get_quote_yahoo(list_tickers)
        pd.set_option =("display.max_columns", None)
        print(df.head())
        """

        market_caps = data.get_quote_yahoo(list_tickers)[metric]
        list_market_caps = market_caps.values.tolist()

        for stock, market_cap in zip(list_stocks, list_market_caps):
            stock.metric = market_cap
            stock = Stock.update_metric(stock)
            stock.metric = "{:,}".format(stock.metric).replace(',', '.')
            list_stocks_with_metric.append(stock)
            
        
        return list_stocks_with_metric

    @staticmethod
    def get_df_prices(ticker_list):
        df = pd.DataFrame()
        
        for ticker in ticker_list:
            stock = Stock.get_stock_by_ticker(ticker)

            if stock:
                df[ticker] = stock.get_stock_prices_dates()['adjusted_close']

        return df

        
