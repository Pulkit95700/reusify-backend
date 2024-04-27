from flask import Flask
from flask_restx import Api
from .controllers.auth_controller import auth_ns
from .config.config import config_dict

def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    api = Api(app)
    api.add_namespace(auth_ns, path='/auth/')

    return app

