from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.middlewares.auth_middleware import protected
from api.models.wishlist_model import WishList

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

@user_ns.route('/wishlist')
class Wishlist(Resource):
    @protected
    def get(user, self):
        """Get user wishlist"""
        
        userId = str(user.get('_id'))

        try:
            db = DB.get_db()
            wishlist = db.wishlists.find_one({'user_id': userId})
            if not wishlist:
                return ApiResponse(200, 'Wishlist details', {'wishlist': None}), 200
            
            wishlist['id'] = str(wishlist['_id'])
            wishlist.pop('_id')
            wishlist.pop('user_id')
            wishlist['products'] = list(wishlist['products'])
            for product in wishlist['products']:
                product_id = product['product_id']
                product_details = db.products.find_one({'_id': ObjectId(product_id)})
                product_details.pop('_id')
                product_details.pop('created_at')
                product_details.pop('company_id')
                product_details.pop('categories')
                product['product'] = product_details
            
            return ApiResponse(200, 'Wishlist details', {'wishlist': wishlist}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    @protected
    def post(user, self):
        """Add product to wishlist"""

        userId = str(user.get('_id'))

        data = request.get_json()
        productId = data.get('product_id')

        if not productId:
            return ApiError(400, 'Missing product_id'), 400

        try:
            db = DB.get_db()

            product = db.products.find_one({'_id': ObjectId(productId)})
            if not product:
                return ApiError(404, 'Product not found'), 404
            
            wishlist = db.wishlists.find_one({'user_id': userId})
            if not wishlist:
                new_wishlist = WishList(userId, productId)
                created_wishlist = db.wishlists.insert_one(new_wishlist.to_dict())
            else:
                # Check if product already exists in wishlist
                product_exists = False
                for product in wishlist['products']:
                    if product['product_id'] == productId:
                        product_exists = True
                        break
                
                if not product_exists:
                    db.wishlists.update_one(
                        {'user_id': userId},
                        {'$push': {'products': {'product_id': productId}}}
                    )

            return ApiResponse(201, 'Product added to wishlist successfully'), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    @protected
    def delete(user, self):
        """Remove product from wishlist"""
        
        userId = str(user.get('_id'))

        data = request.get_json()
        productId = data.get('product_id')

        if not productId:
            return ApiError(400, 'Missing product_id'), 400

        try:
            db = DB.get_db()

            product = db.products.find_one({'_id': ObjectId(productId)})
            if not product:
                return ApiError(404, 'Product not found'), 404
            
            wishlist = db.wishlists.find_one({'user_id': userId})
            if not wishlist:
                return ApiError(404, 'Wishlist not found'), 404
            
            product_exists = False
            for product in wishlist['products']:
                if product['product_id'] == productId:
                    product_exists = True
                    break
                
            if product_exists:
                db.wishlists.update_one(
                    {'user_id': userId},
                    {'$pull': {'products': {'product_id': productId}}}
                )

            return ApiResponse(200, 'Product removed from wishlist successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400