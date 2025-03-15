from flask import Flask
from .routes import routes
from .auth import auth

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my_secret_key'

    app.register_blueprint(routes, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    return app