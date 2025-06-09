#!/usr/bin/env python3
"""
Deployment configuration for Render platform
Sets up environment variables and database configuration
"""

import os

def setup_render_environment():
    """Configure environment variables for Render deployment"""
    
    # Database configuration for Render
    render_env = {
        'DATABASE_URL': 'postgresql://postgres:Papers%23444@db.kpdmfxyhcogvxxlpuxyl.supabase.co:5432/postgres',
        'CLOUDINARY_CLOUD_NAME': 'dn5l0jh19',
        'CLOUDINARY_API_KEY': '741223792776498',
        'CLOUDINARY_API_SECRET': '36ODK08w5GkAd0UKekFkFt3QyXo',
        'CLOUDINARY_UPLOAD_PRESET': 'Papers',
        'SESSION_SECRET': 'your-production-secret-key-change-this',
        'FLASK_ENV': 'production'
    }
    
    print("Environment variables for Render deployment:")
    print("-" * 50)
    for key, value in render_env.items():
        if 'SECRET' in key or 'PASSWORD' in key:
            masked_value = value[:8] + '*' * (len(value) - 8) if len(value) > 8 else '*' * len(value)
            print(f"{key}={masked_value}")
        else:
            print(f"{key}={value}")
    print("-" * 50)
    
    return render_env

if __name__ == "__main__":
    setup_render_environment()