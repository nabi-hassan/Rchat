from models import Users

from passlib.hash import pbkdf2_sha256

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, length, Email, EqualTo, ValidationError

def Validating_Credentials(form, field):
    """ Validating entered credentials for the User """
    
    username = form.username.data
    password = field.data

    user_obj = Users.query.filter_by(username = username).first()

    if user_obj is None:
        raise ValidationError('Username or Password is incorrect')
    elif not pbkdf2_sha256.verify(password, user_obj.password):
        raise ValidationError('Username or Password is incorrect')


class RegistrationForm(FlaskForm):
    """ Registration Page for new User """

    username = StringField('Username', validators=[DataRequired(), 
    length(min = 4, max = 25, message = 'Username must be between 4 to 25 characters')])
    
    #email = StringField('Email', validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired(), 
    length(min = 4, max = 25, message = 'Password must be between 4 to 25 characters')])

    confirm_pswd = PasswordField('Confirm Password', 
    validators=[EqualTo('password', message = 'Passwords must match!!')])

    submit = SubmitField('Sign Up')

    def validate_username(self,username):

        #For checking whether username is taken or not
        user_obj = Users.query.filter_by(username = username.data).first()

        if user_obj:
            raise ValidationError('User name already exists. Select a different username.')


class LoginForm(FlaskForm):
    """ Login Page for the Registered User """

    username = StringField('Username', validators = [DataRequired(message='Username required')])
    password = PasswordField('Password', validators = [DataRequired(message='Password required'), Validating_Credentials])
    submit = SubmitField('Login')











