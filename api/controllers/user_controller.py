from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.middlewares.auth_middleware import protected
from api.models.wishlist_model import WishListItem

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
        limit = request.args.get('limit') or 10
        offset = request.args.get('offset') or 0
        try:
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500
            
            wishlistitems = db.wishlistitems.find({'user_id': userId}).skip(offset).limit(offset)

            if not wishlistitems:
                return ApiResponse(200, 'Wishlist is empty', {'wishlist': None}), 200
            
            products = []
            for item in wishlistitems:
                product = db.products.find_one({'_id': ObjectId(item.get('product_id'))})
                product['id'] = str(product.get('_id'))
                product.pop('_id')
                product.pop('created_at')
                # fetch comaapny details
                company = db.companies.find_one({'_id': ObjectId(product.get('company_id'))})
                company = {
                    'id': str(company.get('_id')),
                    'name': company.get('name'),
                    'imageUrl': company.get('imageUrl') or ''
                }

                product['company'] = company
                product.pop('company_id')
                # fetch category details
                categories = []
                for category_id in product['categories']:
                    category = db.categories.find_one({'_id': ObjectId(category_id)})
                    category['id'] = str(category.get('_id'))
                    category.pop('_id')
                    category.pop('created_at')
                    category.pop('description')
                    categories.append(category)
                product.pop('categories')
                product['categories'] = list(categories)
                products.append(product)

            return ApiResponse(200, 'Wishlist items', {'wishlist': products}), 200
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
            
            # check if product already exists in wishlist
            wishlistitem = db.wishlistitems.find_one({
                'user_id': userId,
                'product_id': productId
            })

            if wishlistitem:
                return ApiError(201, 'Product added to wishlist'), 201
            
            wishlistitem = WishListItem(userId, productId)
            db.wishlistitems.insert_one(wishlistitem.to_dict())

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
            
            wishlistitem = db.wishlistitems.find_one({
                'user_id': userId,
                'product_id': productId
            })

            if not wishlistitem:
                return ApiResponse(200, 'Product not found in wishlist', {'wishlist': None}), 200
            db.wishlistitems.delete_one({
                'user_id': userId,
                'product_id': productId
            })

            return ApiResponse(200, 'Product removed from wishlist successfully'), 200

        except Exception as e:
            return ApiError(400, str(e)), 400