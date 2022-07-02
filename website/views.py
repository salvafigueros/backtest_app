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
from .searchNavForm import SearchNavForm

#Chart
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plot
import mpld3
import seaborn as sns
from matplotlib.figure import Figure

import uuid

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if "user_name" in session:
        if ("user_role" in session) and (session["user_role"] == "Admin"):
            return redirect(url_for('views.upload_historic_data'))
        return redirect(url_for('auth.dashboard', id=session["user_id"]))
    else:
        if ("user_id" in session) == False:
            pseudo_id = uuid.uuid1()
            unregistered_user = User.create_unregistered_user(pseudo_id)
            session["user_id"] = unregistered_user.id
        return redirect(url_for('auth.login'))

    return render_template("home.html")


@views.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchNavForm()

    if request.method == "POST":
        #Query (Step 1)
        category = form.category.data
        query = form.query.data


        result = ''
        url = ''

        if category == 'Backtesting' or category == "Portfolio" or category=="Asset":
            stock = Stock.get_stock_by_ticker(query)
            if stock:
                result = stock.id
            else:
                future = Futures.get_futures_by_ticker(query)
                if future:
                    result = future.id
                else:
                    return redirect(url_for('views.home'))

            url = 'views_backtesting.search_backtesting' if category == "Backtesting" else 'views.search_portfolio'

            if category=="Asset":
                url = 'views.search_asset' 

        elif category == 'User':
            result = query
            url = 'auth.search_user'
        else:
            return redirect(url_for('views.home'))
       
        return redirect(url_for(url, id=result))
    
    return redirect(url_for('views.home'))


@views.route('/asset', methods=['GET'])
def search_asset():
    asset_id = request.args.get('id')
    asset = Stock.get_stock_by_id(asset_id)
    asset_prices = None

    if not asset:
        asset = Futures.get_futures_by_id(asset_id)

        if asset:
            asset_prices = asset.get_futures_prices_dates()
            
    else:
        asset_prices = asset.get_stock_prices_dates()

    if asset:
         # Generate the figure **without using pyplot**.
        fig = Figure(figsize=(9, 6))
        ax = fig.subplots()
        ax.plot(asset_prices.index, asset_prices['close'], label=asset.ticker + 'Price')

        # Save it to a temporary buffer.
        buf = io.BytesIO()
        fig.savefig(buf, format="png")

        # Embed the result in the html output.
        chart = base64.b64encode(buf.getbuffer()).decode("ascii")

        return render_template("show_historic_data.html",
                                asset=asset, 
                                asset_prices=asset_prices.to_html(classes=["table-bordered table-striped table-hover"]),
                                chart=chart)
        
    return redirect(url_for('views.home'))

#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'log_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Acceso no autorizado. Por favor, inicia sesión', category='error')
            return redirect(url_for('auth.login'))
    return wrap

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
                    flash('Error al subir los datos históricos. Mira las fechas introducidas.', category='error')

            else:
                company_name = request.form.get('company_name') 
                market = request.form.get('market') 
                currency = request.form.get('currency')

                if company_name and currency and market:
                    stock = Stock.create_stock(ticker, company_name, market, currency)

                    if stock:
                        uploaded = stock.upload_historic_data(first_date, last_date)

                        if uploaded == True:
                            flash('Se han subido los datos históricos con éxito.', category='success') 
                            return redirect(url_for('views.show_historic_data_stocks', id = stock.id, first_date = first_date, last_date = last_date))
                        else:
                            flash('Error al subir los datos históricos. Mira las fechas introducidas.', category='error')
                            flash('El ticker introducido no es un ticker válido en Yahoo! Finance.', category='error')
                            Stock.delete(stock)

                    else:
                        flash('Hay un error con el ticker de la acción introducida.', category='error')
                        return render_template("upload_historic_data.html")
                else:
                    flash('Tienes que introducir el Nombre de la Compañía, el Mercado y la Moneda, ya que se trata de una acción nueva para el sistema.', category='error')

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
                    flash('Error al subir los datos históricos. Mira las fechas introducidas.', category='error')

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
                            flash('Error al subir los datos históricos. Mira las fechas introducidas.', category='error')
                            flash('El ticker introducido no es un ticker válido en Yahoo! Finance.', category='error')
                            Futures.delete(futures)

                    else:
                        flash('Hay un error con el ticker del futuro introducido.', category='error')
                        return render_template("upload_historic_data.html")
                else:
                    flash('Tienes que introducir el Nombre del Futuro y la moneda, ya que se trata de un futuro nuevo para el sistema.', category='error')

        else:
            flash('Tienes que rellenar todos los campos que aparecen por pantalla', category='error')

    return render_template("upload_historic_data.html")



@views.route('/show-historic-data-stocks', methods=['GET'])
@admin_required
def show_historic_data_stocks():
    stock_id = request.args.get('id')
    first_date = request.args.get('first_date')
    last_date = request.args.get('last_date')

    if stock_id and first_date and last_date:
        stock = Stock.get_stock_by_id(stock_id)
        if stock:
            stock_prices = stock.get_stock_prices_dates(first_date, last_date)

            # Generate the figure **without using pyplot**.
            fig = Figure(figsize=(9, 6))
            ax = fig.subplots()
            ax.plot(stock_prices.index, stock_prices['close'], label=stock.ticker + 'Price')

            # Save it to a temporary buffer.
            buf = io.BytesIO()
            fig.savefig(buf, format="png")

            # Embed the result in the html output.
            chart = base64.b64encode(buf.getbuffer()).decode("ascii")

            return render_template("show_historic_data.html",
                                   asset=stock, 
                                   asset_prices=stock_prices.head(50).to_html(classes=["table-bordered table-striped table-hover"]),
                                   chart=chart)

    return redirect(url_for('views.home'))

