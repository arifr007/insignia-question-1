import { writable } from 'svelte/store';
import api from '../services/api.js';

// Auth store
export const user = writable(null);
export const isAuthenticated = writable(false);

// Chat Room store
export const chatRooms = writable([]);
export const currentRoom = writable(null);
export const currentRoomMessages = writable([]);
export const currentMessage = writable('');
export const sidebarVisible = writable(false);

// App state
export const currentTab = writable('dashboard');
export const loading = writable(false);
export const error = writable(null);

// Initialize auth state only if we actually have a valid token
if (typeof window !== 'undefined') {
  const token = api.getAccessToken();
  if (token && !api.isTokenExpired(token)) {
    isAuthenticated.set(true);
  } else if (token && api.isTokenExpired(token)) {
    // Clear expired tokens silently without dispatching events
    api.clearTokens();
  }
}

// Chat Room management
export const chatRoomStore = {
  async loadRooms() {
    try {
      const response = await api.getChatRooms();
      chatRooms.set(response.rooms || []);
      return response.rooms || [];
    } catch (error) {
      console.error('Failed to load chat rooms:', error);
      return [];
    }
  },

  async createRoom(title = 'New Chat') {
    try {
      const response = await api.createChatRoom(title);
      if (response.room) {
        chatRooms.update(rooms => [response.room, ...rooms]);
        return response.room;
      }
    } catch (error) {
      console.error('Failed to create chat room:', error);
      throw error;
    }
  },

  async selectRoom(roomId) {
    try {
      const response = await api.getChatRoom(roomId);
      if (response.room && response.messages) {
        currentRoom.set(response.room);
        currentRoomMessages.set(response.messages);
        localStorage.setItem('current_room_id', roomId);
        return response;
      }
    } catch (error) {
      console.error('Failed to load chat room:', error);
      throw error;
    }
  },

  async updateRoomTitle(roomId, title) {
    try {
      await api.updateChatRoom(roomId, title);
      chatRooms.update(rooms =>
        rooms.map(room => (room.id === roomId ? { ...room, title } : room))
      );
      currentRoom.update(room => (room && room.id === roomId ? { ...room, title } : room));
    } catch (error) {
      console.error('Failed to update room title:', error);
      throw error;
    }
  },

  async deleteRoom(roomId) {
    try {
      await api.deleteChatRoom(roomId);
      chatRooms.update(rooms => rooms.filter(room => room.id !== roomId));

      // If deleting current room, clear it
      currentRoom.update(room => {
        if (room && room.id === roomId) {
          currentRoomMessages.set([]);
          localStorage.removeItem('current_room_id');
          return null;
        }
        return room;
      });
    } catch (error) {
      console.error('Failed to delete room:', error);
      throw error;
    }
  },

  async sendMessage(roomId, message) {
    try {
      // Add user message immediately to show in UI
      const userMessage = {
        type: 'user',
        content: message,
        timestamp: new Date(),
        id: 'temp-' + Date.now() // Temporary ID
      };
      currentRoomMessages.update(messages => [...messages, userMessage]);

      // Send message to backend (backend will save both user and bot messages)
      const response = await api.sendMessage(roomId, message);

      // Reload messages from server to get the complete conversation including any chart data
      await this.selectRoom(roomId);

      // Update room's last activity
      chatRooms.update(rooms =>
        rooms.map(room =>
          room.id === roomId
            ? { ...room, updated_at: new Date(), message_count: room.message_count + 2 }
            : room
        )
      );

      return response;
    } catch (error) {
      // Remove the temporary user message and add error message
      currentRoomMessages.update(messages => {
        const filtered = messages.filter(msg => !msg.id?.startsWith('temp-'));
        return [
          ...filtered,
          {
            type: 'error',
            content: `Error: ${error.response?.data?.error || 'Failed to send message'}`,
            timestamp: new Date()
          }
        ];
      });
      throw error;
    }
  },

  async clearRoomMessages(roomId) {
    try {
      await api.clearRoomMessages(roomId);
      currentRoomMessages.set([]);

      // Reset message count
      chatRooms.update(rooms =>
        rooms.map(room => (room.id === roomId ? { ...room, message_count: 0 } : room))
      );
    } catch (error) {
      console.error('Failed to clear room messages:', error);
      throw error;
    }
  },

  toggleSidebar() {
    sidebarVisible.update(visible => !visible);
  },

  async initializeFromStorage() {
    const savedRoomId = localStorage.getItem('current_room_id');
    if (savedRoomId) {
      try {
        await this.selectRoom(savedRoomId);
      } catch (_error) {
        // Room might not exist anymore, clear storage
        localStorage.removeItem('current_room_id');
      }
    }
  }
};

// Legacy chat store for backward compatibility
export const chatHistory = writable([]);
export const chatStore = {
  addMessage(message) {
    currentRoomMessages.update(messages => [...messages, message]);
  },
  clearHistory() {
    currentRoomMessages.set([]);
  }
};

// Auth functions
export const auth = {
  async login(username, password) {
    try {
      loading.set(true);
      error.set(null);
      await api.login(username, password);
      isAuthenticated.set(true);
      return true;
    } catch (err) {
      error.set(err.response?.data?.error || 'Login failed');
      return false;
    } finally {
      loading.set(false);
    }
  },

  async register(username, password) {
    try {
      loading.set(true);
      error.set(null);
      await api.register(username, password);
      return true;
    } catch (err) {
      error.set(err.response?.data?.error || 'Registration failed');
      return false;
    } finally {
      loading.set(false);
    }
  },

  logout() {
    api.logout();
    isAuthenticated.set(false);
    user.set(null);
    chatRooms.set([]);
    currentRoom.set(null);
    currentRoomMessages.set([]);
    sidebarVisible.set(false);
    localStorage.removeItem('current_room_id');
  }
};

// Listen for auth logout events (must be after auth object is defined)
let logoutEventAdded = false;
if (typeof window !== 'undefined' && !logoutEventAdded) {
  window.addEventListener('auth:logout', event => {
    console.log('Auth logout event received:', event.detail);
    // Only process logout if currently authenticated to prevent spam
    if (api.isAuthenticated()) {
      auth.logout();
    }
  });
  logoutEventAdded = true;
}
