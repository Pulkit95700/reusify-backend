from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.orders_model import Order

order_ns = Namespace('order', description='Order related operations')

@order_ns.route('/create-order')
class OrderController(Resource):
    def post(self):
        """Create a new order"""
        data = request.get_json()
        order_id = data.get('order_id')
        product_name = data.get('product_name')
        quantity = data.get('quantity')
        price = data.get('price')
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')

        if not order_id or not product_name or not quantity or not price or not customer_name or not customer_email:
            return ApiError(400, 'Missing required fields'), 400
        
        try:
            new_order = Order(order_id, product_name, quantity, price, customer_name, customer_email)
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            created_order = db.orders.insert_one(new_order.to_dict())

            return ApiResponse(201, 'Order created successfully', {'order_id': str(created_order.inserted_id)}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        

@order_ns.route('/<string:order_id>')
class OrderDetails(Resource):
    def get(self, order_id):
        """Get order details"""
        try:
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            order = db.orders.find_one({'_id': ObjectId(order_id)})
            if not order:
                return ApiError(404, 'Order not found'), 404

            order.pop('_id')

            return ApiResponse(200, 'Order details', {'order': order}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    def put(self, order_id):
        """Update order details"""
        data = request.get_json()
        # Update the order details here
        pass

@order_ns.route('/all-orders')
class Orders(Resource):
    def get(self):
        """Get all orders"""
        try:
            db = DB.get_db()
            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            orders = db.orders.find()

            orders = list(orders)
            for order in orders:
                order.pop('_id')

            return ApiResponse(200, 'Orders', {'orders': orders}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

# You can add more routes as needed, such as delete, search, etc.
