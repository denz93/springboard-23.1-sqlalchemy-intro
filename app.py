"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from config import DevConfig

def create_app(config=DevConfig):
  app = Flask(__name__)
  
  app.config.from_object(config)

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
      return render_template('edit-user.html', error={"message": f"Cannot find user with id '{user_id}'"})
    
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
      return render_template('edit-user.html', error=e)
    return redirect(f'/users/{user_id}')

  @app.post('/users/<int:user_id>/delete')
  def delete_user(user_id):
    delete_count = db.session.query(User).filter(User.id == user_id).delete(synchronize_session='evaluate')
    if delete_count > 0:
      db.session.commit()
    return redirect('/users')
  return app