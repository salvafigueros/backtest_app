from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response
from .stock import Stock
from .futures import Futures
from .user import User
import queue 
from .backtesting.data.historicDBDataHandler import HistoricDBDataHandler
from .backtesting.conservativePortfolio import ConservativePortfolio
from .backtesting.simulatedExecutionHandler import SimulatedExecutionHandler
from .backtesting.strategy.buyMaxStrategy import BuyMaxStrategy
from .backtesting.strategy.shortMaxStrategy import ShortMaxStrategy
from .backtesting.strategy.buyMinStrategy import BuyMinStrategy
from .backtesting.strategy.shortMinStrategy import ShortMinStrategy
from .backtesting.strategy.strategy import Strategy
from .backtesting.backtesting import Backtesting
from .backtesting.backtesting_assets import Backtesting_Assets
from .backtestingForm import AssetBacktestingForm, PortfolioBacktestingForm, OptimizationBacktestingForm, BacktestingViewForm
import json 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import plotly
import io
import os

views_backtesting = Blueprint('views_backtesting', __name__)


@views_backtesting.route('/backtesting/preview', methods=['GET', 'POST'])
def backtesting_preview():
    backtesting_id = request.args.get('id')
    if backtesting_id:
        backtesting = Backtesting.get_backtesting_by_id(backtesting_id)
        if backtesting:
            user = User.get_user_by_id(backtesting.user_id)
            strategy = Strategy.get_strategy_by_id(backtesting.strategy_id)
            strategies = {"buymax": BuyMaxStrategy(strategy.time_fraem, strategy.exit_trade, strategy.exit_conguration),
                            "buymin": BuyMinStrategy(strategy.time_fraem, strategy.exit_trade, strategy.exit_conguration),
                            "shortmax": ShortMaxStrategy(strategy.time_fraem, strategy.exit_trade, strategy.exit_conguration),
                            "shortmin": ShortMinStrategy(strategy.time_fraem, strategy.exit_trade, strategy.exit_conguration)}
            backtesting_assets = Backtesting_Assets.get_backtesting_assets_by_backtesting_id(backtesting_id)
            return render_template("backtesting_preview.html", backtesting=backtesting, user=user, strategy=strategies[strategy.strategy], ticker_list = backtesting_assets.ticker_list)

    return redirect(url_for('views.home'))



@views_backtesting.route('/backtesting/save-backtesting', methods=['POST'])
def backtesting_save_backtesting():
    #backtesting = json.loads(request.data)
    backtesting = request.get_json()
    backtesting = Backtesting.save_backtesting_in_bd(backtesting['user_id'],
                                                        backtesting['starting_cash'],
                                                        backtesting['currency'],
                                                        backtesting['ticker_list'],
                                                        backtesting['strategy'],
                                                        backtesting['time_frame'],
                                                        backtesting['exit_trade'],
                                                        backtesting['exit_configuration'])
    
    return jsonify({"button": "." + backtesting.strategy.get_name()})

@views_backtesting.route('/backtesting/asset', methods=['GET', 'POST'])
def backtesting_asset():
    form = AssetBacktestingForm()

    if form.validate_on_submit():
        ticker = form.asset.data
        starting_cash = int(form.starting_capital.data)
        currency = form.currency.data
        time_frame = int(form.time_frame.data)

        strategies = {
            "buymax": form.buymax.data,
            "shortmax": form.shortmax.data,
            "buymin": form.buymin.data,
            "shortmin": form.shortmin.data
        }

        strategies = {key: value for key, value in strategies.items() if value == True}

        exit_trade = form.exit_trade.data
        exit_time_frame = int(form.exit_time_frame.data)
        atr_multiplier = int(form.atr_multiplier.data)

        backtesting = True
        exit_configuration = exit_time_frame if exit_trade == "exit_time_frame" else  atr_multiplier

        """
        
  
        #Comprobar que el valor de time_frame es uno de los valores propuestos.
        if not strategies:
            flash('Es obligatorio seleccionar alguna de las opciones del campo Estrategia.', category='error')
            backtesting = False
        #Comprobar que el valor de strategy es uno de los valores propuestos.
        """

        if backtesting:
            ticker_list = [ticker]

            list_backtesting = {}
            list_backtesting_info = {}
            for key, value in strategies.items():
                backtesting = Backtesting.create_backtesting_from_user(None, None, starting_cash, currency, ticker_list, key, time_frame, exit_trade, exit_configuration)

                backtesting.execute_backtesting()

                list_backtesting[key] = enumerate(backtesting.output_results_backtesting())
                list_backtesting_info[key] = backtesting

            return render_template("backtesting.html", list_backtesting=list_backtesting, list_backtesting_info=list_backtesting_info)

            
    return render_template("backtesting_asset.html", form=form)


