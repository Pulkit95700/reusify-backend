# Creating the User model in flask application with Flask PyMongo
from datetime import datetime
from bson import Timestamp
from api.utils import get_timestamp

class User:
    def __init__(self, full_name, password, email, fcm_token=None, created_at=get_timestamp()):
        self.full_name = full_name
        self.password = password
        self.email = email
        self.fcm_token = fcm_token
        self.created_at = created_at

    def to_json(self):
        return {
            'full_name': self.full_name,
            'password': self.password,
            'email': self.email,
            'created_at': self.created_at,
            'fcm_token': self.fcm_token
        }