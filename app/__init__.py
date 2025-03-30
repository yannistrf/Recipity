from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_hashing import Hashing
from sqlalchemy import func, select
import os
import random
import json

db = SQLAlchemy()
hashing = Hashing()
DB_NAME = "recipity.db"
UPLOAD_FOLDER = "./app/static/photo_uploads"
STATIC_UPLOAD_FOLDER = "./photo_uploads"
TEST_DATA = "./app/test_data.json"

def create_app():
    # avoid circular dependency
    from .routes import routes
    from .auth import auth

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my_secret_key'

    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    from .models import Recipe, User

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_test_data()

    hashing.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # prompt to login page if login required
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

    return app

def create_test_data():
    from .models import Recipe, User
    
    # Check if data already exists
    if db.session.execute(db.select(func.count()).select_from(User)).scalar() != 0:
        return

    with open(TEST_DATA) as f:
        data = json.load(f)

    for user_data in data["users"]:
        username = user_data["username"]
        password = hashing.hash_value(user_data["password"], username)
        db.session.add(User(username=username, password=password))

    users_count = len(data["users"])

    for recipe_data in data["recipes"]:
        recipe = Recipe(name=recipe_data["name"], desc=recipe_data["desc"],
                                     user_id=random.randint(1, users_count),
                                     photo_path=STATIC_UPLOAD_FOLDER + "/" + recipe_data["photo"])

        db.session.add(recipe)

        # get random users and in random like or dislike the recipe
        rand_user_ids = random.sample(range(1, users_count + 1), random.randint(1, users_count))
        for user_id in rand_user_ids:
            user = db.session.get(User, user_id)
            if random.randint(0, 1):
                recipe.liked_by_users.append(user)
            else:
                recipe.disliked_by_users.append(user)

        
    db.session.commit()
    print("Test data inserted!")