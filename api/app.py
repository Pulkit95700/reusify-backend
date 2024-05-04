from flask import Flask
from flask_restx import Api
from .controllers.auth_controller import auth_ns
from .controllers.company_controller import company_ns
from .controllers.category_controller import category_ns
from .controllers.product_controller import product_ns
from .controllers.cart_controller import cart_ns
from .controllers.user_controller import user_ns 
from .controllers.order_controller import order_ns 
from .config.config import config_dict, Config
from flask_bcrypt import Bcrypt
from api.db import db
from api.helpers.lib import lib

config = config_dict[Config.TYPE]

def create_app(config=config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_db(app)
    bcrypt = Bcrypt(app)
    lib.init_bcrypt(bcrypt)

    api = Api(app)
    api.add_namespace(auth_ns, path='/user/auth')
    api.add_namespace(company_ns, path='/company')
    api.add_namespace(category_ns, path='/category')
    api.add_namespace(product_ns, path='/product')
    api.add_namespace(cart_ns, path='/cart')
    api.add_namespace(user_ns, path='/user')
    api.add_namespace(order_ns, path='/order')
    return app
