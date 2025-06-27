import axios from 'axios';

// Use environment variable for API base URL, fallback to proxy for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.isRefreshing = false;
    this.failedQueue = [];

    // Add auth token to requests
    this.api.interceptors.request.use(config => {
      const token = this.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle token refresh on 401 responses
    this.api.interceptors.response.use(
      response => response,
      async error => {
        const originalRequest = error.config;

        // Handle database connection errors
        if (error.response?.status === 503) {
          const errorMessage = error.response.data?.message || 'Server is temporarily unavailable';

          // Dispatch a custom event for server errors
          window.dispatchEvent(
            new CustomEvent('server:error', {
              detail: {
                message: errorMessage,
                type: 'database_error'
              }
            })
          );

          return Promise.reject(error);
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // If we're already refreshing, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then(token => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return this.api(originalRequest);
              })
              .catch(err => {
                return Promise.reject(err);
              });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newToken = await this.refreshAccessToken();
            this.isRefreshing = false;
            this.processQueue(null, newToken);

            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            this.isRefreshing = false;
            this.processQueue(refreshError, null);
            this.handleRefreshFailure();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  processQueue(error, token = null) {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });

    this.failedQueue = [];
  }

  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/refresh`, {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: new_refresh_token } = response.data;

      this.setTokens(access_token, new_refresh_token);
      return access_token;
    } catch (error) {
      // Refresh token is invalid or expired
      this.clearTokens();
      throw error;
    }
  }

  handleRefreshFailure() {
    // Only dispatch logout event if we actually had tokens to clear
    const hadTokens = this.getAccessToken() || this.getRefreshToken();

    // Clear tokens and redirect to login
    this.clearTokens();

    // Only dispatch custom event if we were actually authenticated
    if (hadTokens && typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('auth:logout', {
          detail: { reason: 'token_expired' }
        })
      );
    }
  }

  setTokens(accessToken, refreshToken) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('chat_history');
    localStorage.removeItem('current_room_id');
  }

  getAccessToken() {
    return localStorage.getItem('access_token');
  }

  getRefreshToken() {
    return localStorage.getItem('refresh_token');
  }

  // For backward compatibility
  getToken() {
    return this.getAccessToken();
  }

  // Auth methods
  async login(username, password) {
    const response = await this.api.post('/login', { username, password });
    const { access_token, refresh_token } = response.data;

    if (access_token && refresh_token) {
      this.setTokens(access_token, refresh_token);
    }
    return response.data;
  }

  async register(username, password) {
    const response = await this.api.post('/register', { username, password });
    return response.data;
  }

  logout() {
    // Call backend logout endpoint if needed
    this.api.post('/logout').catch(() => {
      // Ignore errors on logout
    });

    this.clearTokens();
  }

  isAuthenticated() {
    return !!this.getAccessToken();
  }

  // Token utility methods
  isTokenExpired(token) {
    if (!token) return true;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch (_error) {
      return true;
    }
  }

  getTokenTimeRemaining(token) {
    if (!token) return 0;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return Math.max(0, payload.exp - currentTime);
    } catch (_error) {
      return 0;
    }
  }

  // Check if access token needs refresh (refresh if less than 2 minutes remaining)
  shouldRefreshToken() {
    const token = this.getAccessToken();
    if (!token) return false;

    const timeRemaining = this.getTokenTimeRemaining(token);
    return timeRemaining < 120; // 2 minutes
  }

  // Ensure we have a valid token (refresh if needed)
  async ensureValidToken() {
    const token = this.getAccessToken();

    if (!token) {
      throw new Error('No access token available');
    }

    if (this.isTokenExpired(token)) {
      // Token is expired, try to refresh
      return await this.refreshAccessToken();
    }

    if (this.shouldRefreshToken()) {
      // Token expires soon, refresh proactively
      try {
        return await this.refreshAccessToken();
      } catch (error) {
        // If refresh fails but current token is still valid, use it
        if (!this.isTokenExpired(token)) {
          return token;
        }
        throw error;
      }
    }

    return token;
  }

  // Chat Room methods
  async getChatRooms() {
    const response = await this.api.get('/rooms');
    return response.data;
  }

  async createChatRoom(title = 'New Chat') {
    const response = await this.api.post('/rooms', { title });
    return response.data;
  }

  async getChatRoom(roomId) {
    const response = await this.api.get(`/rooms/${roomId}`);
    return response.data;
  }

  async updateChatRoom(roomId, title) {
    const response = await this.api.put(`/rooms/${roomId}`, { title });
    return response.data;
  }

  async deleteChatRoom(roomId) {
    const response = await this.api.delete(`/rooms/${roomId}`);
    return response.data;
  }

  async getRoomMessages(roomId) {
    const response = await this.api.get(`/rooms/${roomId}/messages`);
    return response.data;
  }

  async clearRoomMessages(roomId) {
    const response = await this.api.delete(`/rooms/${roomId}/messages`);
    return response.data;
  }

  // Chat methods
  async sendMessage(roomId, message) {
    const payload = {
      message
    };
    const response = await this.api.post(`/chat/${roomId}`, payload);
    return response.data;
  }

  // EDA methods
  async getEDASummary() {
    const response = await this.api.get('/eda');
    return response.data;
  }

  async getDetailedBreakdown(dimension, topN = 10) {
    const response = await this.api.get(`/eda/breakdown/${dimension}?top_n=${topN}`);
    return response.data;
  }

  async getTimeSeries(groupBy = 'month_year') {
    const response = await this.api.get(`/eda/timeseries?group_by=${groupBy}`);
    return response.data;
  }

  async detectAnomalies(method = 'comprehensive', params = {}) {
    const query = new URLSearchParams({ method, ...params }).toString();
    const response = await this.api.get(`/anomaly/detect?${query}`);
    return response.data;
  }

  async getStatisticalAnomalies(threshold = 2.5) {
    return this.detectAnomalies('statistical', { threshold });
  }

  async getMLAnomalies(contamination = 0.1) {
    return this.detectAnomalies('ml', { contamination });
  }

  async getTrendAnomalies(threshold_pct = 30.0) {
    return this.detectAnomalies('trend', { threshold_pct });
  }

  // Visualization methods
  async getTrendChart(roomId = null) {
    const url = roomId ? `/charts/trend?room_id=${roomId}` : '/charts/trend';
    const response = await this.api.get(url);
    return response.data;
  }

  async getCategoryBreakdownChart(roomId = null) {
    const url = roomId
      ? `/charts/category-breakdown?room_id=${roomId}`
      : '/charts/category-breakdown';
    const response = await this.api.get(url);
    return response.data;
  }

  async getHeatmapChart(roomId = null) {
    const url = roomId ? `/charts/heatmap?room_id=${roomId}` : '/charts/heatmap';
    const response = await this.api.get(url);
    return response.data;
  }

  async getAnomalyScatterChart(method = 'ml', roomId = null) {
    let url = `/charts/anomaly-scatter?method=${method}`;
    if (roomId) {
      url += `&room_id=${roomId}`;
    }
    const response = await this.api.get(url);
    return response.data;
  }

  // Health check method
  async checkServerHealth() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new ApiService();
