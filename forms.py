from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


#Form for account registration
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                        validators=[DataRequired(), Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    firstname = StringField('First name',
                        validators=[DataRequired(), Length(min=5, max=20)])
    lastname = StringField('Last name',
                        validators=[DataRequired(), Length(min=5, max=30)])                          
    submit = SubmitField('Sign Up')


#Submit form for adding to watchlist
class MovieSubmit(FlaskForm):
    submit = SubmitField('Add to watchlist')


#Submit form for deleting a movie from the watchlist
class MovieDelete(FlaskForm):
    submit = SubmitField('Delete from watchlist')


#Submit forms for deleting an account and clearing a users watchlist
class ProfileForm(FlaskForm):
    submit = SubmitField('Delete Account')
    submit2 = SubmitField('Clear Watchlist')


#Login form
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                        validators=[DataRequired(), Length(min=5, max=20)])
    submit = SubmitField('Log In')


#Form for confirming user email before sending a link to reset password
class EmailConfirm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    confirm_email = StringField('Confirm Email',
                        validators=[DataRequired(), Email(), EqualTo('email')])
    submit = SubmitField('Submit')


#Form for resetting a user password. Only accessable via email link
class PasswordReset(FlaskForm):
    password = PasswordField('Password', 
                        validators=[DataRequired(),Length(min=5, max=20)])
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')


#Form for changing password when logged in.
class PasswordChange(FlaskForm):
    old_password = PasswordField('Old Password', 
                        validators=[DataRequired(), Length(min=5, max=20)])
    new_password = PasswordField('New Password', 
                        validators=[DataRequired(), Length(min=5, max=20),])
    confirm_password = PasswordField('Confirm Password',
                        validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')
