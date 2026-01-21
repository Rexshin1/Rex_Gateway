from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    # Field Username (Wajib ada biar bisa login pake username nanti)
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    
    # Field Email (Wajib format email)
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Field Password
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
    # Field Konfirmasi Password (biar gak typo)
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Sign Up')