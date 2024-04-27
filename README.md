I am writing everything and every knowledge from scratch here. That I have learned for building this project from scratch.

# Initializing the API

1. To start a project, it is always recommend to use virtual environment in Python. If you do not know what is virtual environment, its a space (environment) inside your computer that is assigned to your own project. Virtual environments are used because python is not good at managing dependencies. A virtual environment makes sure that your project dependencies remain in your project only without effecting global python dependencies which could effect other projects.

To create a venv i refer following this article. Make sure to activate it before working in project.
https://realpython.com/python-virtual-environments-a-primer/

2. After making a virtual environment now make an api folder. I am following a services based directory structure. Although you can make your own directory structure if you like.

3. Install flask dependency using "pip install flask" command

4. After installing dependency, create a requirements.txt file in your root folder. It keeps track of all the dependecies with their versions. To make it write "pip freeze >requirements.txt" command. In future make sure to always update requirements.txt after installing any dependency.

5. Now inside your api file create __init__.py file. Write your create_app script over there.

****************************************************
from flask import Flask

def create_app():
    app = Flask(__name__)

    return app
****************************************************

# Understanding the starters.

1. Now, we will make an pizza ordering api in flask. To make the api we need to install flask-restx package. So install it using flask-restx. Update the requirements.txt from the same command.

2. Now we will use blueprints to make our api more modular. Blueprints in python are used to separate our logics in api. It is just like router in express.js 😉. 

3. Make auth folder and orders folder and also make their __init__.py files inside the app folder.

4. Its time to create views inside each service. Make an file named views.py inside the orders and auth folder. Now write the code for making a blueprint and use it inside the http methods.

***************************************************

// blueprints helps our project to split into various modules so that we can separate our code

from flask_restx import Namespace, Resource

here we are going to use namespace for our blueprints.
namespace is just like router in express js

// here we are going to use namespace for our blueprints. 
auth_ns = Namespace('auth', description='Authentication related operations')


@auth_ns.route('/')
class HelloAuth(Resource):
    def get(self):
        return {'hello': 'world'}

***************************************************

5. Do same for orders page. Now we need to use it inside our main application so import these inside the __init__.py file in the app folder.

**************************************************************

from flask import Flask
from flask_restx import Api
from .orders.views import orders_ns
from .auth.views import auth_ns

def create_app():
    app = Flask(__name__)

    api = Api(app)
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(orders_ns, path='/orders')

    return app

**************************************************************

6. YES and by the way to run it you have to first make sure that your api works correctly. You have to use "set FLASK_APP=api/" command in your cmd. This will tell the flask to run the __init__.py file in api folder.

7. Now run the server through "flask run" command.

8. You can see the url of the localhost. Click on the link to run your simple API.

# Moving to more 

now we need to setup env configurations, production, development and testing environments and more.

1. Make a config folder. Make __init__.py file and config.py file