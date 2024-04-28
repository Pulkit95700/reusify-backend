# here we are going to use namespace for our blueprints.
# blueprints helps our project to split into various modules so that we can separate our code
import datetime
from flask_restx import Namespace, Resource
from flask import request
from api.middlewares.auth_middleware import protected
from api.db import db as DB
from api.helpers.lib import lib
from api.models.user_model import User
from api.config.config import Config
from bson.objectid import ObjectId
from api.constants import BUYER_ROLE
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
import jwt

# here we are going to use namespace for our blueprints.
# namespace is just like router in express js

# here we are going to use namespace for our blueprints. 
auth_ns = Namespace('auth', description='Authentication related operations')

@auth_ns.route('/signup')
class SignUp(Resource):
    
    def post(self):
        """Create a new user"""
        data = request.get_json()
        full_name = data.get('full_name')
        password = data.get('password')
        email = data.get('email')
        fcm_token = data.get('fcm_token') or None

        if not full_name or not password or not email:
            return ApiError(400, 'Missing full_name, email or password'), 400
        
        if not password.strip() or not email.strip():
            return ApiError(400, 'Invalid email or password'), 400

        if(len(password) < 6):
            return ApiError(400, 'Password must be at least 6 characters'), 400
        
        if(email.find('@') == -1 or email.find('.') == -1):
            return ApiError(400, 'Invalid Email'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            user = db.users.find_one({'email': email})    
            if user:
                return ApiError(400, 'User already exists'), 400
            
            bcrypt = lib.get_bcrypt()
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(full_name, password, email, fcm_token)
            created_user = db.users.insert_one(new_user.to_json())
            
            accessToken = jwt.encode({
                '_id': str(created_user.inserted_id),
                'role': BUYER_ROLE,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            refreshToken = jwt.encode({
                '_id': str(created_user.inserted_id),
                'role': BUYER_ROLE,
                'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')

            user = db.users.find_one({'_id': ObjectId(created_user.inserted_id)})
            user['id'] = str(user.get('_id'))
            user.pop('password')
            user.pop('_id')
            return ApiResponse(201, 'User created successfully', {'accessToken': accessToken, 'refreshToken': refreshToken, 'user': user}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400


@auth_ns.route('/login')
class Login(Resource):

    def post(self):
        """Generate a JWT pair"""
        data = request.get_json()
        email = str(data.get('email'))
        password = str(data.get('password'))
        fcm_token = str(data.get('fcm_token')) or ''

        if not email or not password:
            return ApiError(400, 'Missing username or password'), 400
        
        if not email.strip() or not password.strip():
            return ApiError(400, 'Invalid username or password'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database connection error'), 500
            
            user = db.users.find_one({'email': email})

            if not user:
                return ApiError(404, 'User not found'), 404
            
            # check if the password is correct
            bcrypt = lib.get_bcrypt()
            check_password = bcrypt.check_password_hash(user.get('password'), password)
            if not check_password:
                return ApiError(400, 'Invalid username or password'), 400
            
            # update the fcm token
            if fcm_token != '':
                db.users.update_one({'_id': user.get('_id')}, {'$set': {'fcm_token': fcm_token}})
            
            
            user['fcm_token'] = fcm_token
            user['id'] = str(user.get('_id'))
            

            accessToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': BUYER_ROLE,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            refreshToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': BUYER_ROLE,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')


            user.pop('password')
            user.pop('_id')
            
            return ApiResponse(200, 'Login successful', {'accessToken': accessToken, 'refreshToken': refreshToken, 'user': user}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
        

@auth_ns.route('/refresh')
class Refresh(Resource):
    
    def post(self):
        """Refresh the JWT pair"""
        data = request.get_json()
        refreshToken = data.get('refreshToken')
        
        if not refreshToken:
            return ApiError(400, 'Missing refreshToken'), 400
        
        try:
            data = jwt.decode(refreshToken, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database connection error'), 500
            
            user = db.users.find_one({
                '_id': ObjectId(data.get('_id'))
            })
            
            if not user:
                return ApiError(404, 'User not found'), 404
            
            accessToken = jwt.encode({
                '_id': str(user.get('_id')),
                'role': BUYER_ROLE,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            return ApiResponse(200, 'Token refreshed successfully', {'accessToken': accessToken}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

@auth_ns.route('/verify-user')
class VerifyUser(Resource):
    @protected
    def get(user, self):
        user['id'] = str(user.get('_id'))
        user.pop('password')
        user.pop('_id')
        return ApiResponse(200, 'User Verified Successfully', {'user': user}), 200        
