import mysql.connector
from .backtestingManualOperation import BacktestingManualOperation
import pandas as pd

class BacktestingManual():


    def __init__(self, backtesting_id=None, name=None, user_id=None, starting_cash=None, currency=None, saved=False, operations=None):
        self.id = backtesting_id
        self.name = name
        self.user_id = user_id 
        self.starting_cash = starting_cash
        self.currency = currency
        self.saved = saved
        self.operations = operations

        if (self.operations is None) and (self.id is not None):
            list_operation = BacktestingManualOperation.get_all_operations_by_backtesting_manual_id(self.id)
            list_operation.sort(key=lambda x:x.date)
            self.operations = list_operation

    @staticmethod
    def insert(backtesting_manual):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO backtesting_manual(name, user_id, starting_cash, currency, saved) VALUES(%s, %s, %s, %s, %s)", (backtesting_manual.name,
                                                                                                                                            backtesting_manual.user_id, 
                                                                                                                                            backtesting_manual.starting_cash, 
                                                                                                                                            backtesting_manual.currency,
                                                                                                                                            backtesting_manual.saved))
        backtesting_manual.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting_manual
    
    @staticmethod
    def update(backtesting_manual):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE backtesting_manual B SET name=%s, user_id = %s, starting_cash=%s, currency=%s, saved=%s WHERE B.id=%s", (backtesting_manual.name,
                                                                                                                                            backtesting_manual.user_id, 
                                                                                                                                            backtesting_manual.starting_cash, 
                                                                                                                                            backtesting_manual.currency,
                                                                                                                                            backtesting_manual.saved,
                                                                                                                                            backtesting_manual.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return backtesting_manual

    @staticmethod
    def delete(backtesting_manual):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM backtesting_manual WHERE id=%s", (backtesting_manual.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_backtesting_manual(backtesting_manual):
        if backtesting_manual.id is not None:
            return BacktestingManual.update(backtesting_manual)
        return BacktestingManual.insert(backtesting_manual)

    @staticmethod
    def create_backtesting_manual(user_id, starting_cash, currency):
        backtesting_manual = BacktestingManual(user_id=user_id, starting_cash=starting_cash, currency=currency)

        return BacktestingManual.save_backtesting_manual(backtesting_manual)

    @staticmethod
    def get_backtesting_manual_by_id(backtesting_manual_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_manual B WHERE B.id = %s", (backtesting_manual_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            backtesting_manual = BacktestingManual(backtesting_id=row[0], name=row[1], user_id=row[2], starting_cash=row[3], currency=row[4], saved=row[5])
            
            conn_cursor.close()
            conn_bd.close()
            return backtesting_manual
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod
    def get_list_backtesting_manual_by_user_id(user_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM backtesting_manual B WHERE B.user_id = %s", (user_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_backtesting_manual = []
            for row in records:
                backtesting_manual = BacktestingManual(backtesting_id=row[0], name=row[1], user_id=row[2], starting_cash=row[3], currency=row[4], saved=row[5])
                list_backtesting_manual.append(backtesting_manual)
            
            conn_cursor.close()
            conn_bd.close()
            return list_backtesting_manual
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []

    @property
    def operations_df(self):
        data = {'Date': [backtesting_manual_operation.date for backtesting_manual_operation in self.operations],
               'Quantity': [backtesting_manual_operation.quantity for backtesting_manual_operation in self.operations]
                }

        return pd.DataFrame(data).sort_values(by=['Date'])

    @property
    def equity_curve_df(self):
        equity_curve = []

        capital = self.starting_cash
        for backtesting_manual_operation in self.operations:
            capital = capital + backtesting_manual_operation.quantity
            equity_curve.append(capital)
        equity_curve.insert(0, self.starting_cash)



        data = {'Date': [backtesting_manual_operation.date for backtesting_manual_operation in self.operations],
               'Quantity': [backtesting_manual_operation.quantity for backtesting_manual_operation in self.operations],
               'Equity Curve': equity_curve
                }

        data['Date'].insert(0, None)
        data['Quantity'].insert(0, None)

        df = pd.DataFrame(data)
        df['Returns'] = df['Equity Curve'].pct_change()
        print(df)
        return pd.DataFrame(data)


    @property
    def capital_now(self):

        capital = self.starting_cash
        for backtesting_manual_operation in self.operations:
            capital = capital + backtesting_manual_operation.quantity

        return capital

    @property
    def total_trades(self):
        return len(self.operations)

    @property
    def total_wins(self):
        wins = 0

        for operation in self.operations:
            if operation.quantity > 0:
                wins = wins + 1
   
        return wins

    @property
    def total_losses(self):
        losses = 0

        for operation in self.operations:
            if operation.quantity < 0:
                losses = losses + 1
        
        return losses

    @property
    def pnl_return(self):
        return ("{:.2f}".format(float((self.equity_curve_df['Equity Curve'].iloc[-1] - self.starting_cash)/self.starting_cash)*100))
