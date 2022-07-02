import mysql.connector

class StrategyType:

    def __init__(self, strategy_id=None, strategy_type=None):
        self.id = strategy_id
        self.strategy_type = strategy_type


    @staticmethod
    def insert(strategy_type):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO strategy_type(strategy_type) VALUES(%s)", (strategy_type.strategy_type,))
        strategy_type.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy_type
    
    @staticmethod
    def update(strategy_type):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("UPDATE strategy_type S SET strategy_type=%s WHERE S.id=%s", (strategy_type.strategy_type, strategy_type.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return strategy_type

    @staticmethod
    def delete(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM strategy_type WHERE id=%s", (strategy_id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True

    @staticmethod
    def save_strategy_type(strategy_type):
        if (hasattr(strategy_type, 'id') == True) and (strategy_type.id is not None):
            return StrategyType.update(strategy_type)
        return StrategyType.insert(strategy_type)

    @staticmethod
    def create_strategy_type(s_type):
        """
        Instances object of class StrategyType for the first time and
        saves it in db. The first time an object of this class is created 
        is when a user creates a backtesting for the first time. 
        """
        strategy_type = StrategyType(strategy_type=s_type)

        return StrategyType.save_strategy_type(strategy_type)


    @staticmethod
    def get_strategy_type_by_id(strategy_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM strategy_type S WHERE S.id = %s", (strategy_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            strategy_type = StrategyType(strategy_id=row[0], 
                                         strategy_type=row[1])
            
            conn_cursor.close()
            conn_bd.close()
            return strategy_type
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False
