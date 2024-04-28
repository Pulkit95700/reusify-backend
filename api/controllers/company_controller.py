from flask_restx import Namespace, Resource
from flask import request
from api.helpers.ApiResponse import ApiResponse
from api.helpers.ApiError import ApiError
from api.db import db as DB
from bson.objectid import ObjectId
from api.models.company_model import Company

company_ns = Namespace('company', description='Company related operations')


@company_ns.route('/signup')
class SignUp(Resource):
    def post(self):
        """Create a new company"""
        # creating company temporarily without authentication

        data = request.get_json()
        name = data.get('name')
        address = data.get('address')
        phone = data.get('phone')
        email = data.get('email')
        imageUrl = data.get('imageUrl')

        if not name or not address or not phone or not email:
            return ApiError(400, 'Missing name, address, phone or email'), 400
        
        if not name.strip() or not address.strip() or not phone.strip() or not email.strip():
            return ApiError(400, 'Invalid name, address, phone or email'), 400
        
        if(len(phone) < 10):
            return ApiError(400, 'Phone number must be at least 10 characters'), 400
        
        if(email.find('@') == -1 or email.find('.') == -1):
            return ApiError(400, 'Invalid Email'), 400
        
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            company = db.companies.find_one({'email': email})
            if company:
                return ApiError(400, 'Company already exists'), 400
            
            new_company = Company(name, address, phone, email, imageUrl)
            created_company = db.companies.insert_one(new_company.to_dict())

            return ApiResponse(201, 'Company created successfully', {'company_id': str(created_company.inserted_id)}), 201
        except Exception as e:
            return ApiError(400, str(e)), 400
    
@company_ns.route('/<string:company_id>')
class CompanyDetails(Resource):
    def get(self, company_id):
        """Get company details"""
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            company = db.companies.find_one({'_id': ObjectId(company_id)})
            if not company:
                return ApiError(404, 'Company not found'), 404
            
            company['id'] = str(company.get('_id'))
            company.pop('_id')
            return ApiResponse(200, 'Company details', {'company': company}), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

    def put(self, company_id):
        """Update company details"""
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            company = db.companies.find_one({'_id': ObjectId(company_id)})
            if not company:
                return ApiError(404, 'Company not found'), 404
            
            data = request.get_json()
            name = data.get('name')
            address = data.get('address')
            phone = data.get('phone')
            email = data.get('email')
            imageUrl = data.get('imageUrl')
            
            if not name and not address and not phone and not email and not imageUrl:
                return ApiError(400, 'Missing name, address, phone, email or imageUrl'), 400
            
            if name:
                company['name'] = name
            if address:
                company['address'] = address
            if phone:
                company['phone'] = phone
            if email:
                company['email'] = email
            if imageUrl:
                company['imageUrl'] = imageUrl
            
            db.companies.update_one({'_id': ObjectId(company_id)}, {'$set': company})
            return ApiResponse(200, 'Company updated successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400

    def delete(self, company_id):
        """Delete company"""
        try:
            db = DB.get_db()

            if(db is None):
                return ApiError(500, 'Database Connection Error'), 500
            
            company = db.companies.find_one({'_id': ObjectId(company_id)})
            if not company:
                return ApiError(404, 'Company not found'), 404
            
            db.companies.delete_one({'_id': ObjectId(company_id)})
            return ApiResponse(200, 'Company deleted successfully'), 200
        except Exception as e:
            return ApiError(400, str(e)), 400