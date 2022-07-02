from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, DateField, SubmitField
from wtforms.validators import ValidationError, InputRequired, NumberRange, Optional
from datetime import datetime



class BacktestingManualForm(FlaskForm):
    starting_cash = IntegerField(u'Capital', validators=[InputRequired(), NumberRange(min=1000)])
    currency = SelectField(u'Moneda', validators=[InputRequired()], choices=[("USD", "USD"),
                                                                             ("EUR", "EUR"),
                                                                             ("GBP", "GBP"),
                                                                             ("CHF", "CHF"),
                                                                             ("JPY", "JPY"),
                                                                             ("AUD", "AUD")])    

class BacktestingManualFormProfit(FlaskForm):
    profit = IntegerField(u'Ganancia', validators=[InputRequired(), NumberRange(min=0)])
    date = DateField(u'Fecha', default=datetime.today, validators=[InputRequired()], format="%Y-%m-%d")
    add_profit = SubmitField(u'Añadir Beneficio')
    backtesting_id = HiddenField()

class BacktestingManualFormLoss(FlaskForm):
    loss =IntegerField(u'Pérdida', validators=[InputRequired(), NumberRange(min=0)])
    date = DateField(u'Fecha', default=datetime.today, validators=[InputRequired()], format="%Y-%m-%d")
    add_loss = SubmitField(u'Añadir Pérdida')
    backtesting_id = HiddenField()

