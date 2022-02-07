from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .stock import Stock
from .futures import Futures
import queue 
from .historicDBDataHandler import HistoricDBDataHandler
from .conservativePortfolio import ConservativePortfolio
from .simulatedExecutionHandler import SimulatedExecutionHandler
from .buyMaxStrategy import BuyMaxStrategy
from .shortMaxStrategy import ShortMaxStrategy
from .buyMinStrategy import BuyMinStrategy
from .shortMinStrategy import ShortMinStrategy
from .backtesting import Backtesting

views_backtesting = Blueprint('views_backtesting', __name__)


@views_backtesting.route('/backtesting/asset', methods=['GET', 'POST'])
def backtesting_asset():
    if request.method == 'POST':
        ticker = request.form.get('asset') 
        starting_cash = request.form.get('starting_cash')
        currency = request.form.get('currency')
        time_frame = request.form.get('time_frame')
        strategies = request.form.getlist('strategy[]')
        trading_exit = request.form.get('exit')
        exit_time_frame = request.form.get('exit_time_frame')
        atr_multiplier = request.form.get('ATR_multiplier')

        backtesting = True
        exit_configuration = None

        if not ticker:
            flash('Es obligatorio rellenar el campo Activo.', category='error')
            backtesting = False
        elif not Futures.get_futures_by_ticker(ticker) and not Stock.get_stock_by_ticker(ticker):
            flash('No existe el ticker introducido.', category='error')
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

        if backtesting:
            ticker_list = [ticker]

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

            return render_template("backtesting.html", list_backtesting=list_backtesting)

            
    return render_template("backtesting_asset.html")


@views_backtesting.route('/backtesting/portfolio', methods=['GET', 'POST'])
def backtesting_portfolio():
    if request.method == 'POST':
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

        if backtesting:
            ticker_list = tickers

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

            return render_template("backtesting.html", list_backtesting=list_backtesting)

            
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