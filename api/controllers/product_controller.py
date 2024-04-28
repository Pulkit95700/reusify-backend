from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.product_model import Product

product_ns = Namespace('product', description='Product related operations')

@product_ns.route('/create-product')
class ProductController(Resource):
    def post(self):
        """Create a new product"""
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        company_id = data.get('company_id')
        price = data.get('price')
        imageUrls = data.get('imageUrls')
        categories = data.get('categories')

        if not name or not description or not price or not categories or not company_id:
            return ApiError(400, 'Missing name, description, price, company_id or categories'), 400
        
        if not name.strip() or not description.strip() or not company_id.strip():
            return ApiError(400, 'Invalid name, description, price or company'), 400
        
        # categories should be an array
        if categories and not isinstance(categories, list):
            return ApiError(400, 'Invalid categories'), 400
        
        if(categories and len(categories) < 1):
            return ApiError(400, 'At least one category is required'), 400
        
        # categories should be an array of strings
        if categories and not all(isinstance(category, str) for category in categories):
            return ApiError(400, 'Invalid categories'), 400
        
        # imageUrls should be an array
        if imageUrls and not isinstance(imageUrls, list):
            return ApiError(400, 'Invalid imageUrls'), 400
        
        # imageUrls should be an array of strings
        if imageUrls and not all(isinstance(imageUrl, str) for imageUrl in imageUrls):
            return ApiError(400, 'Invalid imageUrls'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            # check if company exists
            company = db.companies.find_one({'_id': ObjectId(company_id)})

            if not company:
                return ApiError(404, 'Company not found'), 404
            
            product = db.products.find_one({'name': name})
            if product:
                return ApiError(400, 'Product already exists'), 400
            
            new_product = Product(name, price, description, company_id, categories, imageUrls)
            created_product = db.products.insert_one(new_product.to_dict())

            return ApiResponse(201, 'Product created successfully', {'product_id': str(created_product.inserted_id)}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        

@product_ns.route('/<string:product_id>')
class ProductDetails(Resource):
    def get(self, product_id):
        """Get product details"""
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500

            product = db.products.find_one({'_id': ObjectId(product_id)})
            if not product:
                return ApiError(404, 'Product not found'), 404
            
            product['id'] = str(product['_id'])
            product.pop('_id')

            # get company details
            company = db.companies.find_one({'_id': ObjectId(product['company_id'])})
            print(company)
            company['id'] = str(company['_id'])
            company.pop('_id')
            product['company'] = company

            # get categories details
            categories = db.categories.find({'_id': {'$in': [ObjectId(category_id) for category_id in product['categories']]}})
     
            product['categories'] = [{'id': str(category['_id']), 'category_name': category['category_name'], 'imageUrl': category['imageUrl']} for category in categories]

            return ApiResponse(200, 'Product details', {'product': product}), 200
        except Exception as e:
            print(e)
            return ApiError(400, str(e)), 400
    
    def put(self, product_id):
        """Update product details"""
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        company_id = data.get('company_id')
        price = data.get('price')
        imageUrls = data.get('imageUrls')
        categories = data.get('categories')

        if not name or not description or not price or not categories or not company_id:
            return ApiError(400, 'Missing name, description, price, company_id or categories'), 400
        
        if not name.strip() or not description.strip() or not company_id.strip():
            return ApiError(400, 'Invalid name, description, price or company'), 400
        
        # categories should be an array
        if categories and not isinstance(categories, list):
            return ApiError(400, 'Invalid categories'), 400
        
        if(categories and len(categories) < 1):
            return ApiError(400, 'At least one category is required'), 400
        
        # categories should be an array of strings
        if categories and not all(isinstance(category, str) for category in categories):
            return ApiError(400, 'Invalid categories'), 400
        
        # imageUrls should be an array
        if imageUrls and not isinstance(imageUrls, list):
            return ApiError(400, 'Invalid imageUrls'), 400
        
        # imageUrls should be an array of strings
        if imageUrls and not all(isinstance(imageUrl, str) for imageUrl in imageUrls):
            return ApiError(400, 'Invalid imageUrls'), 400
        
        try:
            db = DB.get_db()

            product = db.products.find_one({'_id': ObjectId(product_id)})
            if not product:
                return ApiError(404, 'Product not found'), 404
            
            db.products.update_one({'_id': ObjectId(product_id)}, {'$set': {'name': name, 'price': price, 'description': description, 'company_id': company_id, 'categories': categories, 'imageUrls': imageUrls}})
            return ApiResponse(200, 'Product updated successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
        