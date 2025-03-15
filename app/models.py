from flask_login import UserMixin
from . import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    desc = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    recipes = db.relationship('Recipe', back_populates='user')  # TODO: cascade
