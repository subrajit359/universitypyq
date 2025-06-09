#!/usr/bin/env python3
"""
Database migration script for UniversityPYQ
Handles database schema creation and migration to Supabase PostgreSQL
"""

import os
import sys
from app import create_app, db
from models import User, Paper, Bookmark, Feedback
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_to_supabase():
    """Migrate database schema to Supabase PostgreSQL"""
    
    # Set your Supabase database URL
    supabase_url = "postgresql://postgres:Papers%23444@db.kpdmfxyhcogvxxlpuxyl.supabase.co:5432/postgres"
    
    # Temporarily override the DATABASE_URL
    original_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = supabase_url
    
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Creating database tables...")
            
            # Drop all tables first (be careful in production!)
            db.drop_all()
            
            # Create all tables
            db.create_all()
            
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@universitypyq.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin_user.set_password('Pyqs2025')
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Admin user created successfully")
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Admin user might already exist: {e}")
            
            logger.info("Database migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        # Restore original DATABASE_URL
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            os.environ.pop('DATABASE_URL', None)
    
    return True

if __name__ == "__main__":
    success = migrate_to_supabase()
    sys.exit(0 if success else 1)