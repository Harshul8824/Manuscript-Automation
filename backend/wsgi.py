"""
WSGI entry point for production deployment with Gunicorn
"""
from app import create_app
import os

# Create Flask app instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run()
