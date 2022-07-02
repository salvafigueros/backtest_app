import mysql.connector
from .position import Position
from .positionHandler import PositionHandler
from datetime import datetime
from decimal import *

class Portfolio(object):
    
    
    def __init__(
        self,
        name,
        user_id,
        start_dt,
        end_dt=None,
        starting_cash=0.0,
        current_cash=0.0,
        currency="USD",
        shared=False
    ):
        self.user_id = user_id
        self.name = name
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.current_dt = start_dt
        self.starting_cash = starting_cash
        self.current_cash = current_cash
        self.currency = currency
        self.shared = shared
        self.pos_handler = PositionHandler(self.currency)
        

    @staticmethod
    def insert(portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("INSERT INTO portfolios(name, user_id, start_dt, end_dt, starting_cash, current_cash, currency, shared) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (
            portfolio.name,
            portfolio.user_id,
            portfolio.start_dt,
            portfolio.end_dt, 
            portfolio.starting_cash,
            portfolio.current_cash,
            portfolio.currency,
            portfolio.shared))
        portfolio.id = conn_cursor.lastrowid
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return portfolio
    
    @staticmethod
    def update(portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        sql = "UPDATE portfolios P SET P.name=%s, P.user_id=%s, P.start_dt = %s, P.end_dt=%s, P.starting_cash=%s, P.current_cash=%s, P.currency=%s, P.shared=%s WHERE P.id=%s"
        conn_cursor.execute(sql, (
            portfolio.name,
            portfolio.user_id,
            portfolio.start_dt, 
            portfolio.end_dt, 
            portfolio.starting_cash, 
            portfolio.current_cash, 
            portfolio.currency,
            portfolio.shared,
            portfolio.id))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return portfolio

    @staticmethod
    def delete(portfolio):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor()
        conn_cursor.execute("DELETE FROM portfolios P WHERE P.id=%s", (portfolio.id,))
        conn_bd.commit()

        conn_cursor.close()
        conn_bd.close()

        return True 
    
    @staticmethod
    def get_portfolio_by_id(portfolio_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM portfolios P WHERE P.id = %s", (portfolio_id,))
        conn_bd.commit()

        if conn_cursor.rowcount == 1:
            row = conn_cursor.fetchone()
            portfolio = Portfolio(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            portfolio.id = row[0]
            portfolio.pos_handler = PositionHandler.get_positions_by_portfolio_id(portfolio.id, portfolio.currency)
            
            conn_cursor.close()
            conn_bd.close()
            return portfolio
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return False

    @staticmethod
    def get_list_portfolio_by_user_id(user_id):
        conn_bd = mysql.connector.connect(host="localhost", user="backtesting", passwd="backtesting", database="backtesting")
        conn_cursor = conn_bd.cursor(buffered=True)
        conn_cursor.execute("SELECT * FROM portfolios P WHERE P.user_id = %s", (user_id,))
        conn_bd.commit()

        if conn_cursor.rowcount > 0:
            records = conn_cursor.fetchall()
            list_portfolio = []
            for row in records:
                portfolio = Portfolio(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
                portfolio.id = row[0]
                portfolio.pos_handler = PositionHandler.get_positions_by_portfolio_id(portfolio.id, portfolio.currency)

                list_portfolio.append(portfolio)
            
            conn_cursor.close()
            conn_bd.close()
            return list_portfolio
        else:
            pass
            #print("Error al consultar en la BD")
        
        conn_cursor.close()
        conn_bd.close()

        return []
    
    @staticmethod
    def get_list_portfolio_by_asset(asset):
        list_position_portfolio = PositionHandler.get_list_position_portfolio_by_asset(asset)

        list_portfolio = []
        for position_portfolio in list_position_portfolio:
            portfolio = Portfolio.get_portfolio_by_id(position_portfolio.portfolio_id)
            if portfolio:
                list_portfolio.append(portfolio)

        return list_portfolio
    
    def get_list_transactions(self):
        return PositionHandler.get_list_transactions(self.id)

    @staticmethod
    def create_portfolio(name, user_id, start_dt, starting_cash, currency):
        portfolio = Portfolio(name, user_id, start_dt, starting_cash = starting_cash, currency = currency)
        portfolio.current_cash = portfolio.starting_cash
        
        return Portfolio.insert(portfolio)
    
    @staticmethod 
    def end_portfolio(portfolio):
        # portfolio.end_dt = datetime.now()
        # 1. update portfolio into db
        # 2. return success or failure
        pass


    @property
    def total_market_value(self):
        """
        Obtain the total market value of the portfolio excluding cash.
        """
        return self.pos_handler.total_market_value()

    @property
    def total_equity(self):
        """
        Obtain the total market value of the portfolio including cash.
        """
        return self.total_market_value + self.current_cash

    @property
    def total_unrealised_pnl(self):
        """
        Calculate the sum of all the positions' unrealised P&Ls.
        """
        return self.pos_handler.total_unrealised_pnl()

    @property
    def total_realised_pnl(self):
        """
        Calculate the sum of all the positions' realised P&Ls.
        """
        return self.pos_handler.total_realised_pnl(self.id, self.currency)

    @property
    def total_pnl(self):
        """
        Calculate the sum of all the positions' total P&Ls.
        """
        return self.pos_handler.total_pnl(self.id, self.currency)

    
    def transact_asset(self, txn):
        """
        Adjusts positions to account for a transaction.
        """
        if txn.dt < self.current_dt:
            raise ValueError(
                'Transaction datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'transact assets.' % (txn.dt, self.current_dt)
            )
        self.current_dt = txn.dt

        txn_share_cost = txn.price * txn.quantity
        txn_total_cost = txn_share_cost + txn.commission

        if txn_total_cost > self.current_cash:
            #if settings.PRINT_EVENTS:
            print(
                'WARNING: Not enough cash in the portfolio to '
                'carry out transaction. Transaction cost of %s '
                'exceeds remaining cash of %s. Transaction '
                'will proceed with a negative cash balance.' % (
                    txn_total_cost, self.current_cash
                )
            )

        self.pos_handler.transact_position(self.id, txn)

        self.current_cash = Decimal(self.current_cash) - txn_total_cost

      

    def portfolio_to_dict(self):
        """
        Output the portfolio holdings information as a dictionary
        with Assets as keys and sub-dictionaries as values.
        This excludes cash.
        Returns
        -------
        `dict`
            The portfolio holdings.
        """
        holdings = {}
        for asset, pos in self.pos_handler.positions.items():
            holdings[asset] = {
                "position_id": pos.id,
                "quantity": pos.net_quantity,
                "market_value": pos.market_value,
                "unrealised_pnl": pos.unrealised_pnl,
                "realised_pnl": pos.realised_pnl,
                "total_pnl": pos.total_pnl,
                "distribution": int((pos.market_value/self.total_market_value)*100)
            }
        return holdings

    @property
    def ticker_list(self):
        ticker_list = []
        for asset, pos in self.pos_handler.positions.items():
            ticker_list.append(asset)
        return ticker_list

    @property
    def weight_list(self):
        weights = []
        for asset, pos in self.pos_handler.positions.items():
            weights.append(int((pos.market_value/self.total_market_value)*100))
        return weights

    @property
    def color_list(self):
        colors = []
        color_nuance = 192
        for asset, pos in self.pos_handler.positions.items():
            colors.append("rgba(75,192," + str(color_nuance) + ",0.4)")
            color_nuance = color_nuance + 50
        return colors

    def update_market_value_of_asset(self, asset, current_price, current_dt):
        """
        Update the market value of the asset to the current
        trade price and date.
        """
        if asset not in self.pos_handler.positions:
            return
        else:
            if current_price < 0.0:
                raise ValueError(
                    'Current trade price of %s is negative for '
                    'asset %s. Cannot update position.' % (
                        current_price, asset
                    )
                )

            if current_dt < self.current_dt:
                raise ValueError(
                    'Current trade date of %s is earlier than '
                    'current date %s of asset %s. Cannot update '
                    'position.' % (
                        current_dt, self.current_dt, asset
                    )
                )

            self.pos_handler.positions[asset].update_current_price(
                current_price, current_dt
            )
    
    def update_market_value_of_assets(self):
        return self.pos_handler.update_market_value_of_assets()

 

    

    

    