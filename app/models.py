from flask_login import UserMixin
from sqlalchemy import func, select
from . import db

user_likes_recipe = db.Table('user_likes_recipe',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                )

user_dislikes_recipe = db.Table('user_dislikes_recipe',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                )

user_save_recipe = db.Table('user_save_recipe',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                )


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.String(1000), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='recipes')
    liked_by_users = db.relationship('User', secondary=user_likes_recipe, back_populates='liked_recipes')
    disliked_by_users = db.relationship('User', secondary=user_dislikes_recipe, back_populates='disliked_recipes')
    saved_by_users = db.relationship('User', secondary=user_save_recipe, back_populates='saved_recipes')

    @classmethod
    def get_like_ratio(cls):
        likes = select(func.count()).where(user_likes_recipe.c.recipe_id == cls.id).scalar_subquery()
        dislikes = select(func.count()).where(user_dislikes_recipe.c.recipe_id == cls.id).scalar_subquery()

        # check like-dislike difference and consider as a weight the amount of people that voted
        # also add 0.01 in case likes == dislikes so that the weight is taken into account
        return (likes - dislikes + 0.01) * (likes + dislikes)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    recipes = db.relationship('Recipe', back_populates='user')
    liked_recipes = db.relationship('Recipe', secondary=user_likes_recipe, back_populates='liked_by_users')
    disliked_recipes = db.relationship('Recipe', secondary=user_dislikes_recipe, back_populates='disliked_by_users')
    saved_recipes = db.relationship('Recipe', secondary=user_save_recipe, back_populates='saved_by_users')