@views_backtesting.route('/backtesting/portfolio', methods=['GET', 'POST'])
def backtesting_portfolio():
    form = PortfolioBacktestingForm()

    if request.method == 'POST':
        tickers = request.form.getlist('asset[]') 
        starting_cash = int(request.form.get('starting_cash'))
        currency = request.form.get('currency')
        time_frame = int(request.form.get('time_frame'))
        strategies = request.form.getlist('strategy[]')
        exit_trade = request.form.get('exit')
        exit_time_frame = int(request.form.get('exit_time_frame'))
        atr_multiplier = int(request.form.get('ATR_multiplier'))

        backtesting = True
        exit_configuration = exit_time_frame if exit_trade == "exit_time_frame" else  atr_multiplier

        """
        if not tickers:
            flash('Es obligatorio rellenar el campo Activo.', category='error')
            backtesting = False
        else:
            for ticker in tickers:
                if (not Futures.get_futures_by_ticker(ticker)) and (not Stock.get_stock_by_ticker(ticker)):
                    flash('No existe el ticker introducido: ' + ticker, category='error')
                    backtesting = False
        if not starting_cash:
            flash('Es obligatorio rellenar el campo Capital.', category='error')
            backtesting = False
        else:
            starting_cash = int(starting_cash)
            if starting_cash <= 0:
                flash('El campo Capital tiene que ser mayor que 0.', category='error')
                backtesting = False
        if not currency:
            flash('Es obligatorio rellenar el campo Moneda.', category='error')
            backtesting = False
        if not time_frame:
            flash('Es obligatorio seleccionar una opción en el campo Marco Temporal.', category='error')
            backtesting = False
        else: time_frame = int(time_frame)
        #Comprobar que el valor de time_frame es uno de los valores propuestos.
        if not strategies:
            flash('Es obligatorio seleccionar alguna de las opciones del campo Estrategia.', category='error')
            backtesting = False
        #Comprobar que el valor de strategy es uno de los valores propuestos.
        if not trading_exit:
            flash('Es obligatorio seleccionar una opción en el campo Salida.', category='error')
            backtesting = False
        else:
            if trading_exit == "exittime":
                if not exit_time_frame:
                    flash('Es obligatorio seleccionar una opción en el campo Stop Temporal.', category='error')
                    backtesting = False
                else:
                    exit_time_frame = int(exit_time_frame)
                    if exit_time_frame not in [1, 2, 3]:
                        flash('La opción seleccionada en el campo Stop Temporal no es válida.', category='error')
                        backtesting = False
                    else:
                        exit_configuration = exit_time_frame
            elif trading_exit == "trailingstop":
                if not atr_multiplier:
                    flash('Es obligatorio seleccionar una opción en el campo Multiplicador ATR.', category='error')
                    backtesting = False
                else:
                    atr_multiplier = int(atr_multiplier)
                    if atr_multiplier not in  [1, 2, 3]:
                        flash('La opción seleccionada en el campo Multiplicador ATR no es válida.', category='error')
                        backtesting = False
                    else:
                        exit_configuration = atr_multiplier
            else:
                flash('La opción seleccionada en el campo Salida no es válida.', category='error')
                backtesting = False
            """

        if backtesting:
            ticker_list = tickers

            list_backtesting = {}
            list_backtesting_info = {}
            for s in strategies:
                backtesting = Backtesting.create_backtesting_from_user(None, None, starting_cash, currency, ticker_list, s, time_frame, exit_trade, exit_configuration)

                backtesting.execute_backtesting()

                list_backtesting[s] = enumerate(backtesting.output_results_backtesting())
                list_backtesting_info[s] = backtesting

            return render_template("backtesting.html", list_backtesting=list_backtesting, list_backtesting_info=list_backtesting_info)

            
    return render_template("backtesting_portfolio.html")



