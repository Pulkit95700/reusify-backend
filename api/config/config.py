# os is used to get the environment variables
import os
from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    MONGO_URI = config('MONGO_URI')
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = config('JWT_ACCESS_TOKEN_EXPIRES', cast=int, default=900)
    JWT_REFRESH_TOKEN_EXPIRES = config('JWT_REFRESH_TOKEN_EXPIRES', cast=int, default=2592000)
    PORT = config('PORT', cast=int, default=5000)

class DevConfig(Config):
    DEBUG = config('DEBUG', cast=bool, default=True)

class TestConfig(Config):
    pass 

class ProductionConfig(Config):
    DEBUG = False


config_dict = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProductionConfig
}