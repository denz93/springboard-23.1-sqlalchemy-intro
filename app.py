"""Blogly application."""

from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User, Post, Tag
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
  app.secret_key = config.SECRET_KEY
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
    tags = db.session.query(Tag).all()
    return render_template('new-post.html', user=user, tags=tags)
  
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
    tags = list(map(lambda tag_id: Tag(id=tag_id), request.form.getlist('tags[]', [])))
    post.tags = tags
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
    all_tags = db.session.query(Tag)
    if post is None:
      flash(f"Cannot find post with id '{post_id}'", "error")
    return render_template('edit-post.html', post=post, all_tags=all_tags)
  
  @app.post('/posts/<int:post_id>/edit')
  def edit_post(post_id):
    post = db.session.get(Post, post_id)
    title = request.form.get('title')
    content = request.form.get('content')
    tags = list(
      map(
        lambda tag_id: db.session.get(Tag, tag_id), 
        request.form.getlist('tags[]')
      )
    )
    if title and len(title) > 0:
      post.title = title
    if content and len(content) > 0:
      post.content = content
    post.tags.clear()
    post.tags.extend(tags)
    db.session.commit()

    return redirect(f'/posts/{post_id}')
  @app.post('/posts/<int:post_id>/delete')
  def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post:
      db.session.delete(post)
      db.session.commit()
    return redirect(f'/users/{post.author_id}')
  
  @app.get('/tags/new')
  def create_tag_page():
    return render_template('new-tag.html') 

  @app.get('/tags')
  def tags_page():
    tags = db.session.query(Tag).all()
    return render_template('tags.html', tags=tags) 

  @app.get('/tags/<int:tag_id>')
  def tag_page(tag_id: int):
    tag = db.session.get(Tag, tag_id)
    return render_template('tag.html', tag=tag)

  @app.get('/tags/<int:tag_id>/edit')
  def edit_tag_page(tag_id: int):
    tag = db.session.get(Tag)
    return render_template('edit-tag.html', tag=tag) 

  @app.post('/tags/new')
  def create_tag():
    name = request.form.get('name', None)

    if name is None or len(name) < 1:
      flash('Tag name should be provided', 'error')
      return redirect('/tags/new')
    existingTag = db.session.query(Tag).filter(Tag.name == name).first()

    if existingTag:
      flash(f'Tag "{name}" already exists', 'error')
      return redirect('/tags/new')

    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    flash(f'Tag "{name}" created', 'success')
    return redirect('/tags/new')
  
  @app.post('/tags/<int:tag_id>/edit')
  def edit_tag(tag_id: int):
    name = request.form.get('name')

    if name is None or len(name) < 1:
      flash(f'Tag name is required', 'error')
      return redirect(f'/tags/{tag_id}/edit')
    
    existingTag = db.session.query(Tag).filter(Tag.id != tag_id, Tag.name == name).first()
    if existingTag:
      flash(f'Tag "{name}" already exists', 'error')
      return redirect(f'/tags/{tag_id}/edit')

    tag = db.session.get(Tag, tag_id)

    if tag is None:
      flash(f'Tag id "{tag_id}" not found', 'error')
      return redirect(f'/tags/{tag_id}/edit')
    
    tag.name = name
    db.session.commit()

    flash(f'Tag name updated to "{name}"')
    return redirect(f'/tags/{tag_id}/edit')


  @app.post('/tags/<int:tag_id>/delete')
  def delete_tag(tag_id: int):
    tag = db.session.get(Tag, tag_id)

    if tag is None:
      flash(f'Tag "{tag_id}" already exists', 'error')
      return redirect(f'/tags')
    
    db.session.delete(tag)
    db.session.commit()
    flash(f'Tag "{tag.name}" deleted', 'success')
    return redirect('/tags')
  return app