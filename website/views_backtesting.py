from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response, send_file, g
from .stock import Stock
from .futures import Futures
from .user import User
from functools import wraps

from .backtesting.strategy.strategy import Strategy
from .backtesting.strategy.strategy_factory import StrategyFactory
from .backtesting.strategy.strategyType import StrategyType
from .backtesting.strategy.buyMaxStrategy_builder import BuyMaxStrategyBuilder
from .backtesting.strategy.shortMaxStrategy_builder import ShortMaxStrategyBuilder
from .backtesting.strategy.buyMinStrategy_builder import BuyMinStrategyBuilder
from .backtesting.strategy.shortMinStrategy_builder import ShortMinStrategyBuilder
from .backtesting.strategy.buyAndHoldStrategy_builder import BuyAndHoldStrategyBuilder

from .backtesting.backtesting import Backtesting
from .backtesting.backtesting_assets import Backtesting_Assets
from .backtestingForm import AssetBacktestingForm, OptimizationBacktestingForm, BacktestingViewForm, BacktestingGroupsForm
import json 
import numpy as np
import pandas as pd
import os

#Chart
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure


views_backtesting = Blueprint('views_backtesting', __name__)


def create_strategy_factory():
    strategy_factory = StrategyFactory()
    strategy_factory.register_builder('buymax', BuyMaxStrategyBuilder())
    strategy_factory.register_builder('shortmax', ShortMaxStrategyBuilder())
    strategy_factory.register_builder('buymin', BuyMinStrategyBuilder())
    strategy_factory.register_builder('shortmin', ShortMinStrategyBuilder())
    strategy_factory.register_builder('buyandhold', BuyAndHoldStrategyBuilder())


    return strategy_factory

def get_strategy_factory():
    if 'strategy_factory' not in g:
        g.strategy_factory = create_strategy_factory()

    return g.strategy_factory


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


@views_backtesting.route('/backtesting/save-backtesting', methods=['POST'])
def backtesting_save_backtesting():
    #backtesting = json.loads(request.data)
    backtesting = request.get_json()
    backtesting = Backtesting.get_backtesting_by_id(backtesting['backtesting_id'])
    backtesting.saved = True
    backtesting = Backtesting.save_backtesting(backtesting)
  
    return jsonify({})

@views_backtesting.route('/backtesting/run-form', methods=['GET', 'POST'])
def backtesting_form():  
    form = AssetBacktestingForm()

    if form.validate_on_submit():
        #Portfolio (Step 1)
        name = form.name.data
        starting_cash = int(form.starting_capital.data)
        currency = form.currency.data

        #Tickers (Step 2)
        ticker_list = request.form.getlist('asset[]') 

        #Dates (Step 3)
        start_dt = form.start_dt.data
        end_dt = form.end_dt.data

        valid_data = True

        for ticker in ticker_list:
            asset = Stock.get_stock_by_ticker(ticker)

            if asset.currency != currency:
                flash("No se puede seleccionar el ticker " + ticker + ". Todos los tickers introducidos tienen que estar denominados en la moneda de la cartera:  " + currency + ".", category='error')
                valid_data = False

            if asset:
                if (Stock.price_already_in_bd(asset.id, start_dt) == False) or (Stock.price_already_in_bd(asset.id, end_dt) == False):
                    flash("No existe los datos seleccionados para el ticker introducido: " + ticker, category='error')
                    valid_data = False
            else:
                asset = Futures.get_futures_by_ticker(ticker)
                if asset:
                    if (Futures.price_already_in_bd(asset.id, start_dt) == False) or (Futures.price_already_in_bd(asset.id, end_dt) == False):
                        flash("No existe los datos seleccionados para el ticker introducido: " + ticker, category='error')
                        valid_data = False
                else:
                    flash("No existe el ticker introducido: " + ticker, category='error')
                    valid_data = False
                
        if valid_data == True:
            #Strategy (Step 4)
            strategy_conf = {}
            strategy_name = form.strategy.data

            #Configuration Strategy (Step 5)
            strategy_conf["time_frame"] = int(form.time_frame.data)
            strategy_conf["exit_trade"] = form.exit_trade.data
            exit_time_frame = int(form.exit_time_frame.data)
            atr_multiplier = int(form.atr_multiplier.data)
            strategy_conf["exit_configuration"] = exit_time_frame if strategy_conf["exit_trade"] == "exit_time_frame" else  atr_multiplier

            #Create Strategy (Step 6)
            strategy_factory = get_strategy_factory()
            strategy = strategy_factory.get(strategy_name, **strategy_conf)

            if strategy:
                strategy_type = StrategyType.create_strategy_type(strategy_name)
                strategy = strategy.save_strategy(strategy_type.id)

            #Create Backtesting
            backtesting = Backtesting.create_backtesting_from_user(session["user_id"], name, starting_cash, currency, start_dt, end_dt, ticker_list, strategy_type)


            return redirect(url_for('views_backtesting.backtesting_view', id=backtesting.id))

    
    return render_template("backtesting_form.html", form=form)


