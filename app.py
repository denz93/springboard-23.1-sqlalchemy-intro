"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User, Post
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from config import DevConfig, ProdConfig, TestingConfig
from datetime import datetime
import os

def datetime_format(d: datetime, format: str):
  return d.strftime(format)

def load_config(mode='dev'):
  env = os.getenv('ENV', mode)
  
  if env == 'PROD':
    config = ProdConfig
  elif env == 'TEST':
    config = TestingConfig
  else:
    config = DevConfig
  return config

def create_app():
  config = load_config()
  app = Flask(__name__)

  app.secret_key = config.SECRECT_KEY
  app.config.from_object(config)
  app.jinja_env.filters['datetime'] = datetime_format
  connect_db(app)
  with app.app_context():
    db.create_all()

  @app.get('/')
  def home_page():
    return redirect('/users')

  @app.get('/users')
  def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)

  @app.get('/users/new')
  def new_user_page():
    return render_template('create-user.html')

  @app.post('/users/new')
  def add_new_user():
    user = User(
      first_name=request.form.get('first_name'), 
      last_name=request.form.get('last_name'), 
      image_url=request.form.get('image_url', None))
    db.session.add(user)

    try:
      db.session.commit()
    except SQLAlchemyError as e:
      return render_template('create-user.html', error=e)
    return redirect('/users')

  @app.get('/users/<int:user_id>')
  def user_page(user_id):
    user = db.session.query(User).get(user_id)
    return render_template('user.html', user_id=user_id, user=user)

  @app.get('/users/<int:user_id>/edit')
  def user_edit_page(user_id):
    user = db.session.query(User).get(user_id)
    return render_template('edit-user.html', user=user)

  @app.post('/users/<int:user_id>/edit')
  def edit_user(user_id):
    user = db.session.query(User).get(user_id)
    if not user:
      flash(f"Cannot find user with id '{user_id}'")
      return render_template('edit-user.html')
    
    first_name, last_name, image_url = \
      request.form.get('first_name'),\
      request.form.get('last_name'),\
      request.form.get('image_url', None)
    if first_name:
      user.first_name = first_name
    if last_name:
      user.last_name = last_name
    user.image_url = image_url
    try:
      db.session.commit()
    except SQLAlchemyError as e:
      flash(str(e), 'error')
      return render_template('edit-user.html')
    return redirect(f'/users/{user_id}')

  @app.post('/users/<int:user_id>/delete')
  def delete_user(user_id):
    user = db.session.get(User, user_id)
    # delete_count = db.session.query(User).filter(User.id == user_id).delete(synchronize_session='evaluate')
    if user:
      db.session.delete(user)
      db.session.commit()
    return redirect('/users')
  
  @app.get('/users/<int:user_id>/posts/new')
  def new_post_page(user_id):
    user = db.session.get(User, user_id)
    if user is None:
      flash(f"Cannot find user with id '{user_id}'")
      render_template('new-post.html')
    return render_template('new-post.html', user=user)
  
  @app.post('/users/<int:user_id>/posts/new')
  def create_post(user_id):
    user = db.session.get(User, user_id)
    if user is None:
      flash(f"Cannot find user with id '{user_id}'")
      return render_template('new-post.html')
    post = Post(
      title = request.form.get('title'), 
      content = request.form.get('content'),
      author = user
      )
    db.session.add(post)
    db.session.commit()
    return redirect(f'/users/{user_id}')
  
  @app.get('/posts/<int:post_id>')
  def post_page(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
      flash(f"Cannot find post with id '{post_id}'", "error")
    return render_template('post.html', post=post)
  
  @app.get('/posts/<int:post_id>/edit')
  def edit_post_page(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
      flash(f"Cannot find post with id '{post_id}'", "error")
    return render_template('edit-post.html', post=post)
  
  @app.post('/posts/<int:post_id>/edit')
  def edit_post(post_id):
    post = db.session.get(Post, post_id)
    title = request.form.get('title')
    content = request.form.get('content')
    if title and len(title) > 0:
      post.title = title
    if content and len(content) > 0:
      post.content = content 
    db.session.commit()

    return redirect(f'/posts/{post_id}')
  @app.post('/posts/<int:post_id>/delete')
  def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post:
      db.session.delete(post)
      db.session.commit()
    return redirect(f'/users/{post.author_id}')
  return app