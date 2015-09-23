'''
Created on 23 Sep 2015

@author: si
'''

from flask import Flask, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from models import Foo


def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)
    
    db.init_app(app)
    cors = CORS(app)

    from views import api_views
    app.register_blueprint(api_views)

    return app