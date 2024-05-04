from functools import wraps
import jwt
from flask import request, abort    
from api.db import db
from bson.objectid import ObjectId
from api.config.config import Config
from api.helpers.ApiError import ApiError

def protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            accessToken = request.headers.get('Authorization')
            if not accessToken:
                return ApiError(401, 'Access token is missing'), 401
            accessToken = accessToken.split(' ')[1]
            payload = jwt.decode(accessToken, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            user = db.get_db().users.find_one({'_id': ObjectId(payload['_id'])})

            role = payload.get('role')
            if not user:
                return ApiError(404, 'User not found'), 404
            if not role:
                return ApiError(401, 'Role not found'), 401
            
            user['role'] = role
            return f(user, *args, **kwargs)
        except Exception as e:
            return ApiError(401, str(e)), 401
    return decorated_function