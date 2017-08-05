import json
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .database import db_session

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

import luminance.routes

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

with open(os.getcwd() + '/secrets.json') as data_file:
    print(os.getcwd())
    app.secret_key = json.load(data_file)['secret_key']

