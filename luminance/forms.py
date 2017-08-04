from wtforms import (
    Form, 
    StringField, 
    PasswordField, 
    SubmitField,
    DateTimeField,
    validators
)

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
    start_date = DateTimeField('start_date', format="%Y-%m-%dT%H:%M")
    end_date = DateTimeField('end_date', format="%Y-%m-%dT%H:%M")
    submit = SubmitField('create')