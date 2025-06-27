from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from app.utils.jwt_utils import hash_password, create_access_token, create_refresh_token, verify_password, verify_refresh_token
from app.models.mongo import user_collection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if user_collection.find_one({"username": data["username"]}):
            return jsonify({"error": "User already exists"}), 400
        hashed = hash_password(data["password"])
        user_collection.insert_one({"username": data["username"], "password": hashed})
        return jsonify({"message": "User created"}), 201
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(f"Database connection error in register: {e}")
        return jsonify({
            "error": "Database connection failed",
            "message": "Cannot connect to the database. Please try again later."
        }), 503
    except Exception as e:
        print(f"Unexpected error in register: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = user_collection.find_one({"username": data["username"]})
        if not user or not verify_password(data["password"], user["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        
        username = data["username"]
        access_token = create_access_token({"sub": username})
        refresh_token = create_refresh_token({"sub": username})
        
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }), 200
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(f"Database connection error in login: {e}")
        return jsonify({
            "error": "Database connection failed",
            "message": "Cannot connect to the database. Please try again later."
        }), 503
    except Exception as e:
        print(f"Unexpected error in login: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    try:
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({"error": "Refresh token required"}), 400
        
        username = verify_refresh_token(refresh_token)
        if not username:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        user = user_collection.find_one({"username": username})
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        new_access_token = create_access_token({"sub": username})
        new_refresh_token = create_refresh_token({"sub": username})
        
        return jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer"
        }), 200
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        print(f"Database connection error in refresh: {e}")
        return jsonify({
            "error": "Database connection failed",
            "message": "Cannot connect to the database. Please try again later."
        }), 503
    except Exception as e:
        print(f"Unexpected error in refresh: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200