@views_backtesting.route('/backtesting/metrics', methods=['GET', 'POST'])
def backtesting_metrics():
    if request.method == 'POST':
        metric = request.form.get('metric') 
        
        if not metric:
            flash('Es obligatorio seleccionar una opción en el campo Métrica.', category='error')
        else:
            list_stocks = Stock.get_list_stocks_by_metric(metric)
            return render_template("backtesting_metrics_value.html", metric=metric, list_stocks=list_stocks)

    return render_template("backtesting_metrics.html")


@views_backtesting.route('/backtesting/metrics/value', methods=['GET', 'POST'])
def backtesting_metrics_value():
    if request.method == 'POST':
        metric = request.form.get('metric')
        separator = request.form.get('separator') 

        return render_template("backtesting_metrics_value_config.html", metric=metric, separator=separator)

    return render_template("backtesting_metrics.html")


@views_backtesting.route('/backtesting/metrics/config', methods=['GET', 'POST'])
def backtesting_metrics_config():
    if request.method == 'POST':
        metric = request.form.get('metric')
        separator = request.form.get('separator') 
        separator = int(separator)
        tickers = request.form.getlist('asset[]') 
        starting_cash = request.form.get('starting_cash')
        currency = request.form.get('currency')
        time_frame = request.form.get('time_frame')
        strategies = request.form.getlist('strategy[]')
        trading_exit = request.form.get('exit')
        exit_time_frame = request.form.get('exit_time_frame')
        atr_multiplier = request.form.get('ATR_multiplier')

        backtesting = True
        exit_configuration = None

        if not starting_cash:
            flash('Es obligatorio rellenar el campo Capital.', category='error')
            backtesting = False
        else:
            starting_cash = int(starting_cash)
            if starting_cash <= 0:
                flash('El campo Capital tiene que ser mayor que 0.', category='error')
                backtesting = False
        if not currency:
            flash('Es obligatorio rellenar el campo Moneda.', category='error')
            backtesting = False
        if not time_frame:
            flash('Es obligatorio seleccionar una opción en el campo Marco Temporal.', category='error')
            backtesting = False
        else: time_frame = int(time_frame)
        #Comprobar que el valor de time_frame es uno de los valores propuestos.
        if not strategies:
            flash('Es obligatorio seleccionar alguna de las opciones del campo Estrategia.', category='error')
            backtesting = False
        #Comprobar que el valor de strategy es uno de los valores propuestos.
        if not trading_exit:
            flash('Es obligatorio seleccionar una opción en el campo Salida.', category='error')
            backtesting = False
        else:
            if trading_exit == "exittime":
                if not exit_time_frame:
                    flash('Es obligatorio seleccionar una opción en el campo Stop Temporal.', category='error')
                    backtesting = False
                else:
                    exit_time_frame = int(exit_time_frame)
                    if exit_time_frame not in [1, 2, 3]:
                        flash('La opción seleccionada en el campo Stop Temporal no es válida.', category='error')
                        backtesting = False
                    else:
                        exit_configuration = exit_time_frame
            elif trading_exit == "trailingstop":
                if not atr_multiplier:
                    flash('Es obligatorio seleccionar una opción en el campo Multiplicador ATR.', category='error')
                    backtesting = False
                else:
                    atr_multiplier = int(atr_multiplier)
                    if atr_multiplier not in  [1, 2, 3]:
                        flash('La opción seleccionada en el campo Multiplicador ATR no es válida.', category='error')
                        backtesting = False
                    else:
                        exit_configuration = atr_multiplier
            else:
                flash('La opción seleccionada en el campo Salida no es válida.', category='error')
                backtesting = False

        if backtesting:
            list_stocks = Stock.get_all_stocks()
            lists_tickers = {}

            lists_tickers["Group 1"] = []
            lists_tickers["Group 2"] = []

            for stock in list_stocks:
                if stock.metric <= separator:
                    lists_tickers["Group 1"].append(stock.ticker)
                else:
                    lists_tickers["Group 2"].append(stock.ticker)

            results_backtesting = {}

            for key, value in lists_tickers.items():
                ticker_list = value
                list_backtesting = {}

                for s in strategies:
                    events = queue.Queue()
                    bars = HistoricDBDataHandler(events, ticker_list)
                    port = ConservativePortfolio(bars, events, bars.get_start_date(), starting_cash)
                    simulator = SimulatedExecutionHandler(events)
                    list_backtesting[s] = None
                    strategy = None

                    if s == "buymax":
                        strategy = BuyMaxStrategy(bars, events, time_frame, trading_exit, exit_configuration)
                    elif s == "shortmax":
                        strategy = ShortMaxStrategy(bars, events, time_frame, trading_exit, exit_configuration)
                    elif s == "buymin":
                        strategy = BuyMinStrategy(bars, events, time_frame, trading_exit, exit_configuration)
                    elif s == "shortmin":
                        strategy = ShortMinStrategy(bars, events, time_frame, trading_exit, exit_configuration)

                
                    backtesting = Backtesting(ticker_list, events, bars, strategy, port, simulator)

                    backtesting.execute_backtesting()

                    list_backtesting[s] = enumerate(backtesting.output_results_backtesting())

                results_backtesting[key] = list_backtesting

            return render_template("backtesting_groups.html", results_backtesting=results_backtesting, metric=metric)

        return render_template("backtesting_metrics_value_config.html", metric=metric, separator=separator)

    return render_template("backtesting_metrics.html")


