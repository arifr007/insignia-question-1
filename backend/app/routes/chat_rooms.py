from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.mongo import ChatRoom, ChatMessage

chat_rooms_bp = Blueprint('chat_rooms', __name__)

@chat_rooms_bp.route('/rooms', methods=['GET'])
@jwt_required()
def get_rooms():
    username = get_jwt_identity()
    rooms = ChatRoom.get_user_rooms(username)
    return jsonify({"rooms": rooms})

@chat_rooms_bp.route('/rooms', methods=['POST'])
@jwt_required()
def create_room():
    username = get_jwt_identity()
    data = request.json or {}
    title = data.get('title', 'New Chat')
    
    room_id = ChatRoom.create_room(username, title)
    room = ChatRoom.get_room(room_id, username)
    
    return jsonify({
        "message": "Room created successfully",
        "room": room
    }), 201

@chat_rooms_bp.route('/rooms/<room_id>', methods=['GET'])
@jwt_required()
def get_room(room_id):
    username = get_jwt_identity()
    room = ChatRoom.get_room(room_id, username)
    
    if not room:
        return jsonify({"error": "Room not found"}), 404
    
    messages = ChatMessage.get_room_messages(room_id)
    
    return jsonify({
        "room": room,
        "messages": messages
    })

@chat_rooms_bp.route('/rooms/<room_id>', methods=['PUT'])
@jwt_required()
def update_room(room_id):
    username = get_jwt_identity()
    data = request.json
    title = data.get('title')
    
    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    success = ChatRoom.update_room_title(room_id, username, title)
    
    if not success:
        return jsonify({"error": "Room not found or update failed"}), 404
    
    return jsonify({"message": "Room updated successfully"})

@chat_rooms_bp.route('/rooms/<room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    username = get_jwt_identity()
    success = ChatRoom.delete_room(room_id, username)
    
    if not success:
        return jsonify({"error": "Room not found or delete failed"}), 404
    
    return jsonify({"message": "Room deleted successfully"})

@chat_rooms_bp.route('/rooms/<room_id>/messages', methods=['GET'])
@jwt_required()
def get_room_messages(room_id):
    username = get_jwt_identity()
    room = ChatRoom.get_room(room_id, username)
    
    if not room:
        return jsonify({"error": "Room not found"}), 404
    
    messages = ChatMessage.get_room_messages(room_id)
    return jsonify({"messages": messages})

@chat_rooms_bp.route('/rooms/<room_id>/messages', methods=['DELETE'])
@jwt_required()
def clear_room_messages(room_id):
    username = get_jwt_identity()
    room = ChatRoom.get_room(room_id, username)
    
    if not room:
        return jsonify({"error": "Room not found"}), 404
    
    deleted_count = ChatMessage.clear_room_messages(room_id)
    return jsonify({
        "message": f"Cleared {deleted_count} messages",
        "deleted_count": deleted_count
    })
