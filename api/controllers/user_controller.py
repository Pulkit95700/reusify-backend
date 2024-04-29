from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.middlewares.auth_middleware import protected


user_ns = Namespace('user', description='User related operations')

@user_ns.route('/edit-profile')
class EditProfile(Resource):
    @protected
    def patch(user, self):
        """Edit user profile"""

        userId = str(user.get('_id'))

        data = request.get_json()
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')
        fcm_token = data.get('fcm_token') or None

        updated_data = {}
        if full_name:
            updated_data['full_name'] = full_name
        
        if email:
            if(email.find('@') == -1 or email.find('.') == -1):
                return ApiError(400, 'Invalid Email'), 400
            updated_data['email'] = email
        
        if phone:
            if(len(phone) < 10):
                return ApiError(400, 'Phone number must be at least 10 characters'), 400
            updated_data['phone'] = phone
        
        if address:
            updated_data['address'] = address
        
        if fcm_token:
            updated_data['fcm_token'] = fcm_token
        
        if not updated_data:
            return ApiError(400, 'Missing full_name, email, phone, address or fcm_token'), 400        

        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            user = db.users.find_one({'email': email})
            if user:
                return ApiError(400, 'User already exists'), 400
            
            db.users.update_one(
                {'_id': ObjectId(userId)},
                {'$set': updated_data}
            )

            return ApiResponse(200, 'Profile updated successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
        
@user_ns.route('/view-profile')
class ViewProfile(Resource):
    @protected
    def get(user, self):
        """View user profile"""

        userId = str(user.get('_id'))
        
        try:
            db = DB.get_db()
            user = db.users.find_one({'_id': ObjectId(userId)})
            if not user:
                return ApiError(404, 'User not found'), 404
            
            user['id'] = str(user['_id'])
            user.pop('password')
            user.pop('_id')
            
            return ApiResponse(200, 'User details', {'user': user}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400