from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

mongo = PyMongo()
jwt = JWTManager()
limiter = Limiter(get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    
    mongo.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    
    # Register blueprints
    from .routes.auth import auth_blueprint
    from .routes.users import users_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(users_blueprint)
    
    return app
