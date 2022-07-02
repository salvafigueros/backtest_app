from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms.validators import ValidationError, InputRequired, NumberRange, Optional, EqualTo


class UserForm(FlaskForm):
    user_id = HiddenField()
    user_name = StringField(u'Nombre de Usuario', validators=[])
    user_full_name = StringField(u'Nombre Completo', validators=[])


class UserSecurityForm(FlaskForm):
    user_id = HiddenField()
    password = PasswordField(u'Contraseña', validators=[InputRequired()])



