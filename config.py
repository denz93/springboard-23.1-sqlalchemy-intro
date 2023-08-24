from dotenv import dotenv_values
from os import getenv
dotenvs = dotenv_values()
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = None 
    SECRET_KEY = getenv('SECRET_KEY', dotenvs.get('SECRET_KEY'))
    
class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql:///blogly'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    TESTING = True

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URI', dotenvs.get('DATABASE_URI'))

