from flask import Blueprint, jsonify
from datetime import datetime

basic_bp = Blueprint('basic', __name__)

@basic_bp.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "API is working",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

@basic_bp.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Service is running",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "Service is operational"
    }), 200
