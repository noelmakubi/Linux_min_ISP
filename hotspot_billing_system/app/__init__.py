from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='../config/settings.py'):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_pyfile(config_name)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes.portal import portal_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(portal_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
    
    return app