@views_backtesting.route('/backtesting/optimization-weight', methods=['GET', 'POST'])
def backtesting_optimization_weight():
    form = OptimizationBacktestingForm()

    if form.validate_on_submit():
        #ticker_list = form.assets.data
        ticker_list = request.form.getlist('asset[]') 
        return_portfolio = int(form.return_portfolio.data)/100
        starting_capital = int(form.starting_capital.data)

        df = Stock.get_df_prices(ticker_list) 
        #df = (1 + df.pct_change())
        df = np.log(1 + df.pct_change())

        returns = []
        stds = []
        w = []

        for i in range(500):
            weights = weights_creator(df)
            returns.append(portfolio_return(weights, df))
            stds.append(portfolio_std(weights, df))
            w.append(weights)

        
        #Select weight of 
        """
        returns_user = [retorno for retorno in returns if retorno <= return_portfolio*1.1 and retorno >= return_portfolio*0.9] #Hay que aproximar, no tiene que ser exactamente el mismo número
        stds_user = []
        for return_user in returns_user:
            stds_user.append(stds[returns.index(return_user)]) 

        weight = weights[stds.index(min(stds_user))]
        return_user = returns_user[stds.index(min(stds_user))]

        #graficar la efficient frontier 
        plt.scatter(std, returns)
        plt.scatter(df.std().iloc[0]*np.sqrt(250), df.mean().iloc[0], c='k')
        plt.scatter(df.std().iloc[1]*np.sqrt(250), df.mean().iloc[1], c='yellow')
        plt.scatter(min(stds_user), returns[stds.index(min(stds_user))], c='green')
        plt.title("Efficient Frontier")
        plt.xlabel("Portfolio std")
        plt.ylabel("Portfolio Return")
        plt.show()
        """
        
        plt.scatter(stds, returns)
        plt.scatter(df.std().iloc[0]*np.sqrt(250), df.mean().iloc[0], c='k')
        plt.scatter(df.std().iloc[1]*np.sqrt(250), df.mean().iloc[1], c='yellow')
        plt.scatter(min(stds), returns[stds.index(min(stds))], c='green')
        plt.title("Efficient Frontier")
        plt.xlabel("Portfolio std")
        plt.ylabel("Portfolio Return")
        n = np.random.random()
        plt.savefig('website/static/images/portfolio_optimization' + str(n) + '.png')
        


        return render_template("backtesting_optimization_results.html", ticker_list=ticker_list, starting_capital=starting_capital, weight=w[returns.index(max(returns))], return_user=max(returns), std_user=stds[returns.index(max(returns))], url = "../static/images/portfolio_optimization" + str(n) + ".png")

    return render_template("backtesting_optimization_assets.html", form=form)

