from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, IntegerField, FieldList, FormField, HiddenField, DateField, DecimalField
from wtforms.validators import ValidationError, InputRequired, NumberRange, Optional
from.stock import Stock
from .futures import Futures

def asset(message=None):
    message = 'No existe el ticker introducido.' 

    def _asset(form, field):
        if (not Futures.get_futures_by_ticker(field.data)) and (not Stock.get_stock_by_ticker(field.data)):
            raise ValidationError(message)

    return _asset

def min_starting_capital(message=None):
    message = 'El capital introducido tiene que ser superior a 1000.' 

    def _min_starting_capital(form, field):
        if field.data < 1000:
            raise ValidationError(message)

    return _min_starting_capital

def validate_finish_date(message=None):
    message = 'La Fecha Final tiene que ser posterior a la Fecha Inicial.' 

    def _validate_finish_date(form, field):
        if field.data < form.start_dt.data:
            raise ValidationError(message)

    return _validate_finish_date


class BacktestingForm(FlaskForm):
    start_dt = DateField(u'Fecha de Inicio', validators=[InputRequired()], format="%Y-%m-%d")
    end_dt = DateField(u'Fecha de Fin', validators=[InputRequired(), validate_finish_date()], format="%Y-%m-%d")

    strategy = SelectField(u'Estrategia', validators=[InputRequired()], choices=[('',''),
                                                                                ('buymax', 'Comprar Máximos'),
                                                                                ('shortmax', 'Vender Máximos'),
                                                                                ('buymin', 'Comprar Mínimos'),
                                                                                ('shortmin', 'Vender Mínimos')])
                                                                                #('dualmovingaveragecrossover', 'Cruce de Dos Medias Móviles'),
                                                                                #('donchianchannelbreakout', 'Breakout con el Canal de Donchian'),
                                                                                #('timeseriesmomentum', "Momentum de Series Temporales"),
                                                                                #('meanreversionrsi', "Mean Reversion con RSI"),
                                                                                #('pairstrading', 'Trading de Pares')])

    #BuyShortMaxMin Strategy
    time_frame = SelectField(u'Marco Temporal', choices=[(5, '5 días'),
                                                        (10, '10 días'),
                                                        (15, '15 días'),
                                                        (30, '1 mes'),
                                                        (90, '3 meses'),
                                                        (180, '6 meses'),
                                                        (360, '1 año')])

    exit_trade = SelectField(u'Salida', choices=[('exit_time', 'Salida Temporal'),
                                                 ('trailing_stop', 'Salida con Trailing Stop')])

    exit_time_frame = SelectField(u'Stop Temporal', choices=[(1, 'La mitad de los días del Marco Temporal'),
                                                             (2, 'El mismo número de días que el Marco Temporal'),
                                                             (3, 'El mismo número de días más la mitad que el Marco Temporal')])
    atr_multiplier = SelectField(u'Multiplicador ATR', choices=[(1, '1'),
                                                                (2, '2'),
                                                                (3, '3')])



class AssetBacktestingForm(BacktestingForm):
    #asset = StringField(u'Activo', validators=[InputRequired(), asset()])
    name = StringField(u'Nombre', validators=[InputRequired()])
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), min_starting_capital()])
    currency = SelectField(u'Moneda', validators=[InputRequired()], choices=[("USD", "USD"),
                                                                             ("EUR", "EUR"),
                                                                             ("GBP", "GBP"),
                                                                             ("CHF", "CHF"),
                                                                             ("JPY", "JPY"),
                                                                             ("AUD", "AUD")])
                                                                             

class AssetForm(FlaskForm):
    asset = StringField(u'Activo', validators=[InputRequired(), asset()])

#No debería hereder de BacktestingForm, porque solo se debe poder escoger una estrategia
class OptimizationBacktestingForm(FlaskForm):
    #assets = FieldList(FormField(AssetForm), min_entries=2, max_entries=2)
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), min_starting_capital()])
    currency = SelectField(u'Moneda', validators=[InputRequired()], choices=[("USD", "USD"),
                                                                             ("EUR", "EUR"),
                                                                             ("GBP", "GBP"),
                                                                             ("CHF", "CHF"),
                                                                             ("JPY", "JPY"),
                                                                             ("AUD", "AUD")])    
    allAssets = BooleanField(u'Todos los activos')
    #return_portfolio = IntegerField(u'Rendimiento Esperado', validators=[InputRequired(), NumberRange(min=1)])


class BacktestingViewForm(FlaskForm):
    backtesting_id = HiddenField()


class BacktestingGroupsForm(BacktestingForm):
    metric = SelectField(u'Métrica', choices=[('marketCap', 'Capitalización del Mercado'),
                                               ('averageDailyVolume10Day', 'Volumen')])
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), min_starting_capital()])
    currency = SelectField(u'Moneda', validators=[InputRequired()], choices=[("USD", "USD"),
                                                                             ("EUR", "EUR"),
                                                                             ("GBP", "GBP"),
                                                                             ("CHF", "CHF"),
                                                                             ("JPY", "JPY"),
                                                                             ("AUD", "AUD")])