@views_backtesting.route('/backtesting/view', methods=['GET', 'POST'])
def backtesting_view():
    form = BacktestingViewForm()

    #Run Backtesting
    if form.validate_on_submit():
        #Get Backtesting from DB
        backtesting_id = form.backtesting_id.data
        backtesting = Backtesting.create_backtesting_from_db(backtesting_id)
        backtesting.set_strategy(get_strategy_factory())


        #Execute Backtesting
        backtesting.execute_backtesting()
        backtesting_output= backtesting.output_results_backtesting()
        #list_trading_signals_chart = backtesting.port.list_trading_signals_chart(10, 7)

        #Benchmark (Buy & Hold)
        benchmark = backtesting.benchmark_backtesting()

        #Stock List
        asset_list = [Stock.get_stock_by_ticker(ticker) for ticker in backtesting.strategy.ticker_list]

        return render_template("backtesting_view.html",
                               form=form, 
                               backtesting=backtesting, 
                               backtesting_output=backtesting_output,
                               benchmark=benchmark, 
                               user=User.get_user_by_id(backtesting.user_id), 
                               asset_list=asset_list)

    backtesting_id = request.args.get('id')

    #View Backtesting
    if backtesting_id:
        backtesting = Backtesting.create_backtesting_from_db(backtesting_id)

        if backtesting and ((backtesting.shared == True) or (backtesting.user_id == session["user_id"])):
            backtesting.set_strategy(get_strategy_factory())

            if backtesting:
                return render_template("backtesting_preview.html", backtesting=backtesting, form=form, user=User.get_user_by_id(backtesting.user_id))

    return redirect(url_for('views.home'))


@views_backtesting.route('/backtesting/equity-curve-chart', methods=['GET', 'POST'])
def backtesting_equity_curve():
    backtesting_id = request.args.get('backtesting_id') 
    backtesting = Backtesting.create_backtesting_from_db(backtesting_id)
    backtesting.set_strategy(get_strategy_factory())


    if backtesting:
        #Execute Backtesting
        backtesting.execute_backtesting()
        backtesting_output= backtesting.output_results_backtesting()
        df = backtesting.equity_curve

        fig, ax = plt.subplots(figsize=(7,7))
        ax = sns.set(style="darkgrid")
        sns.lineplot(data=df, x=df.index, y="equity_curve")
        canvas = FigureCanvas(fig)
        img = io.BytesIO()
        fig.savefig(img)
        img.seek(0)

    return send_file(img, mimetype='img/png')




