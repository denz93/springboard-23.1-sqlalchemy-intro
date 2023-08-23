from dotenv import dotenv_values
from os import getenv
dotenv = dotenv_values()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = None 
    SECRECT_KEY = getenv('SERECT_KEY', dotenv.get('SECRET_KEY'))
    
class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql:///blogly'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    TESTING = True

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URI', dotenv.get('DATABASE_URI'))

