"""Models for Blogly."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

db = SQLAlchemy()

def connect_db(app):
    db.app = app 
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    image_url = Column(String) 
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
