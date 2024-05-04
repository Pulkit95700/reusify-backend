import json
from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.orders_model import Order
from api.middlewares.auth_middleware import protected

order_ns = Namespace('order', description='Order related operations')

@order_ns.route('/create-order')
class OrderController(Resource):
    @protected
    def post(user,  self):
        # """Create a new order"""
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        price = data.get('price')

        if not product_id or not quantity or not price:
            return ApiError(400, 'Missing required fields'), 400
        
        try:
            new_order = Order(product_id, quantity, price , str(user['_id']))
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            created_order = db.orders.insert_one(new_order.to_dict())

            return ApiResponse(201, 'Order created successfully', {'order_id': str(created_order.inserted_id)}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        

@order_ns.route('/<string:order_id>')
class OrderDetails(Resource):
    @protected
    def get(user, self, order_id):
        # """Get order details"""
        try:
            order_id = str(order_id)
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            order = db.orders.find_one({'_id': ObjectId(order_id)})
            if not order:
                return ApiError(404, 'Order not found'), 404

            order.pop('_id')

            print(order)
            return ApiResponse(200, 'Order details', {'order': order}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    def put(self, order_id):
        # """Update order details"""
        data = request.get_json()
        # Update the order details here
        pass

@order_ns.route('/all-orders')
class Orders(Resource):
    def get(self):
        try:
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            orders = db.orders.find()

            orders_list = []
            for order in orders:
                try:
                    order['_id'] = str(order['_id'])  # Convert ObjectId to string
                    
                    orders_list.append(order)
                except Exception as e:
                    print(f"Error converting ObjectId to string for order: {order}")
                    print(f"Error: {e}")

            return ApiResponse(200, 'Orders', {'orders': orders_list}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

# You can add more routes as needed, such as delete, search, etc.
