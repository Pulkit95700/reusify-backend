from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.category_model import Category

category_ns = Namespace('category', description='Category related operations')

@category_ns.route('/create-category')
class CreateCategory(Resource):
    def post(self):
        """Create a new category"""
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        imageUrl = data.get('imageUrl')

        if not name or not description:
            return ApiError(400, 'Missing name or description'), 400
        
        if not name.strip() or not description.strip():
            return ApiError(400, 'Invalid name or description'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            category = db.categories.find_one({'name': name})
            if category:
                return ApiError(400, 'Category already exists'), 400
            
            new_category = Category(name, description, imageUrl)
            created_category = db.categories.insert_one(new_category.to_dict())

            return ApiResponse(201, 'Category created successfully', {'category_id': str(created_category.inserted_id)}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        
@category_ns.route('/<string:category_id>')
class CategoryDetails(Resource):
    def get(self, category_id):
        """Get category details"""
        try:
            db = DB.get_db()
            category = db.categories.find_one({'_id': ObjectId(category_id)})
            if not category:
                return ApiError(404, 'Category not found'), 404
            
            category['id'] = str(category['_id'])
            category.pop('_id')
            return ApiResponse(200, 'Category details', {'category': category}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    def put(self, category_id):
        """Update category details"""
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        imageUrl = data.get('imageUrl')

        if not name or not description:
            return ApiError(400, 'Missing name or description'), 400
        
        if not name.strip() or not description.strip():
            return ApiError(400, 'Invalid name or description'), 400
        
        try:
            db = DB.get_db()

            category = db.categories.find_one({'_id': ObjectId(category_id)})
            if not category:
                return ApiError(404, 'Category not found'), 404
            
            db.categories.update_one({'_id': ObjectId(category_id)}, {'$set': {'name': name, 'description': description, 'imageUrl': imageUrl}})
            return ApiResponse(200, 'Category updated successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
    
    def delete(self, category_id):
        """Delete category"""
        try:
            db = DB.get_db()

            category = db.categories.find_one({'_id': ObjectId(category_id)})
            if not category:
                return ApiError(404, 'Category not found'), 404
            
            db.categories.delete_one({'_id': ObjectId(category_id)})
            return ApiResponse(200, 'Category deleted successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400
        
@category_ns.route('/all')
class Categories(Resource):
    def get(self):
        """Get all categories"""
        search = request.args.get('search') or ''
        try:
            db = DB.get_db()
            categories = db.categories.find(
                {
                    'category_name': {
                        '$regex': search,
                        '$options': 'i'
                    }
                }
            )
            categories = [{'id': str(category['_id']), 'category_name': category['category_name'], 'description': category['description'], 'imageUrl': category['imageUrl']} for category in categories]
            return ApiResponse(200, 'Categories list', {'categories': categories}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400