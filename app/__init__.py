from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    from . import routes
    from .admin import routes as admin_routes
    
    app.register_blueprint(routes.main)
    app.register_blueprint(admin_routes.admin, url_prefix='/admin')
    
    return app