@views_backtesting.route('/backtesting/metrics-groups', methods=['GET', 'POST'])
def backtesting_metric_groups_form():
    form = BacktestingGroupsForm()

    if form.validate_on_submit():
        #Metric (Step 1)
        metric = form.metric.data

        #Portfolio (Step 2)
        starting_cash = int(form.starting_capital.data)
        currency = form.currency.data

        #Tickers (Step 3)
        ticker_list = request.form.getlist('asset[]') 

        #Dates (Step 4)
        start_dt = form.start_dt.data
        end_dt = form.end_dt.data

        #Strategy (Step 5)
        strategy_conf = {}
        strategy_name = form.strategy.data

        #Configuration Strategy (Step 6)
        strategy_conf["time_frame"] = int(form.time_frame.data)
        strategy_conf["exit_trade"] = form.exit_trade.data
        exit_time_frame = int(form.exit_time_frame.data)
        atr_multiplier = int(form.atr_multiplier.data)
        strategy_conf["exit_configuration"] = exit_time_frame if strategy_conf["exit_trade"] == "exit_time_frame" else  atr_multiplier

        #Create Strategy (Step 7)
        strategy_factory = get_strategy_factory()
        strategy_1 = strategy_factory.get(strategy_name, **strategy_conf)
        strategy_2 = strategy_factory.get(strategy_name, **strategy_conf)

        if strategy_1:
            strategy_type_1 = StrategyType.create_strategy_type(strategy_name)
            strategy_1 = strategy_1.save_strategy(strategy_type_1.id)

        if strategy_2:
            strategy_type_2 = StrategyType.create_strategy_type(strategy_name)
            strategy_2 = strategy_2.save_strategy(strategy_type_2.id)

        #Create Groups - Divide list in two halfs (Step 7)
        list_stocks = Stock.get_list_stocks_by_metric(metric, ticker_list)
        list_stocks.sort(key=lambda x: x.metric)
        list_stocks_1 = list_stocks[:len(list_stocks)//2]
        ticker_list_1 = [stock.ticker for stock in list_stocks_1]
        list_stocks_2 = list_stocks[len(list_stocks)//2:]
        ticker_list_2 = [stock.ticker for stock in list_stocks_2]

        


        #Create Backtesting
        #User default: 19 (it needs to be changed)
        backtesting_1 = Backtesting.create_backtesting_from_user(session["user_id"], "Conjunto Menor", starting_cash, currency, start_dt, end_dt, ticker_list_1, strategy_type_1)
        backtesting_2 = Backtesting.create_backtesting_from_user(session["user_id"], "Conjunto Mayor", starting_cash, currency, start_dt, end_dt, ticker_list_2, strategy_type_2)

        list_backtesting = [backtesting_1, backtesting_2]
        for backtesting in list_backtesting: backtesting.set_strategy(get_strategy_factory())

        return render_template("backtesting_by_groups.html", list_backtesting=list_backtesting, metric=metric)
    
    return render_template("backtesting_metric_groups_form.html", form=form)


@views_backtesting.route('/backtesting/optimization-portfolio', methods=['GET', 'POST'])
def optimization_portfolio():
    form = OptimizationBacktestingForm()

    if form.validate_on_submit():
        starting_capital = int(form.starting_capital.data)
        currency = form.currency.data
        allAssets = form.allAssets.data

        ticker_list = []
        valid_data = True
        if allAssets is True:
            list_stock = Stock.get_all_stocks()
            for stock in list_stock:
                ticker_list.append(stock.ticker)
        else:
            ticker_list = request.form.getlist('asset[]') 

            i = 0
            while (valid_data == True) and (i < len(ticker_list)):
                asset_object = Stock.get_stock_by_ticker(ticker_list[i])

                if asset_object == False:
                    asset_object = Futures.get_futures_by_ticker(ticker_list[i])

                if asset_object == False:
                    valid_data = False
                    flash('"' + ticker_list[i] + '"' + ' no existe.', category='error')

                i = i+1

        
        if valid_data == True:
            df = Stock.get_df_prices(ticker_list) 
            df = np.log(1 + df.pct_change())

            returns = []
            stds = []
            w = []

            for i in range(500):
                weights = weights_creator(df)
                returns.append(portfolio_return(weights, df))
                stds.append(portfolio_std(weights, df))
                w.append(weights)

            return render_template("backtesting_optimization_results.html", 
                                    ticker_list=ticker_list, 
                                    efficient_frontier=efficient_frontier_html(returns, stds), 
                                    starting_capital=starting_capital, currency=currency, 
                                    weight=w[returns.index(max(returns))], 
                                    return_user=max(returns), 
                                    std_user=stds[returns.index(max(returns))], 
                                    color_list=color_list(ticker_list))

    return render_template("backtesting_optimization_assets.html", form=form)


def portfolio_return(weights, df):
    return np.dot(df.mean(), weights)

def portfolio_std(weights, df):
    return (np.dot(np.dot(df.cov(), weights), weights))**(1/2)*np.sqrt(250)

def weights_creator(df):
    rand = np.random.random(len(df.columns))
    rand /= rand.sum()

    return rand

def color_list(ticker_list):
    colors = []
    color_nuance = 192
    for ticker in ticker_list:
        colors.append("rgba(75,192," + str(color_nuance) + ",0.4)")
        color_nuance = color_nuance + 50
    return colors

def efficient_frontier_html(returns, stds):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.scatter(returns, stds)
    # Save it to a temporary buffer.
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data


@views_backtesting.route('/backtesting/list-my-backtestings', methods=['GET'])
@is_logged_in
def list_my_backtestings():
    user_id = request.args.get('id')

    if user_id:
        user_id = int(user_id)

    if user_id and user_id == session["user_id"]:
        list_backtesting = Backtesting.get_list_backtesting_by_user_id(user_id)
        list_backtesting = [backtesting for backtesting in list_backtesting if backtesting.saved == True]
        for backtesting in list_backtesting: backtesting.set_strategy(get_strategy_factory())

        return render_template("search_backtesting_user.html", list_backtesting=list_backtesting, user=User.get_user_by_id(user_id))

    return redirect(url_for('views.home'))


@views_backtesting.route('/backtesting/share', methods=['POST'])
def backtesting_share():
    backtesting = request.get_json()
    backtesting = Backtesting.create_backtesting_from_db(backtesting['backtesting_id'])
    backtesting.shared = True
    backtesting = Backtesting.save_backtesting(backtesting)
    
    return jsonify({})

@views_backtesting.route('/backtesting/delete', methods=['POST'])
def backtesting_delete():
    form = BacktestingViewForm()

    if form.validate_on_submit():
        backtesting_id = form.backtesting_id.data

        backtesting = Backtesting.create_backtesting_from_db(backtesting_id)
        StrategyType.delete(backtesting.strategy_id)
        Backtesting.delete(backtesting)
        

    return redirect(url_for('views.home'))


@views_backtesting.route('/backtesting/list', methods=['GET'])
def search_backtesting():
    asset_id = request.args.get('id')
    asset = Stock.get_stock_by_id(asset_id)

    if asset:
        list_backtesting = Backtesting.get_list_backtesting_by_asset(asset)
        for backtesting in list_backtesting: backtesting.set_strategy(get_strategy_factory())

        if list_backtesting:
            list_backtesting = [backtesting for backtesting in list_backtesting if backtesting.shared == True]
            return render_template("search_backtesting.html", list_backtesting=list_backtesting, ticker=asset.ticker)

    return redirect(url_for('views.home'))


@views_backtesting.route('/backtesting/equity_curve<int:pid>.png')
def plot_equity_curve(pid):
    backtesting = Backtesting.create_backtesting_from_db(pid)
    backtesting.execute_backtesting()
    backtesting.output_results_backtesting()
    fig = backtesting.plot_equity_curve()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')