@views_backtesting.route('/backtesting/optimization-portfolio', methods=['GET'])
def backtesting_optimization_portfolio():
    #ticker_list = form.assets.data
    list_stock = Stock.get_all_stocks()
    ticker_list = []

    for stock in list_stock:
        ticker_list.append(stock.ticker)

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

    plt.scatter(stds, returns)
    plt.scatter(df.std().iloc[0]*np.sqrt(250), df.mean().iloc[0], c='k')
    plt.scatter(df.std().iloc[1]*np.sqrt(250), df.mean().iloc[1], c='yellow')
    plt.scatter(min(stds), returns[stds.index(min(stds))], c='green')
    plt.title("Efficient Frontier")
    plt.xlabel("Portfolio std")
    plt.ylabel("Portfolio Return")
    plt.savefig('website/static/images/portfolio_optimization.png')
        


    return render_template("backtesting_optimization_results.html", ticker_list=ticker_list, starting_capital=100000, weight=w[returns.index(max(returns))], return_user=max(returns), std_user=stds[returns.index(max(returns))], url = "../static/images/portfolio_optimization.png")



def portfolio_return(weights, df):
    return np.dot(df.mean(), weights)

def portfolio_std(weights, df):
    return (np.dot(np.dot(df.cov(), weights), weights))**(1/2)*np.sqrt(250)

def weights_creator(df):
    rand = np.random.random(len(df.columns))
    rand /= rand.sum()

    return rand


@views_backtesting.route('/backtesting/list-my-backtestings', methods=['GET'])
def list_my_backtestings():
    user_id = request.args.get('id')
    if user_id:
        list_backtesting = Backtesting.get_list_backtesting_by_user_id(user_id)

        return render_template("list_backtesting.html", list_backtesting=list_backtesting)

    return redirect(url_for('views.home'))

@views_backtesting.route('/backtesting/view', methods=['GET', 'POST'])
def backtesting_view():
    form = BacktestingViewForm()

    if form.validate_on_submit():
        backtesting_id = form.backtesting_id.data
        backtesting = Backtesting.create_backtesting_from_db(backtesting_id)
        backtesting.execute_backtesting()
        backtesting_output= backtesting.output_results_backtesting()

        print(os.getcwd())
        #url_equity_curve = backtesting.plot_equity_curve()
        plt.plot(backtesting.port.equity_curve.index, backtesting.port.equity_curve['equity_curve'])
        plt.title('Equity Curve Vs Year')
        plt.xlabel('Year')
        plt.ylabel('Equity Curve')
        plt.savefig('website/static/images/equity_curve.png')

        return render_template("backtesting_view.html", form=form, backtesting=backtesting, backtesting_output=backtesting_output, user=User.get_user_by_id(backtesting.user_id), url='../static/images/equity_curve.png')

    backtesting_id = request.args.get('id')

    if backtesting_id:
        backtesting = Backtesting.create_backtesting_from_db(backtesting_id)

        if backtesting:
            return render_template("backtesting_preview.html", backtesting=backtesting, form=form, user=User.get_user_by_id(backtesting.user_id))

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
        Strategy.delete(backtesting.strategy_id)
        Backtesting.delete(backtesting)
        

    return redirect(url_for('views.home'))


@views_backtesting.route('/backtesting/search-backtesting', methods=['GET', 'POST'])
def search_backtesting():
    if request.method == 'POST':
        asset = request.form.get('asset') 
        asset = Stock.get_stock_by_ticker(asset)

        if asset:
            list_backtesting = Backtesting.get_list_backtesting_by_asset(asset)
            if list_backtesting:
                list_backtesting = [backtesting for backtesting in list_backtesting if backtesting.shared == True]
                return render_template("list_backtesting.html", list_backtesting=list_backtesting)

    return render_template("search_backtesting.html")

@views_backtesting.route('/backtesting/equity_curve<int:pid>.png')
def plot_equity_curve(pid):
    backtesting = Backtesting.create_backtesting_from_db(pid)
    backtesting.execute_backtesting()
    backtesting.output_results_backtesting()
    fig = backtesting.plot_equity_curve()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')