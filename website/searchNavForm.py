from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, IntegerField, FieldList, FormField, HiddenField, DateField
from wtforms.validators import ValidationError, InputRequired, NumberRange, Optional
from.stock import Stock
from .futures import Futures

class SearchNavForm(FlaskForm):
    query = StringField(u'Buscar', validators=[InputRequired()])
    category = SelectField(u'Categoría', validators=[InputRequired()], choices=[('Backtesting', 'Backtesting'),
                                                                                ('Portfolio', 'Cartera'),
                                                                                ('User', 'Usuario')])