from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .user import User
from .stock import Stock
from .futures import Futures
from .portfolio.portfolio import Portfolio
from .portfolio.transaction import Transaction
from .portfolio.position import Position
from functools import wraps
import datetime
import pandas as pd
from decimal import *

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

#Check if user is admin
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('user_name' in session) and User.isAdmin(session["user_name"]):
            return f(*args, **kwargs)
        else:
            flash('Acceso no autorizado. Por favor, inicia sesión como administrador', category='error')
            return redirect(url_for('auth.login'))
    return wrap

@views.route('/upload-historic-data')
@admin_required
def upload_historic_data():
    return render_template("upload_historic_data.html")

@views.route('/upload-historic-data-stocks', methods=['GET', 'POST'])
@admin_required
def upload_historic_data_stocks():
    if request.method == 'POST':
        ticker = request.form.get('ticker') 
        first_date = request.form.get('first_date') 
        last_date = request.form.get('last_date') 

        if ticker and first_date and last_date:
            stock = Stock.get_stock_by_ticker(ticker)

            if stock:
                uploaded = stock.upload_historic_data(first_date, last_date)

                if uploaded:
                    flash('Se han subido los datos históricos con éxito.', category='success')
                    return redirect(url_for('views.show_historic_data_stocks', id = stock.id, first_date = first_date, last_date = last_date))
                else:
                    pass

            else:
                company_name = request.form.get('company_name') 
                market = request.form.get('market') 
                currency = request.form.get('currency')

                if company_name and currency:
                    stock = Stock.create_stock(ticker, company_name, market, currency)

                    if stock:
                        uploaded = stock.upload_historic_data(first_date, last_date)

                        if uploaded:
                            flash('Se han subido los datos históricos con éxito.', category='success') 
                            return redirect(url_for('views.show_historic_data_stocks', id = stock.id, first_date = first_date, last_date = last_date))
                        else:
                            pass

                    else:
                        flash('Hay un error con el ticker de la acción introducida.', category='error')
                        return render_template("upload_historic_data.html")
                else:
                    flash('Tienes que introducir el Nombre de la Compañía, ya que se trata de una acción nueva para el sistema.', category='error')

        else:
            flash('Tienes que rellenar todos los campos que aparecen por pantalla', category='error')

    return render_template("upload_historic_data.html")


@views.route('/upload-historic-data-futures', methods=['GET', 'POST'])
@admin_required
def upload_historic_data_futures():
    if request.method == 'POST':
        ticker = request.form.get('ticker') 
        first_date = request.form.get('first_date') 
        last_date = request.form.get('last_date') 

        if ticker and first_date and last_date:
            futures = Futures.get_futures_by_ticker(ticker)

            if futures:
                uploaded = futures.upload_historic_data(first_date, last_date)

                if uploaded:
                    flash('Se han subido los datos históricos con éxito.', category='success')
                    return redirect(url_for('views.show_historic_data_futures', id = futures.id, first_date = first_date, last_date = last_date))
                else:
                    pass

            else:
                futures_name = request.form.get('futures_name') 
                currency = request.form.get('currency')

                if futures_name and currency:
                    futures = Futures.create_futures(ticker, futures_name, currency)

                    if futures:
                        uploaded = futures.upload_historic_data(first_date, last_date)

                        if uploaded:
                            flash('Se han subido los datos históricos con éxito.', category='success') 
                            return redirect(url_for('views.show_historic_data_futures', id = futures.id, first_date = first_date, last_date = last_date))
                        else:
                            pass

                    else:
                        flash('Hay un error con el ticker del futuro introducido.', category='error')
                        return render_template("upload_historic_data.html")
                else:
                    flash('Tienes que introducir el Nombre del Futuro, ya que se trata de un futuro nuevo para el sistema.', category='error')

        else:
            flash('Tienes que rellenar todos los campos que aparecen por pantalla', category='error')

    return render_template("upload_historic_data.html")


@views.route('/show-historic-data-stocks', methods=['GET'])
def show_historic_data_stocks():
    stock_id = request.args.get('id')
    first_date = request.args.get('first_date')
    last_date = request.args.get('last_date')

    if stock_id and first_date and last_date:
        stock = Stock.get_stock_by_id(stock_id)
        if stock:
            stock_prices = stock.get_stock_prices_dates(first_date, last_date)
            return render_template("show_historic_data_stocks.html", stock=stock, stock_prices=stock_prices.to_html())

    return redirect(url_for('views.home'))

@views.route('/show-historic-data-futures', methods=['GET'])
def show_historic_data_futures():
    futures_id = request.args.get('id')
    first_date = request.args.get('first_date')
    last_date = request.args.get('last_date')

    if futures_id and first_date and last_date:
        futures = Futures.get_futures_by_id(futures_id)
        if futures:
            futures_prices = futures.get_futures_prices_dates(first_date, last_date)
            return render_template("show_historic_data_futures.html", futures=futures, futures_prices=futures_prices.to_html())

    return redirect(url_for('views.home'))

