from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, IntegerField, FieldList, FormField, HiddenField
from wtforms.validators import ValidationError, InputRequired, NumberRange
from.stock import Stock
from .futures import Futures

def asset(message=None):
    message = 'No existe el ticker introducido.' 

    def _asset(form, field):
        if (not Futures.get_futures_by_ticker(field.data)) and (not Stock.get_stock_by_ticker(field.data)):
            raise ValidationError(message)

    return _asset


class BacktestingForm(FlaskForm):
    time_frame = SelectField(u'Marco Temporal', validators=[InputRequired()], choices=[(5, '5 días'),
                                                        (10, '10 días'),
                                                        (15, '15 días'),
                                                        (30, '1 mes'),
                                                        (90, '3 meses'),
                                                        (180, '6 meses'),
                                                        (360, '1 año')])

    buymax = BooleanField(u'Comprar Máximos')
    shortmax = BooleanField(u'Vender Máximos')
    buymin = BooleanField(u'Comprar Mínimos')
    shortmin = BooleanField(u'Vender Mínimos')

    exit_trade = SelectField(u'Salida', validators=[InputRequired()], choices=[('exit_time', 'Salida Temporal'),
                                                ('trailing_stop', 'Salida con Trailing Stop')])
    exit_time_frame = SelectField(u'Stop Temporal', choices=[(1, 'La mitad de los días del Marco Temporal'),
                                                            (2, 'El mismo número de días que el Marco Temporal'),
                                                            (3, 'El mismo número de días más la mitad que el Marco Temporal')])
    atr_multiplier = SelectField(u'Multiplicador ATR', choices=[(1, '1'),
                                                                (2, '2'),
                                                                (3, '3')])


class AssetBacktestingForm(BacktestingForm):
    asset = StringField(u'Activo', validators=[InputRequired(), asset()])
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), NumberRange(min=1000)])
    currency = StringField(u'Moneda', validators=[InputRequired()])

class PortfolioBacktestingForm(BacktestingForm):
    assets = FieldList(StringField(u'Activo', min_entries=2, max_entries=None))
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), NumberRange(min=1000)])
    currency = StringField(u'Moneda', validators=[InputRequired()])

class AssetForm(FlaskForm):
    asset = StringField(u'Activo', validators=[InputRequired(), asset()])

#No debería hereder de BacktestingForm, porque solo se debe poder escoger una estrategia
class OptimizationBacktestingForm(FlaskForm):
    #assets = FieldList(FormField(AssetForm), min_entries=2, max_entries=2)
    starting_capital = IntegerField(u'Capital', validators=[InputRequired(), NumberRange(min=1000)])
    currency = StringField(u'Moneda', validators=[InputRequired()])
    return_portfolio = IntegerField(u'Rendimiento Esperado', validators=[InputRequired(), NumberRange(min=1)])


class BacktestingViewForm(FlaskForm):
    backtesting_id = HiddenField()