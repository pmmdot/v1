from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField , BooleanField
from wtforms.validators import DataRequired, Email, EqualTo ,Length

class Reg_form(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = EmailField('Email', validators=[DataRequired(message='Yo!! chill!'), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=35)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class Login_form(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=35)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')