from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from app.routes.basic import basic_bp
from app.routes.auth import auth_bp
from app.routes.eda import eda_bp
from app.routes.chat import chat_bp
from app.routes.chat_rooms import chat_rooms_bp
from app.routes.anomaly import anomaly_bp
from app.routes.visualization import visualization_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET
    
    # Simple CORS setup
    CORS(app, 
         origins="*",  # Allow all origins
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    jwt = JWTManager(app)

    app.register_blueprint(basic_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(eda_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(chat_rooms_bp)
    app.register_blueprint(anomaly_bp)
    app.register_blueprint(visualization_bp)

    # Error handlers for database issues
    @app.errorhandler(ServerSelectionTimeoutError)
    def handle_db_timeout(e):
        return jsonify({
            "error": "Database connection timeout",
            "message": "The server is experiencing database connectivity issues. Please try again later."
        }), 503

    @app.errorhandler(ConnectionFailure)
    def handle_db_connection(e):
        return jsonify({
            "error": "Database connection failed", 
            "message": "Cannot connect to the database. The server may be temporarily unavailable."
        }), 503

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        try:
            from app.models.mongo import client
            client.admin.command('ping')
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "message": "All systems operational"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "message": "Database connection issues detected"
            }), 503

    return app