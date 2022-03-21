from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    firstname = StringField('First name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last name',
                           validators=[DataRequired(), Length(min=2, max=30)])                          
    submit = SubmitField('Sign Up')


class MovieSubmit(FlaskForm):
    submit = SubmitField('Add to watchlist')


class MovieDelete(FlaskForm):
    submit = SubmitField('Delete from watchlist')


class ProfileForm(FlaskForm):
    submit = SubmitField('Delete Account')
    submit2 = SubmitField('Clear Watchlist')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class EmailConfirm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email',
                        validators=[DataRequired(), Email(), EqualTo('email')])
    submit = SubmitField('Submit')


class PasswordReset(FlaskForm):
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')


class PasswordChange(FlaskForm):
    old_password = PasswordField('Old Password', 
                            validators=[DataRequired()])
    new_password = PasswordField('New Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')
