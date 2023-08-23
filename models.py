"""Models for Blogly."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy import orm
from datetime import datetime
from typing import List 

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
    posts = orm.relationship('Post', back_populates='author', cascade='all, delete')
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow())
    author_id = Column(Integer, ForeignKey('users.id'))
    author = orm.relationship('User', back_populates='posts')
    tags: orm.Mapped[List['Tag']] = orm.relationship(secondary='post_tag', back_populates='posts')

class Tag(db.Model):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    posts: orm.Mapped[List[Post]] = orm.relationship(secondary='post_tag', back_populates='tags')

class PostTag(db.Model):
    __tablename__ = 'post_tag'
    post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)