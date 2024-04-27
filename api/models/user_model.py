# Creating the User model in flask application with Flask PyMongo
from datetime import datetime
from bson import Timestamp
from api.utils import get_timestamp

class User:
    def __init__(self, username, password, email, role, fcm_token, created_at=get_timestamp()):
        self.username = username
        self.password = password
        self.role = role
        self.email = email
        self.fcm_token = fcm_token
        self.created_at = created_at

    def to_json(self):
        return {
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'email': self.email,
            'created_at': self.created_at,
            'fcm_token': self.fcm_token
        }