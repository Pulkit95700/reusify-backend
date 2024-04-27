# Desc: Database connection and configuration
from flask_pymongo import PyMongo
class MongoDb:
    db = None
    
    def __init__(self):
        pass

    def init_db(self, app):
        self.db = PyMongo(app).db
        if self.db is not None:
            print("Database connected successfully")
        else:
            print("Database connection error")

    def get_db(self):
        return self.db

db = MongoDb()