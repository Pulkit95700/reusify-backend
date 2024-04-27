# here we are going to use namespace for our blueprints.
# blueprints helps our project to split into various modules so that we can separate our code
import datetime
from flask.views import MethodView
from flask_restx import Namespace, Resource
from flask import request
from api.middlewares.auth_middleware import protected
from api.db import db as DB
from api.helpers.lib import lib
from api.models.user_model import User
from api.config.config import Config
from bson.objectid import ObjectId
import jwt
import os

# here we are going to use namespace for our blueprints.
# namespace is just like router in express js

# here we are going to use namespace for our blueprints. 
auth_ns = Namespace('auth', description='Authentication related operations')

@auth_ns.route('/signup')
class SignUp(Resource):
    
    def post(self):
        """Create a new user"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        if not username or not password or not role:
            return {'message': 'Missing username, password or role'}, 400
        
        if not username.strip() or not password.strip() or not role.strip():
            return {'message': 'Invalid username, password or role'}, 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return {'message': 'Database connection error'}, 500
            
            user = db.users.find_one({'username': username})    
            if user:
                return {'message': 'User already exists'}, 400
            
            bcrypt = lib.get_bcrypt()
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username, password, role)
            created_user = db.users.insert_one(new_user.to_json())
            
            print(created_user)
            accessToken = jwt.encode({
                '_id': str(created_user.inserted_id),
                'role': role,
                'exp': Config.JWT_ACCESS_TOKEN_EXPIRES
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            refreshToken = jwt.encode({
                '_id': str(created_user.inserted_id),
                'role': role,
                'exp': Config.JWT_REFRESH_TOKEN_EXPIRES
            }, Config.JWT_SECRET_KEY, algorithm='HS256')

            return {'message': 'User created successfully', 'accessToken': accessToken, 'refreshToken': refreshToken}, 201
        except Exception as e:
            return {'message': str(e)}, 400


@auth_ns.route('/login')
class Login(Resource):

    def post(self):
        """Generate a JWT pair"""
        data = request.get_json()
        username = str(data.get('username'))
        password = str(data.get('password'))

        if not username or not password:
            return {'message': 'Missing username or password'}, 400
        
        if not username.strip() or not password.strip():
            return {'message': 'Invalid username or password'}, 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return {'message': 'Database connection error'}, 500
            
            user = db.users.find_one({'username': username})

            if not user:
                return {'message': 'User not found'}, 404
            
            
            # check if the password is correct
            bcrypt = lib.get_bcrypt()
            check_password = bcrypt.check_password_hash(user.get('password'), password)
            if not check_password:
                return {'message': 'Invalid username or password'}, 400

            accessToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': user.get('role'),
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            refreshToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': user.get('role'),
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')

            return {'message': 'Login successful', 'accessToken': accessToken, 'refreshToken': refreshToken}, 200
        except Exception as e:
            return {'message': str(e)}, 400
        

@auth_ns.route('/refresh')
class Refresh(Resource):
    
    def post(self):
        """Refresh the JWT pair"""
        data = request.get_json()
        refreshToken = data.get('refreshToken')
        
        if not refreshToken:
            return {'message': 'Missing refreshToken'}, 400
        
        try:
            data = jwt.decode(refreshToken, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            db = DB.get_db()

            if(db is None):
                return {'message': 'Database connection error'}, 500
            
            user = db.users.find_one({
                '_id': ObjectId(data.get('_id'))
            })
            
            if not user:
                return {'message': 'User not found'}, 404
            
            
            accessToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': user.get('role'),
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            return {'message': 'Token refreshed successfully', 'accessToken': accessToken}, 200
        except Exception as e:
            return {'message': str(e)}, 400
        
@auth_ns.route('/protected')
class SampleProtected(Resource):
    @protected  
    def get(user, self):
        return {'message': 'This is a protected route'}, 200