import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name='dn5l0jh19',
    api_key='741223792776498',
    api_secret='36ODK08w5GkAd0UKekFkFt3QyXo'
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass    

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration - use environment DATABASE_URL for Supabase connection
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Fallback to your Supabase URL
        database_url = "postgresql://postgres:Papers%23444@db.kpdmfxyhcogvxxlpuxyl.supabase.co:5432/postgres"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 30,
        "pool_size": 3,
        "max_overflow": 5
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Cloudinary configuration
    app.config["CLOUDINARY_CLOUD_NAME"] = os.environ.get("CLOUDINARY_CLOUD_NAME")
    app.config["CLOUDINARY_API_KEY"] = os.environ.get("CLOUDINARY_API_KEY")
    app.config["CLOUDINARY_API_SECRET"] = os.environ.get("CLOUDINARY_API_SECRET")
    app.config["CLOUDINARY_UPLOAD_PRESET"] = os.environ.get("CLOUDINARY_UPLOAD_PRESET")
    
    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max file size
    app.config["UPLOAD_EXTENSIONS"] = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import models after db initialization
    from models import User, Paper, Bookmark
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register routes
    import routes
    routes.register_routes(app)
    
    # Context processor for current year
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.now().year}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='universitypyqs@gmail.com',
                first_name='Admin',
                last_name='User',
                password_hash=generate_password_hash('Pyqs2025'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Admin user created with username: admin, password: admin123')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
