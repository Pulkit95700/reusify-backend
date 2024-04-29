from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.product_model import Product
from api.helpers.scraper import scrap_data_saahas

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
        mrp = data.get('mrp')
        imageUrls = data.get('imageUrls')
        categories = data.get('categories')

        if not name or not description or not price or not categories or not company_id or not mrp:
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
            
            new_product = Product(name, price, mrp, description, company_id, categories, imageUrls)
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
        mrp = data.get('mrp')
        imageUrls = data.get('imageUrls')
        categories = data.get('categories')

        if not name or not description or not price or not categories or not company_id or not mrp:
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
            
            db.products.update_one({'_id': ObjectId(product_id)}, {'$set': {'name': name, 'price': price, 'mrp': mrp, 'description': description, 'company_id': company_id, 'categories': categories, 'imageUrls': imageUrls}})
            return ApiResponse(200, 'Product updated successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

@product_ns.route('/all-products')
class Products(Resource):
    def get(self):
        """Get all products"""

        # get query params
        company_id = request.args.get('company_id')
        category_id = request.args.get('category_id')
        search = request.args.get('search')
        lower_price = request.args.get('lower_price')
        upper_price = request.args.get('upper_price')
        limit = request.args.get('limit') or 10
        offset = request.args.get('offset') or 0
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            query = {}
            if company_id:
                query['company_id'] = company_id
            if category_id:
                query['categories'] = {'$in': [category_id]}
            if search:
                query['name'] = {'$regex': search, '$options': 'i'}
            if lower_price and upper_price:
                query['price'] = {'$gte': int(lower_price), '$lte': int(upper_price)}
            
            products = db.products.find(query).skip(int(offset)).limit(int(limit))

            products = list(products)
            for product in products:
                product['id'] = str(product['_id'])
                product.pop('_id')

                # get company details
                company = db.companies.find_one({'_id': ObjectId(product['company_id'])})

                product['company'] = {
                    'id': str(company['_id']),
                    'name': company['name'],
                    'imageUrl': company['imageUrl']
                }

                # get categories details and select only required fields
                categories = db.categories.find({'_id': {'$in': [ObjectId(category_id) for category_id in product['categories']]}})
                
                product['categories'] = [{'id': str(category['_id']), 'category_name': category['category_name'], 'imageUrl': category['imageUrl']} for category in categories]
            
            products = list(products)
            return ApiResponse(200, 'Products', {'products': products}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

@product_ns.route('/top-finds')
class TopFindProduct(Resource):
    def get(self):
        """Products with most discount"""

        offset = request.args.get('offset') or 0
        limit = request.args.get('limit') or 10

        try:
            db = DB.get_db()

            if db is None:
                return ApiError(500, 'Database Connection Error'), 500

            products = db.products.find().sort('discount', -1).skip(int(offset)).limit(int(limit))
            products = list(products)

            for product in products:
                product['id'] = str(product['_id'])
                product.pop('_id')

                # get company details
                company = db.companies.find_one({'_id': ObjectId(product['company_id'])})

                product['company'] = {
                    'id': str(company['_id']),
                    'name': company['name'],
                    'imageUrl': company['imageUrl']
                }

                # get categories details and select only required fields
                categories = db.categories.find({'_id': {'$in': [ObjectId(category_id) for category_id in product['categories']]}})
                
                product['categories'] = [{'id': str(category['_id']), 'category_name': category['category_name'], 'imageUrl': category['imageUrl']} for category in categories]
            
            products = list(products)
            return ApiResponse(200, 'Top find products', {'products': products}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400    
    

@product_ns.route('/scrap-data')
class ScrapData(Resource):
    def get(self):
        """Scrap data from a website"""
        try:
            # call the scraper function
            scrap_data_saahas()
            return ApiResponse(200, 'Data scrapped successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400