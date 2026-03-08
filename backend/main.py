from flask import Flask, jsonify
from flask_cors import CORS
import os
from pathlib import Path

from .routes.document_routes import document_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configure upload folder if needed
    base_dir = Path(__file__).parent
    temp_dir = base_dir / "tmp"
    temp_dir.mkdir(exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "service": "ManuscriptMagic API"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
