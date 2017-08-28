from wtforms import (
    Form, 
    StringField, 
    PasswordField, 
    SubmitField,
    DateTimeField,
    HiddenField,
    validators
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

class RegistrationForm(Form):
    username = StringField('username', [validators.Length(min=1, max=25)])
    password = PasswordField('password', [validators.Length(min=6, max=512)])
    submit = SubmitField('signup')

class LoginForm(Form):
    username = StringField('username', [validators.Length(min=1, max=25)])
    password = PasswordField('password', [validators.Length(min=6, max=512)])
    submit = SubmitField('login')

class ContestForm(Form):
    name = StringField('name', [validators.Length(min=1, max=1024)])
    start_date = DateTimeField('start_date', format="%Y-%m-%dT%H:%M", validators=[validators.Optional()])
    end_date = DateTimeField('end_date', format="%Y-%m-%dT%H:%M", validators=[validators.Optional()])
    submit = SubmitField('create')

class AddUserToEventForm(Form):
    event_id = HiddenField('event_id')
    submit = SubmitField('register')

class PhotoForm(Form):
    photo = FileField(validators=[FileRequired()])
    submit = SubmitField('upload photo')

class ProfileForm(Form):
    bio = StringField('bio', [validators.Length(max=19000)])
    save = SubmitField('save')

class ChosenEventForm(Form):
    photo_id = HiddenField('photo_id')
    submit = SubmitField('choose')