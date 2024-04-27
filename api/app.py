from flask import Flask
from flask_restx import Api
from .controllers.auth_controller import auth_ns
from .config.config import config_dict
from flask_bcrypt import Bcrypt
from api.db import db
from api.helpers.lib import lib

config = config_dict['dev']

def create_app(config=config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_db(app)
    bcrypt = Bcrypt(app)
    lib.init_bcrypt(bcrypt)
    
    api = Api(app)
    api.add_namespace(auth_ns, path='/auth')

    return app
