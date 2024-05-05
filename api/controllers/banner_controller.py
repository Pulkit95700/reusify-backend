from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.banner_model import Banner
# from api.middlewares.auth_middleware import protected


banner_ns = Namespace('banner', description='Banner related operations')

@banner_ns.route('/add-banner')
class AddBanner(Resource):
    # @protected
    def post(self):
        """Add banner"""
    
        data = request.get_json()
        title = data.get('title')
        imageUrl = data.get('imageUrl')

        if not title or not imageUrl:
            return ApiError(400, 'Missing title or imageUrl'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            banner = db.banners.find_one({'title': title})
            if banner:
                return ApiError(400, 'Banner already exists'), 400
            
            new_banner = Banner(title, imageUrl)
            created_banner = db.banners.insert_one(new_banner.to_dict())

            return ApiResponse(201, 'Banner added successfully'), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
        

@banner_ns.route('/get-banners')
class GetBanners(Resource):
    def get(self):
        """Get all banners"""
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            banners = db.banners.find()
            banner_list = []
            for banner in banners:
                banner.pop('_id')
                banner_list.append(banner)
            
            return ApiResponse(200, 'Banners retrieved successfully', banner_list), 200
        except Exception as e:
            return ApiError(400, str(e)), 400