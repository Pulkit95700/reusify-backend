from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.product_model import Product
from api.models.cart_model import Cart
from api.middlewares.auth_middleware import protected

cart_ns = Namespace('cart', description='Cart related operations')


@cart_ns.route('/add-to-cart')
class AddToCart(Resource):
    @protected
    def post(user, self):
        """Add product to cart"""
        
        userId = str(user.get('_id'))

        data = request.get_json()
        productId = data.get('product_id')
        quantity = data.get('quantity')

        if not productId or not quantity:
            return ApiError(400, 'Missing product_id or quantity'), 400
        
        if quantity is str and not quantity.strip():
            return ApiError(400, 'Invalid quantity'), 400
        
        quantity = int(quantity)
        if quantity < 1:
            return ApiError(400, 'Quantity must be greater than 0'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            product = db.products.find_one({'_id': ObjectId(productId)})
            if not product:
                return ApiError(404, 'Product not found'), 404
            
            cart = db.carts.find_one({'user_id': userId})
            if not cart:
                new_cart = Cart(userId, productId, quantity)
                created_cart = db.carts.insert_one(new_cart.to_dict())
            else:
                db.carts.update_one(
                    {'user_id': userId},
                    {'$push': {'products': {'product_id': productId, 'quantity': quantity}}}
                )

            return ApiResponse(201, 'Product added to cart successfully'), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        
@cart_ns.route('/get-cart')
class GetCart(Resource):
    @protected
    def get(user, self):
        """Get cart details"""
        
        userId = str(user.get('_id'))
        
        try:
            db = DB.get_db()
            cart = db.carts.find_one({'user_id': userId})
            if not cart:
                return ApiResponse(200, 'Cart details', {'cart': None}), 200
            
            cart['id'] = str(cart['_id'])
            cart.pop('_id')
            cart.pop('user_id')
            cart.pop('created_at')
            cart['products'] = list(cart['products'])
            for product in cart['products']:
                product_id = product['product_id']
                product_details = db.products.find_one({'_id': ObjectId(product_id)})
                product_details.pop('_id')
                product_details.pop('created_at')
                product_details.pop('company_id')
                product_details.pop('categories')
                product['product'] = product_details
            
            return ApiResponse(200, 'Cart details', {'cart': cart}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

@cart_ns.route('/remove-from-cart')
class RemoveFromCart(Resource):
    @protected
    def post(user, self):
        """Remove product from cart"""
        
        userId = str(user.get('_id'))

        data = request.get_json()
        productId = data.get('product_id')

        if not productId:
            return ApiError(400, 'Missing product_id'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            cart = db.carts.find_one({'user_id': userId})
            if not cart:
                return ApiError(404, 'Cart not found'), 404
            
            db.carts.update_one(
                {'user_id': userId},
                {'$pull': {'products': {'product_id': productId}}}
            )

            return ApiResponse(200, 'Product removed from cart successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

@cart_ns.route('/clear-cart')
class ClearCart(Resource):
    @protected
    def delete(user, self):
        """Clear cart"""
        
        userId = str(user.get('_id'))
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            cart = db.carts.find_one({'user_id': userId})
            if not cart:
                return ApiError(404, 'Cart not found'), 404
            
            db.carts.delete_one({'user_id': userId})

            return ApiResponse(200, 'Cart cleared successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
