from wtforms import Form, StringField, validators

class RegistrationForm(Form):
    username = StringField('username', [validators.Length(min=1, max=25)])
    password = StringField('password', [validators.Length(min=6, max=512)])

class LoginForm(Form):
    username = StringField('username', [validators.Length(min=1, max=25)])
    password = StringField('password', [validators.Length(min=6, max=512)])