@views.route('/show-historic-data-futures', methods=['GET'])
@admin_required
def show_historic_data_futures():
    futures_id = request.args.get('id')
    first_date = request.args.get('first_date')
    last_date = request.args.get('last_date')

    if futures_id and first_date and last_date:
        futures = Futures.get_futures_by_id(futures_id)
        if futures:
            futures_prices = futures.get_futures_prices_dates(first_date, last_date)

            # Generate the figure **without using pyplot**.
            fig = Figure(figsize=(9, 6))
            ax = fig.subplots()
            ax.plot(futures_prices.index, futures_prices['close'], label=futures.ticker + 'Price')

            # Save it to a temporary buffer.
            buf = io.BytesIO()
            fig.savefig(buf, format="png")

            # Embed the result in the html output.
            chart = base64.b64encode(buf.getbuffer()).decode("ascii")

            return render_template("show_historic_data.html", 
                                    asset=futures, 
                                    asset_prices=futures_prices.tail(50).to_html(classes=["table-bordered table-striped table-hover"]),
                                    chart=chart)

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
        elif not delete_all and (last_date < first_date):
            valid_data = False
            flash('El orden de las fechas introducidas no es correcto.', category='error')

        if ticker and valid_data:
            stock = Stock.get_stock_by_ticker(ticker)

            if stock:
                if delete_all:
                    deleted = stock.delete_all_historic_data()
                    flash('Se han eliminado con éxito los datos.', category='success')
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
                    flash('El ticker introducido no existe.', category='error')
       
        elif not ticker:
            flash('Tienes que introducir el ticker de la acción.', category = 'error')

    return render_template("delete_historic_data.html")


@views.route('/create-portfolio', methods=['GET', 'POST'])
@is_logged_in
def create_portfolio():
    if request.method == 'POST':
        name = request.form.get('name')
        starting_cash = Decimal(request.form.get('starting_cash'))
        currency = request.form.get('currency')
        assets = request.form.getlist('asset[]')
        quantities = request.form.getlist('quantity[]')

        if name and starting_cash and currency:

            valid_data = True
            i = 0

            while (valid_data == True) and (i < len(assets)):
                asset_object = Stock.get_stock_by_ticker(assets[i])

                if asset_object == False:
                    asset_object = Futures.get_futures_by_ticker(assets[i])

                if asset_object == False:
                    valid_data = False
                    flash('"' + assets[i] + '"' + ' no existe.', category='error')

                i = i+1

            if starting_cash < 1000:
                flash('El capital introducido tiene que ser superior a 1000.', category='error')
                valid_data = False

            if len(assets) != len(quantities):
                flash('Error a la hora de añadir los activos financieros.', category='error')
                valid_data = False
 
            if valid_data == True:
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

            if portfolio:

                if ((portfolio.user_id == session["user_id"]) or portfolio.shared == True) and (portfolio.end_dt is None ):
                    portfolio.update_market_value_of_assets()

                    return render_template("portfolio2.html", portfolio=portfolio, user=User.get_user_by_id(portfolio.user_id))

    return redirect(url_for('views.home'))


@views.route('/portfolio/list', methods=['GET'])
def search_portfolio():
    asset_id = request.args.get('id')
    asset = Stock.get_stock_by_id(asset_id)

    if not asset:
        asset = Futures.get_futures_by_id(asset_id)

    if asset:
        list_portfolio = Portfolio.get_list_portfolio_by_asset(asset.ticker)
        if list_portfolio:
            list_portfolio = [portfolio for portfolio in list_portfolio if (portfolio.shared == True) and (portfolio.end_dt == None)]

        return render_template("search_portfolio.html", list_portfolio=list_portfolio)
        
    return redirect(url_for('views.home'))


@views.route('/list-my-portfolios', methods=['GET'])
@is_logged_in
def list_my_portfolios():
    user_id = request.args.get('id')

    if user_id:
        user_id = int(user_id)

    if user_id and session["user_id"] == user_id:
        list_portfolio = Portfolio.get_list_portfolio_by_user_id(user_id)
        list_portfolio = [portfolio for portfolio in list_portfolio if portfolio.end_dt == None]

        return render_template("search_portfolio_user.html", list_portfolio=list_portfolio, user=User.get_user_by_id(user_id))

    return redirect(url_for('views.home'))

@views.route('/share-portfolio', methods=['GET', 'POST'])
def share_portfolio():
    if request.method == 'POST':
        portfolio_id = request.form.get('portfolio_id')

        if portfolio_id:
            portfolio = Portfolio.get_portfolio_by_id(portfolio_id)

            if portfolio and portfolio.user_id == session["user_id"]:
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

        asset_object = Stock.get_stock_by_ticker(asset)
        if asset_object == False:
            asset_object = Futures.get_futures_by_ticker(asset)
        
        if asset_object:
            portfolio = Portfolio.get_portfolio_by_id(portfolio_id)

            if portfolio and portfolio.user_id == session["user_id"]:
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

            if portfolio and portfolio.user_id == session["user_id"]:
                portfolio.end_dt = datetime.datetime.now()
                portfolio = Portfolio.update(portfolio)
    
    return redirect(url_for('views.home'))
