from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "recipity.db"

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

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # prompt to login page if login required
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app