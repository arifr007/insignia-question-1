from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
from app.config import Config
import sys

try:
    client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client['chat_history_db']
    print("✅ Successfully connected to MongoDB")
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    print(f"❌ Cannot connect to MongoDB: {e}")
    print("Please ensure MongoDB is running and accessible")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected database error: {e}")
    sys.exit(1)

# Collections
user_collection = db['users']
chat_rooms_collection = db['chat_rooms']
chat_messages_collection = db['chat_messages']

# Chat Room Model
class ChatRoom:
    @staticmethod
    def create_room(username, title=None):
        """Create a new chat room for a user"""
        room_data = {
            "username": username,
            "title": title or "New Chat",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0
        }
        result = chat_rooms_collection.insert_one(room_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_rooms(username, limit=50):
        """Get all chat rooms for a user"""
        rooms = chat_rooms_collection.find(
            {"username": username}
        ).sort("updated_at", -1).limit(limit)
        
        rooms_list = []
        for room in rooms:
            rooms_list.append({
                "id": str(room["_id"]),
                "title": room["title"],
                "created_at": room["created_at"],
                "updated_at": room["updated_at"],
                "message_count": room["message_count"]
            })
        return rooms_list
    
    @staticmethod
    def get_room(room_id, username):
        """Get a specific room if it belongs to the user"""
        try:
            room = chat_rooms_collection.find_one({
                "_id": ObjectId(room_id),
                "username": username
            })
            if room:
                return {
                    "id": str(room["_id"]),
                    "title": room["title"],
                    "created_at": room["created_at"],
                    "updated_at": room["updated_at"],
                    "message_count": room["message_count"]
                }
            return None
        except:
            return None
    
    @staticmethod
    def update_room_title(room_id, username, title):
        """Update room title"""
        try:
            result = chat_rooms_collection.update_one(
                {"_id": ObjectId(room_id), "username": username},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def delete_room(room_id, username):
        """Delete a room and all its messages"""
        try:
            # Delete all messages in the room
            chat_messages_collection.delete_many({"room_id": room_id})
            # Delete the room
            result = chat_rooms_collection.delete_one({
                "_id": ObjectId(room_id),
                "username": username
            })
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def update_room_activity(room_id):
        """Update room's last activity timestamp and increment message count"""
        try:
            chat_rooms_collection.update_one(
                {"_id": ObjectId(room_id)},
                {
                    "$set": {"updated_at": datetime.utcnow()},
                    "$inc": {"message_count": 1}
                }
            )
        except:
            pass

# Chat Message Model
class ChatMessage:
    @staticmethod
    def add_message(room_id, message_type, content, intent=None, query=None, chart_data=None, summary=None):
        """Add a message to a chat room"""
        message_data = {
            "room_id": room_id,
            "type": message_type,  # 'user', 'bot', 'error'
            "content": content,
            "intent": intent,
            "query": query,
            "timestamp": datetime.utcnow()
        }
        
        # Add chart data if provided
        if chart_data:
            message_data["chart_data"] = chart_data
        
        # Add summary if provided  
        if summary:
            message_data["summary"] = summary
            
        result = chat_messages_collection.insert_one(message_data)
        
        # Update room activity
        ChatRoom.update_room_activity(room_id)
        
        return str(result.inserted_id)
    
    @staticmethod
    def get_room_messages(room_id, limit=100):
        """Get messages for a chat room"""
        messages = chat_messages_collection.find(
            {"room_id": room_id}
        ).sort("timestamp", 1).limit(limit)
        
        messages_list = []
        for msg in messages:
            message_data = {
                "id": str(msg["_id"]),
                "type": msg["type"],
                "content": msg["content"],
                "intent": msg.get("intent"),
                "query": msg.get("query"),
                "timestamp": msg["timestamp"]
            }
            
            # Include chart_data and summary if they exist
            if "chart_data" in msg:
                message_data["chart_data"] = msg["chart_data"]
            if "summary" in msg:
                message_data["summary"] = msg["summary"]
                
            messages_list.append(message_data)
        return messages_list
    
    @staticmethod
    def get_recent_context(room_id, limit=10):
        """Get recent messages for context (limit to last N messages)"""
        messages = chat_messages_collection.find(
            {"room_id": room_id}
        ).sort("timestamp", -1).limit(limit)
        
        # Reverse to get chronological order
        messages_list = []
        for msg in reversed(list(messages)):
            messages_list.append({
                "type": msg["type"],
                "content": msg["content"],
                "intent": msg.get("intent"),
                "timestamp": msg["timestamp"]
            })
        return messages_list
    
    @staticmethod
    def clear_room_messages(room_id):
        """Clear all messages in a room"""
        result = chat_messages_collection.delete_many({"room_id": room_id})
        # Reset message count
        chat_rooms_collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"message_count": 0, "updated_at": datetime.utcnow()}}
        )
        return result.deleted_count