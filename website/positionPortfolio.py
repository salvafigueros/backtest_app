import mysql.connector

class PositionPortfolio(object):
    
    def __init__(
        self,
        portfolio_id,
        position_id
    ):
        self.portfolio_id = portfolio_id
        self.position_id = position_id
        

    @staticmethod
    def insert(position_portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO position_portfolio(portfolio_id, position_id) VALUES(%s, %s)", (
            position_portfolio.portfolio_id,
            position_portfolio.position_id))
        position_portfolio.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return position_portfolio
    
    @staticmethod
    def update(position_portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        sql = "UPDATE position_portfolio P SET P.portfolio_id=%s P.position_id = %s WHERE P.id=%s"
        conn_cursor.execute(sql, (
            position_portfolio.portfolio_id,
            position_portfolio.position_id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return position_portfolio

    @staticmethod 
    def delete(position_portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM position_portfolio P WHERE P.id=%s", (position_portfolio.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True 
    
    @staticmethod
    def get_positions_portfolio_by_portfolio_id(portfolio_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM position_portfolio P WHERE P.portfolio_id = %s", (portfolio_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_positions_portfolio = []
            for row in records:
                position_portfolio = PositionPortfolio(row[1], row[2])
                position_portfolio.id = row[0]
                list_positions_portfolio.append(position_portfolio)
            
            conn_cursor.close()
            conn_bd.close()
            return list_positions_portfolio
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []
    
    @staticmethod
    def get_list_position_portfolio_by_position_id(position_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM position_portfolio P WHERE P.position_id = %s", (position_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_positions_portfolio = []
            for row in records:
                position_portfolio = PositionPortfolio(row[1], row[2])
                position_portfolio.id = row[0]
                list_positions_portfolio.append(position_portfolio)
            
            conn_cursor.close()
            conn_bd.close()
            return list_positions_portfolio
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []


