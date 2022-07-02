from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, StringField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, DateField
from wtforms.validators import ValidationError, InputRequired, NumberRange
from datetime import datetime


class JournalForm(FlaskForm):
    user_id = HiddenField()
    date = DateField(u'Fecha', default=datetime.today, validators=[InputRequired()], format="%Y-%m-%d")
    journal_text = TextAreaField(u'Texto', validators=[InputRequired()])
    #Añadir un campo para añadir Backtesting/Cartera


class ViewJournalForm(JournalForm):
    journal_id = HiddenField()
    date = HiddenField()
    