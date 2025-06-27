from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.chat_service import handle_chat_message

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/<room_id>', methods=['POST'])
@jwt_required()
def chat(room_id):
    username = get_jwt_identity()
    data = request.json
    query = data.get('message')

    if not query:
        return jsonify({"error": "No message provided"}), 400

    response, metadata = handle_chat_message(room_id, username, query)

    if metadata.get("error"):
        return jsonify(metadata), metadata.get("status", 500)

    return jsonify({
        "response": response,
        **metadata
    })