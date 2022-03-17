
from .position import Position
from collections import OrderedDict
from .positionPortfolio import PositionPortfolio
from .transaction import Transaction
from ..stock import Stock
from ..futures import Futures
import mysql.connector
from forex_python.converter import CurrencyRates
import datetime
from decimal import *

class PositionHandler(object):
    """
    A class that keeps track of, and updates, the current
    list of Position instances stored in a Portfolio entity.
    """

    def __init__(self, currency="USD"):
        """
        Initialise the PositionHandler object to generate
        an ordered dictionary containing the current positions.
        """
        self.currency = currency
        self.positions = OrderedDict()
        self.c = CurrencyRates()
    
    @staticmethod
    def get_positions_by_portfolio_id(portfolio_id, portfolio_currency):
        pos_handler = PositionHandler(portfolio_currency)
        
        list_positions_portfolio = PositionPortfolio.get_positions_portfolio_by_portfolio_id(portfolio_id)

        for position_portfolio in list_positions_portfolio:
            position = Position.get_position_by_id(position_portfolio.position_id)
            if position.net_quantity != 0:
                pos_handler.positions[position.asset] = position

        return pos_handler

    @staticmethod
    def get_all_positions_by_portfolio_id(portfolio_id, portfolio_currency):
        pos_handler = PositionHandler(portfolio_currency)
        
        list_positions_portfolio = PositionPortfolio.get_positions_portfolio_by_portfolio_id(portfolio_id)

        for position_portfolio in list_positions_portfolio:
            position = Position.get_position_by_id(position_portfolio.position_id)
            pos_handler.positions[position.asset] = position

        return pos_handler

    

    def func_sort_by_dt(e):
        return e.dt

    @staticmethod
    def get_list_transactions(portfolio_id):
        list_transactions = []

        list_positions_portfolio = PositionPortfolio.get_positions_portfolio_by_portfolio_id(portfolio_id)

        '''for asset, position in self.positions.items():
            list_transactions = list_transactions + Transaction.get_list_transactions_by_position_id(position.id)'''

        for position_portfolio in list_positions_portfolio:
            list_transactions = list_transactions + Transaction.get_list_transactions_by_position_id(position_portfolio.position_id)
        
        if list_transactions:
            list_transactions.sort(reverse = True, key=lambda transaction: transaction.dt)

        return list_transactions

    @staticmethod
    def get_list_position_portfolio_by_asset(asset):
        list_position = Position.get_list_position_by_asset(asset)

        list_position_portfolio = []
        for position in list_position:
            list_position_portfolio = list_position_portfolio + PositionPortfolio.get_list_position_portfolio_by_position_id(position.id)

        
        return list_position_portfolio


    def transact_position(self, portfolio_id, transaction):
        """
        Execute the transaction and update the appropriate
        position for the transaction's asset accordingly.
        """
        asset = transaction.asset
        if asset in self.positions:
            self.positions[asset].transact(transaction)
            Position.update(self.positions[asset])
            position_portfolio = PositionPortfolio(portfolio_id, self.positions[asset].id)
            #position_portfolio = PositionPortfolio.insert(position_portfolio)
        else:
            position = Position.create_position(transaction)
            self.positions[asset] = position
            position_portfolio = PositionPortfolio(portfolio_id, position.id)
            position_portfolio = PositionPortfolio.insert(position_portfolio)

        transaction.position_id = self.positions[asset].id
        transaction = Transaction.update(transaction)

        # If the position has zero quantity remove it
        if self.positions[asset].net_quantity == 0:
            del self.positions[asset]

    @staticmethod
    def get_asset_currency(asset):
        asset = Stock.get_stock_by_ticker(asset)
        if asset == False:
            asset = Futures.get_futures_by_ticker(asset)
            if asset == False:
                return 0
        return asset.currency

    def total_market_value(self):
        """
        Calculate the sum of all the positions' market values.
        """
        return sum(
            self.c.convert(PositionHandler.get_asset_currency(asset), self.currency, pos.market_value)
            for asset, pos in self.positions.items() 
        )

    def total_unrealised_pnl(self):
        """
        Calculate the sum of all the positions' unrealised P&Ls.
        """
        return sum(
            self.c.convert(PositionHandler.get_asset_currency(asset), self.currency, pos.unrealised_pnl)
            for asset, pos in self.positions.items() 
        )

    def total_realised_pnl(self, portfolio_id, portfolio_currency):
        """
        Calculate the sum of all the positions' realised P&Ls.
        """
        return sum(
            Decimal(self.c.convert(PositionHandler.get_asset_currency(asset), self.currency, pos.realised_pnl))
            for asset, pos in PositionHandler.get_all_positions_by_portfolio_id(portfolio_id, portfolio_currency).positions.items()
        )

    def total_pnl(self, portfolio_id, portfolio_currency):
        """
        Calculate the sum of all the positions' P&Ls.
        """
        return sum(
            Decimal(self.c.convert(PositionHandler.get_asset_currency(asset), self.currency, pos.total_pnl))
            for asset, pos in PositionHandler.get_all_positions_by_portfolio_id(portfolio_id, portfolio_currency).positions.items()
        )

    def update_market_value_of_assets(self):
        for asset, pos in self.positions.items():
            pos.update_current_price(
                Stock.get_last_quote(asset), datetime.datetime.now()
            )
            Position.update(pos)
        return 
        