@views.route('/delete-historic-data', methods=['GET', 'POST'])
@admin_required
def delete_historic_data():
    if request.method == 'POST':
        ticker = request.form.get('ticker') 
        first_date = request.form.get('first_date') 
        last_date = request.form.get('last_date') 
        delete_all = request.form.get('delete_all') 
        
        valid_data = True
        if not delete_all and (not first_date or not last_date):
            valid_data = False
            flash('Tienes que introducir las fechas.', category='error')

        if ticker and valid_data:
            stock = Stock.get_stock_by_ticker(ticker)

            if stock:
                if delete_all:
                    deleted = stock.delete_all_historic_data()
                    return redirect(url_for("views.home"))
                else:
                    deleted = stock.delete_historic_data(first_date, last_date)
                    return redirect(url_for("views.home"))
            else:
                futures = Futures.get_futures_by_ticker(ticker)

                if futures:
                    if delete_all:
                        deleted = futures.delete_all_historic_data()
                        return redirect(url_for("views.home"))
                    else:
                        deleted = futures.delete_historic_data(first_date, last_date)
                        return redirect(url_for("views.home"))
        else:
            flash('Tienes que introducir el ticker de la acción.', category = 'error')

    return render_template("delete_historic_data.html")


@views.route('/create-portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if request.method == 'POST':
        name = request.form.get('name')
        starting_cash = Decimal(request.form.get('starting_cash'))
        currency = request.form.get('currency')
        assets = request.form.getlist('asset[]')
        quantities = request.form.getlist('quantity[]')

        #Validate data

        if name and starting_cash and currency:
            user = User.search_user(session["user_name"])
            portfolio = Portfolio.create_portfolio(name, user.id, datetime.datetime.now(), starting_cash, currency)
            
            for asset, quantity in zip(assets, quantities):
                asset_object = Stock.get_stock_by_ticker(asset)
                if asset_object == False:
                    asset_object = Futures.get_futures_by_ticker(asset)
                
                if asset_object:
                    transaction = Transaction.create_transaction(user.id, asset, int(quantity))
                    portfolio.transact_asset(transaction)
            
            portfolio = Portfolio.update(portfolio)
            return redirect(url_for('views.view_portfolio', id = portfolio.id))

        else:
            flash('Los campos Nombre, Capital y Moneda son obligatorios.', category='error')

    return render_template("create_portfolio.html")


@views.route('/view-portfolio', methods=['GET'])
def view_portfolio():
    portfolio_id = request.args.get('id')
    if portfolio_id:
        portfolio = Portfolio.get_portfolio_by_id(portfolio_id)
        portfolio.update_market_value_of_assets()
        if portfolio:
            return render_template("portfolio.html", portfolio=portfolio, user=User.get_user_by_id(portfolio.user_id))

    return redirect(url_for('views.home'))

@views.route('/search-portfolio', methods=['GET', 'POST'])
def search_portfolio():
    if request.method == 'POST':
        asset = request.form.get('asset') 
        if asset:
            list_portfolio = Portfolio.get_list_portfolio_by_asset(asset)
            if list_portfolio:
                list_portfolio = [portfolio for portfolio in list_portfolio if portfolio.shared == False]
                return render_template("list_portfolio.html", list_portfolio=list_portfolio)

    return render_template("search_portfolio.html")

@views.route('/list-my-portfolios', methods=['GET'])
def list_my_portfolios():
    user_id = request.args.get('id')
    if user_id:
        list_portfolio = Portfolio.get_list_portfolio_by_user_id(user_id)
        list_portfolio = [portfolio for portfolio in list_portfolio if portfolio.end_dt == None]

        return render_template("list_portfolio.html", list_portfolio=list_portfolio)

    return redirect(url_for('views.home'))

@views.route('/share-portfolio', methods=['GET', 'POST'])
def share_portfolio():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        if portfolio_id:
            portfolio = Portfolio.get_portfolio_by_id(portfolio_id)
            portfolio.shared = True
            portfolio = Portfolio.update(portfolio)

            if portfolio:
                return redirect(url_for('views.view_portfolio', id=portfolio.id))
    
    return redirect(url_for('views.home'))

@views.route('/modify-portfolio', methods=['GET', 'POST'])
def modify_portfolio():
    if request.method == 'POST':
        position_id = request.form.get('position_id')
        portfolio_id = request.form.get('portfolio_id')
        direction = int(request.form.get('direction'))
        quantity = Decimal(request.form.get('quantity'))
        asset = request.form.get('asset')


        user = User.search_user(session["user_name"])
        #position = Position.get_position_by_id(position_id)
        asset_object = Stock.get_stock_by_ticker(asset)
        if asset_object == False:
            asset_object = Futures.get_futures_by_ticker(asset)
        
        if asset_object:
            portfolio = Portfolio.get_portfolio_by_id(portfolio_id)
            transaction = Transaction.create_transaction(user.id, asset, quantity*direction)
            portfolio.transact_asset(transaction)    
            portfolio = Portfolio.update(portfolio)
        else:
            flash('No existe el ticker del activo.', category='error')

        return redirect(url_for('views.view_portfolio', id = portfolio.id))
        

    return redirect(url_for('views.home'))

@views.route('/finish-portfolio', methods=['GET', 'POST'])
def finish_portfolio():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')
        if portfolio_id:
            portfolio = Portfolio.get_portfolio_by_id(portfolio_id)
            portfolio.end_dt = datetime.datetime.now()
            portfolio = Portfolio.update(portfolio)
    
    return redirect(url_for('views.home'))
