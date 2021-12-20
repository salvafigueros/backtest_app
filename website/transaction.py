import mysql.connector
import numpy as np
import datetime
from .stock import Stock
from decimal import *

class Transaction(object):
    
    def __init__(self, user_id, asset, quantity, price, dt, commmission=0.0, position_id = None):
        self.user_id = user_id
        self.asset = asset
        self.quantity = quantity
        self.price = price
        self.dt = dt
        #self.order_id = order_id
        self.commission = Decimal(commmission)
        self.position_id =  position_id


    @staticmethod
    def insert(transaction):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO transactions(user_id, asset, quantity, price, dt, commission, position_id) VALUES(%s, %s, %s, %s, %s, %s, %s)", (
            transaction.user_id,
            transaction.asset,
            transaction.quantity, 
            transaction.price,
            transaction.dt,
            transaction.commission,
            transaction.position_id))
        transaction.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return transaction
    
    @staticmethod
    def update(transaction):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        sql = "UPDATE transactions T SET T.user_id=%s, T.asset = %s, T.quantity=%s, T.price=%s, T.dt=%s, T.commission=%s, T.position_id=%s  WHERE T.id=%s"
        conn_cursor.execute(sql, (
            transaction.user_id, 
            transaction.asset,
            transaction.quantity,
            transaction.price,
            transaction.dt,
            transaction.commission,
            transaction.position_id,
            transaction.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return transaction

    @staticmethod
    def delete(transaction):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM transactions T WHERE T.id=%s", (transaction.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True 

    @staticmethod
    def get_list_transactions_by_position_id(position_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM transactions T WHERE T.position_id = %s", (position_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_transactions = []
            for row in records:
                transaction = Transaction(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                transaction.id = row[0]
                list_transactions.append(transaction)
            
            conn_cursor.close()
            conn_bd.close()
            return list_transactions
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []

    @staticmethod
    def create_transaction(user_id, asset, quantity):
        # 1. Get Asset's Actual Price
        price = Stock.get_last_quote(asset)
        print(type(price))
        # 2. Get dt of Asset's Actual Price
        dt = datetime.datetime.now()
        # 3. Get commission
        # 4. Create Transaction Object
        transaction = Transaction(user_id, asset, quantity, price, dt)
        # 5. Insert Transaction Object into db
        transaction = Transaction.insert(transaction)
        # 6. Returns Transaction Object
        return transaction


    @property
    def direction(self):
        """
        Returns an integer value representing the direction.
        Returns
        -------
        `int`
            1 - Long, 0 - No direction, -1 - Short.
        """
        if self.quantity == 0:
            return 0
        else:
            return np.copysign(1, self.quantity)

    @property
    def cost_without_commission(self):
        return self.quantity*self.price 

    @property 
    def cost_with_commission(self):
        return self.quantity*self.price - self.commission