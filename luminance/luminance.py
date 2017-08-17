import json
import os
from flask import Flask
from .database import db, db_session
from .auth import login_manager
from .routes import pages
from .events import events

def create_app(config_filename):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_pyfile(config_filename)
    db.init_app(app)
    login_manager.init_app(app)

    with open(os.getcwd() + '/secrets.json') as data_file:
        app.secret_key = json.load(data_file)['secret_key']

    return app

app = create_app('config.py')
app.register_blueprint(pages)
app.register_blueprint(events, url_prefix='/events')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

import luminance.routes


