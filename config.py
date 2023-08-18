class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = None 
  
class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql:///blogly'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    TESTING = True