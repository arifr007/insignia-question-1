# Finance Application API Documentation

This document provides comprehensive information about all the API endpoints available in the Finance Application backend system.

## Base URL
```
http://localhost:5000
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Most endpoints require a valid JWT token in the Authorization header.

### Header Format
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### 1. User Registration

**Endpoint:** `POST /register`

**Description:** Create a new user account

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (201):**
```json
{
  "message": "User created"
}
```

**Error Response (400):**
```json
{
  "error": "User already exists"
}
```

**Error Response (503):**
```json
{
  "error": "Database connection failed",
  "message": "Cannot connect to the database. Please try again later."
}
```

**Error Response (500):**
```json
{
  "error": "Internal server error"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

---

### 2. User Login

**Endpoint:** `POST /login`

**Description:** Authenticate user and receive JWT tokens

**Authentication:** Not required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

**Error Response (503):**
```json
{
  "error": "Database connection failed",
  "message": "Cannot connect to the database. Please try again later."
}
```

**Error Response (500):**
```json
{
  "error": "Internal server error"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

---

### 3. Refresh Token

**Endpoint:** `POST /refresh`

**Description:** Refresh access token using refresh token

**Authentication:** Not required (uses refresh token)

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Error Response (400):**
```json
{
  "error": "Refresh token required"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid or expired refresh token"
}
```

**Error Response (503):**
```json
{
  "error": "Database connection failed",
  "message": "Cannot connect to the database. Please try again later."
}
```

**Error Response (500):**
```json
{
  "error": "Internal server error"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

### 4. Logout

**Endpoint:** `POST /logout`

**Description:** Logout user (invalidate session)

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Basic Health Check Endpoints

### 5. Root Endpoint

**Endpoint:** `GET /`

**Description:** Basic API status check

**Authentication:** Not required

**Success Response (200):**
```json
{
  "message": "API is working",
  "status": "success",
  "timestamp": "2025-06-27T10:30:00Z",
  "version": "1.0.0"
}
```

### 6. Health Check

**Endpoint:** `GET /health-check`

**Description:** Service health status

**Authentication:** Not required

**Success Response (200):**
```json
{
  "status": "healthy",
  "message": "Service is running",
  "timestamp": "2025-06-27T10:30:00Z",
  "uptime": "Service is operational"
}
```

---

## Chat Room Management Endpoints

### 7. Get User Rooms

**Endpoint:** `GET /rooms`

**Description:** Get all chat rooms for the authenticated user

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "rooms": [
    {
      "id": "room123",
      "title": "Financial Analysis Chat",
      "created_at": "2023-12-07T10:30:00.000Z",
      "updated_at": "2023-12-07T11:45:00.000Z"
    }
  ]
}
```

**Example Request:**
```bash
curl -X GET http://localhost:5000/rooms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 8. Create Chat Room

**Endpoint:** `POST /rooms`

**Description:** Create a new chat room

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string (optional, default: 'New Chat')"
}
```

**Success Response (201):**
```json
{
  "message": "Room created successfully",
  "room": {
    "id": "room123",
    "title": "Financial Analysis Chat",
    "created_at": "2023-12-07T10:30:00.000Z",
    "updated_at": "2023-12-07T10:30:00.000Z"
  }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/rooms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Expense Analysis Room"}'
```

---

### 9. Get Chat Room Details

**Endpoint:** `GET /rooms/<room_id>`

**Description:** Get specific chat room details with messages

**Authentication:** Required

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "room": {
    "id": "room123",
    "title": "Financial Analysis Chat",
    "created_at": "2023-12-07T10:30:00.000Z",
    "updated_at": "2023-12-07T11:45:00.000Z"
  },
  "messages": [
    {
      "id": "msg456",
      "message_type": "user",
      "content": "Show me expense anomalies",
      "timestamp": "2023-12-07T10:35:00.000Z"
    },
    {
      "id": "msg457",
      "message_type": "bot",
      "content": "Here are the detected anomalies...",
      "timestamp": "2023-12-07T10:35:30.000Z",
      "intent": "anomaly_detection",
      "chart_data": {}
    }
  ]
}
```

**Error Response (404):**
```json
{
  "error": "Room not found"
}
```

---

### 10. Update Chat Room

**Endpoint:** `PUT /rooms/<room_id>`

**Description:** Update chat room title

**Authentication:** Required

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "string"
}
```

**Success Response (200):**
```json
{
  "message": "Room updated successfully"
}
```

**Error Response (400):**
```json
{
  "error": "Title is required"
}
```

**Error Response (404):**
```json
{
  "error": "Room not found or update failed"
}
```

---

### 11. Delete Chat Room

**Endpoint:** `DELETE /rooms/<room_id>`

**Description:** Delete a chat room

**Authentication:** Required

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Room deleted successfully"
}
```

**Error Response (404):**
```json
{
  "error": "Room not found or delete failed"
}
```

---

### 12. Get Room Messages

**Endpoint:** `GET /rooms/<room_id>/messages`

**Description:** Get all messages for a specific room

**Authentication:** Required

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "messages": [
    {
      "id": "msg456",
      "message_type": "user",
      "content": "Show me expense trends",
      "timestamp": "2023-12-07T10:35:00.000Z"
    },
    {
      "id": "msg457",
      "message_type": "bot",
      "content": "Here's the trend analysis...",
      "timestamp": "2023-12-07T10:35:30.000Z",
      "intent": "trend_analysis",
      "chart_data": {}
    }
  ]
}
```

**Error Response (404):**
```json
{
  "error": "Room not found"
}
```

---

### 13. Clear Room Messages

**Endpoint:** `DELETE /rooms/<room_id>/messages`

**Description:** Clear all messages from a chat room

**Authentication:** Required

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Cleared 15 messages",
  "deleted_count": 15
}
```

**Error Response (404):**
```json
{
  "error": "Room not found"
}
```

---

## Chat/AI Assistant Endpoints

### 14. Chat with AI Assistant

**Endpoint:** `POST /chat/<room_id>`

**Description:** Interact with AI assistant for expense analysis and insights within a specific room

**Authentication:** Required (JWT Token)

**Path Parameters:**
- `room_id`: The ID of the chat room

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "string"
}
```

**Success Response (200):**

For general queries:
```json
{
  "response": "AI-generated response based on your query about financial data",
  "intent": "general_inquiry",
  "query": "What are the main expense trends?"
}
```

For anomaly analysis queries:
```json
{
  "response": "Anomaly Analysis Results:\nStatistical anomalies: 25\nML anomalies: 18\nTrend anomalies: 2\n\nRecommendations:\n• Found 25 statistical outliers - investigate unusually high/low expense entries\n• ML algorithm identified 18 anomalous patterns - review for potential fraud or errors",
  "intent": "anomaly_detection",
  "query": "Show me expense anomalies"
}
```

For EDA queries:
```json
{
  "response": "Data Summary:\nTotal Records: 1,500\nTop Functional Areas by Total Spending:\nTechnology: $45,000 (35.2%)\nAdministration: $32,000 (25.1%)\nOperations: $28,000 (21.9%)\n\nAdditional Insights:\nThe data shows a steady increase in technology spending over the past quarter, with the largest spike occurring in October 2023.",
  "intent": "eda_summary",
  "query": "Give me a data overview"
}
```

For Root Cause Analysis queries:
```json
{
  "response": "Comprehensive Root Cause Analysis:\n\nBasic RCA results:\nTop drivers identified: IT Department increased by $15,000 (45% change)\n\nML insights:\nRandom Forest analysis identified cost center changes as the primary factor\n\nRecommendations:\n• Focus investigation on IT Department spending changes\n• Review technology procurement processes",
  "intent": "root_cause_analysis",
  "query": "What caused the expense increase last month?"
}
```

**Error Response (400):**
```json
{
  "error": "No message provided"
}
```

**Error Response (401):**
```json
{
  "msg": "Missing Authorization Header"
}
```

**Example Requests:**

1. **General Query:**
```bash
curl -X POST http://localhost:5000/chat/room123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main expense trends this quarter?"}'
```

2. **Anomaly Detection Query:**
```bash
curl -X POST http://localhost:5000/chat/room123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me any expense anomalies or outliers"}'
```

3. **Root Cause Analysis Query:**
```bash
curl -X POST http://localhost:5000/chat/room123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What caused the increase in expenses from September to October?"}'
```

4. **EDA Summary Query:**
```bash
curl -X POST http://localhost:5000/chat/room123 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a summary of the expense data"}'
```

---

## EDA (Exploratory Data Analysis) Endpoints

### 15. Get EDA Summary

**Endpoint:** `GET /eda`

**Description:** Retrieve comprehensive exploratory data analysis summary of finance data

**Authentication:** Required (JWT Token)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "total_rows": 1500,
  "data_quality": {
    "missing_values": {
      "amount": 0,
      "functional_area": 23
    },
    "unique_counts": {
      "cost_center_id": 45,
      "functional_area": 8
    },
    "data_completeness": {
      "amount_records": 1450,
      "zero_amount_records": 30,
      "negative_amount_records": 20
    }
  },
  "financial_summary": {
    "total_amount": 127500.50,
    "average_amount": 85.00,
    "median_amount": 67.50,
    "currency_breakdown": {
      "USD": 1200,
      "EUR": 300
    }
  },
  "organizational_breakdown": {
    "top_directorates": {
      "Technology": 45000.0,
      "Operations": 32000.0
    },
    "top_profit_centers": {
      "PC001": 25000.0,
      "PC002": 18000.0
    },
    "top_cost_centers": {
      "CC001": 15000.0,
      "CC002": 12000.0
    },
    "top_functional_areas": {
      "IT": 35000.0,
      "Admin": 22000.0
    }
  },
  "general_ledger_account_analysis": {
    "top_general_ledger_accounts": {
      "Travel Expenses": 25000.0,
      "Office Supplies": 18000.0
    },
    "general_ledger_account_types": {
      "Expense": 95000.0,
      "Asset": 32500.0
    }
  },
  "temporal_analysis": {
    "by_fiscal_year": {
      "2023": 85000.0,
      "2024": 42500.0
    },
    "recent_months": {
      "2023-10": 15800.0,
      "2023-09": 14200.0
    }
  },
  "transaction_analysis": {
    "top_transaction_types": {
      "Purchase": 45000.0,
      "Expense": 35000.0
    },
    "top_level_1": {
      "Operational": 55000.0,
      "Administrative": 40000.0
    },
    "debit_credit_split": {
      "S": 85000.0,
      "H": -12500.0
    }
  },
  "supplier_analysis": {
    "top_suppliers": {
      "Tech Corp": 15000.0,
      "Office Supply Co": 8500.0
    },
    "supplier_count": 45
  },
  "geographic_analysis": {
    "top_regions": {
      "North America": 65000.0,
      "Europe": 35000.0
    },
    "top_entities": {
      "Entity A": 45000.0,
      "Entity B": 28000.0
    }
  }
}
```

**Error Response (500):**
```json
{
  "error": "Error message"
}
```

**Example Request:**
```bash
curl -X GET http://localhost:5000/eda \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 16. Detailed Breakdown by Dimension

**Endpoint:** `GET /eda/breakdown/<dimension>`

**Description:** Get detailed breakdown analysis by specific dimension

**Authentication:** Required

**Path Parameters:**
- `dimension`: The dimension to analyze (e.g., "functional_area", "cost_center_id", "directorate")

**Query Parameters:**
- `top_n` (optional): Number of top entries to return (default: 10)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "dimension": "functional_area",
  "breakdown": {
    "Technology": {
      "amount": {
        "sum": 45000.0,
        "count": 150,
        "mean": 300.0,
        "std": 125.5
      },
      "cost_center_id": {
        "nunique": 5
      },
      "directorate": {
        "nunique": 2
      }
    }
  },
  "summary_stats": {
    "total_categories": 8,
    "total_amount": 127500.50,
    "showing_top": 10
  }
}
```

**Error Response (500):**
```json
{
  "error": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/eda/breakdown/functional_area?top_n=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 17. Time Series Analysis

**Endpoint:** `GET /eda/timeseries`

**Description:** Get time series analysis of expenses

**Authentication:** Required

**Query Parameters:**
- `group_by` (optional): Grouping method - "month_year", "fiscal_year", or "posting_period" (default: "month_year")

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "time_series": [
    {
      "month_year": "2023-01",
      "sum": 12500.0,
      "count": 150,
      "mean": 83.33,
      "growth_rate": 5.2
    },
    {
      "month_year": "2023-02",
      "sum": 13200.0,
      "count": 160,
      "mean": 82.50,
      "growth_rate": 5.6
    }
  ],
  "summary": {
    "total_periods": 12,
    "avg_growth_rate": 4.8,
    "max_amount_period": {
      "month_year": "2023-10",
      "sum": 15800.0,
      "count": 180,
      "mean": 87.78
    },
    "min_amount_period": {
      "month_year": "2023-03",
      "sum": 9200.0,
      "count": 120,
      "mean": 76.67
    }
  }
}
```

**Error Response (500):**
```json
{
  "error": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/eda/timeseries?group_by=month_year" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Anomaly Detection Endpoints

### 18. Comprehensive Anomaly Detection

**Endpoint:** `GET /anomaly/detect`

**Description:** Get comprehensive anomaly analysis using specified method

**Authentication:** Required

**Query Parameters:**
- `method` (optional): Detection method - "comprehensive", "statistical", "ml", or "trend" (default: "comprehensive")

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "method": "comprehensive",
  "parameters": {
    "method": "comprehensive"
  },
  "data": {
    "statistical_anomalies": {
      "anomalies": [
        {
          "id": 123,
          "amount": 5000.0,
          "z_score": 3.2,
          "functional_area": "Technology"
        }
      ],
      "total_anomalies": 25,
      "threshold": 2.5
    },
    "ml_anomalies": {
      "anomalies": [
        {
          "id": 456,
          "amount": 4800.0,
          "anomaly_score": -0.15,
          "cost_center": "CC001"
        }
      ],
      "total_anomalies": 18,
      "contamination": 0.05
    }
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/anomaly/detect?method=comprehensive" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 19. Statistical Anomaly Detection

**Endpoint:** `GET /anomaly/statistical`

**Description:** Get statistical anomalies using Z-score analysis

**Authentication:** Required

**Query Parameters:**
- `threshold` (optional): Z-score threshold (default: 2.5)

**Success Response (200):**
```json
{
  "status": "success",
  "method": "statistical",
  "parameters": {
    "threshold": 2.5
  },
  "data": {
    "anomalies": [
      {
        "id": 123,
        "amount": 5000.0,
        "z_score": 3.2,
        "functional_area": "Technology",
        "cost_center_id": "CC001"
      }
    ],
    "total_anomalies": 25,
    "threshold_used": 2.5,
    "summary": {
      "mean_amount": 85.0,
      "std_amount": 125.5,
      "total_records": 1500
    }
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/anomaly/statistical?threshold=3.0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 20. ML-Based Anomaly Detection

**Endpoint:** `GET /anomaly/ml`

**Description:** Get ML-based anomalies using Isolation Forest algorithm

**Authentication:** Required

**Query Parameters:**
- `contamination` (optional): Expected proportion of anomalies (default: 0.05)

**Success Response (200):**
```json
{
  "status": "success",
  "method": "ml",
  "parameters": {
    "contamination": 0.05
  },
  "data": {
    "anomalies": [
      {
        "id": 456,
        "amount": 4800.0,
        "anomaly_score": -0.15,
        "cost_center_id": "CC001",
        "functional_area": "Technology"
      }
    ],
    "total_anomalies": 18,
    "contamination_used": 0.05,
    "model_info": {
      "algorithm": "IsolationForest",
      "features_used": ["amount", "cost_center_encoded", "functional_area_encoded"]
    }
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/anomaly/ml?contamination=0.1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 21. Trend-Based Anomaly Detection

**Endpoint:** `GET /anomaly/trends`

**Description:** Get trend-based anomalies (month-over-month changes)

**Authentication:** Required

**Query Parameters:**
- `threshold_pct` (optional): Percentage change threshold (default: 30.0)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "method": "trend",
  "parameters": {
    "threshold_pct": 30.0
  },
  "data": {
    "anomalies": [
      {
        "functional_area": "Technology",
        "from_month": "2023-09",
        "to_month": "2023-10",
        "change_amount": 8000.0,
        "change_percentage": 45.2,
        "previous_amount": 17700.0,
        "current_amount": 25700.0
      }
    ],
    "total_anomalies": 3,
    "threshold_percentage": 30.0
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/anomaly/trends?threshold_pct=25.0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Visualization Endpoints

### 22. Trend Chart Data

**Endpoint:** `GET /charts/trend`

**Description:** Get trend chart data for frontend visualization

**Authentication:** Required

**Query Parameters:**
- `room_id` (optional): Room ID for chat integration

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "chart_type": "line_chart",
    "chart_data": {
      "data": [
        {
          "x": ["2023-01", "2023-02", "2023-03"],
          "y": [12500.0, 13200.0, 11800.0],
          "type": "scatter",
          "mode": "lines+markers",
          "name": "Monthly Expenses"
        }
      ],
      "layout": {
        "title": "Monthly Expense Trends",
        "xaxis": {"title": "Month"},
        "yaxis": {"title": "Amount ($)"}
      }
    },
    "summary": {
      "total_amount": 127500.50,
      "avg_monthly_amount": 10625.04,
      "trend_direction": "increasing"
    }
  },
  "saved_to_chat": false
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/charts/trend?room_id=room123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 23. Category Breakdown Chart

**Endpoint:** `GET /charts/category-breakdown`

**Description:** Get functional area breakdown pie chart data

**Authentication:** Required

**Query Parameters:**
- `room_id` (optional): Room ID for chat integration

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "chart_type": "pie_chart",
    "chart_data": {
      "data": [
        {
          "values": [45000, 32000, 28000, 15000, 7500],
          "labels": ["Technology", "Administration", "Operations", "HR", "Facilities"],
          "type": "pie",
          "name": "Functional Area Breakdown"
        }
      ],
      "layout": {
        "title": "Expense Distribution by Functional Area"
      }
    },
    "summary": {
      "total_functional_areas": 8,
      "largest_area": {"name": "Technology", "amount": 45000, "percentage": 35.2},
      "smallest_area": {"name": "Facilities", "amount": 7500, "percentage": 5.9}
    }
  },
  "saved_to_chat": false
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/charts/category-breakdown?room_id=room123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 24. Cost Center Heatmap

**Endpoint:** `GET /charts/heatmap`

**Description:** Get cost center heatmap data

**Authentication:** Required

**Query Parameters:**
- `room_id` (optional): Room ID for chat integration

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "chart_type": "heatmap",
    "chart_data": {
      "data": [
        {
          "z": [[1000, 1500, 2000], [800, 1200, 1800], [1200, 1600, 2200]],
          "x": ["CC001", "CC002", "CC003"],
          "y": ["Jan", "Feb", "Mar"],
          "type": "heatmap",
          "colorscale": "Viridis"
        }
      ],
      "layout": {
        "title": "Cost Center Spending Heatmap",
        "xaxis": {"title": "Cost Centers"},
        "yaxis": {"title": "Months"}
      }
    },
    "summary": {
      "total_cost_centers": 15,
      "highest_spending_center": {"id": "CC003", "amount": 6600},
      "lowest_spending_center": {"id": "CC001", "amount": 4500}
    }
  },
  "saved_to_chat": false
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/charts/heatmap?room_id=room123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 25. Anomaly Scatter Plot

**Endpoint:** `GET /charts/anomaly-scatter`

**Description:** Get anomaly scatter plot data

**Authentication:** Required

**Query Parameters:**
- `room_id` (optional): Room ID for chat integration
- `method` (optional): Anomaly detection method (default: "ml")

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "chart_type": "scatter_plot",
    "chart_data": {
      "data": [
        {
          "x": [1, 2, 3, 4, 5],
          "y": [100, 200, 5000, 150, 180],
          "mode": "markers",
          "type": "scatter",
          "marker": {
            "color": ["blue", "blue", "red", "blue", "blue"],
            "size": [8, 8, 12, 8, 8]
          },
          "text": ["Normal", "Normal", "Anomaly", "Normal", "Normal"],
          "name": "Expense Data"
        }
      ],
      "layout": {
        "title": "Anomaly Detection Scatter Plot",
        "xaxis": {"title": "Record Index"},
        "yaxis": {"title": "Amount ($)"}
      }
    },
    "summary": {
      "total_records": 1500,
      "anomalies_detected": 18,
      "anomaly_percentage": 1.2
    }
  },
  "saved_to_chat": false
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/charts/anomaly-scatter?method=ml&room_id=room123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 26. RCA Waterfall Chart

**Endpoint:** `POST /charts/rca-waterfall`

**Description:** Get RCA waterfall chart data

**Authentication:** Required

**Query Parameters:**
- `room_id` (optional): Room ID for chat integration

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "category": "string",
  "from_month": "string (YYYY-MM format)",
  "to_month": "string (YYYY-MM format)"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "chart_type": "waterfall",
    "chart_data": {
      "data": [
        {
          "x": ["Starting Amount", "Technology", "Operations", "HR", "Final Amount"],
          "y": [12000, 5000, -2000, 1000, 16000],
          "type": "waterfall",
          "name": "Expense Changes"
        }
      ],
      "layout": {
        "title": "Root Cause Analysis - Waterfall Chart",
        "xaxis": {"title": "Categories"},
        "yaxis": {"title": "Amount Change ($)"}
      }
    },
    "summary": {
      "total_change": 4000,
      "largest_contributor": {"category": "Technology", "change": 5000},
      "largest_reduction": {"category": "Operations", "change": -2000}
    }
  },
  "rca_analysis": {
    "basic_rca": {
      "drivers": [
        {"category": "Technology", "change": 5000, "percentage": 41.7}
      ]
    }
  },
  "saved_to_chat": false
}
```

**Error Response (400):**
```json
{
  "error": "Missing required parameters: category, from_month, to_month"
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/charts/rca-waterfall?room_id=room123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Technology",
    "from_month": "2023-09",
    "to_month": "2023-10"
  }'
```

---

### 27. Dashboard Data

**Endpoint:** `GET /dashboard`

**Description:** Get comprehensive dashboard data

**Authentication:** Required

**Query Parameters:**
- `category` (optional): Filter by specific category

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "summary_stats": {
      "total_amount": 127500.50,
      "total_records": 1500,
      "avg_amount": 85.00,
      "anomalies_count": 18
    },
    "trends": {
      "monthly_growth": 5.2,
      "largest_expense_month": "2023-10",
      "trend_direction": "increasing"
    },
    "breakdowns": {
      "by_functional_area": {
        "Technology": 45000.0,
        "Administration": 32000.0
      },
      "by_cost_center": {
        "CC001": 15000.0,
        "CC002": 12000.0
      }
    },
    "recent_anomalies": [
      {
        "id": 123,
        "amount": 5000.0,
        "detected_method": "statistical",
        "functional_area": "Technology"
      }
    ]
  }
}
```

**Error Response (500):**
```json
{
  "status": "error",
  "message": "Error message"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/dashboard?category=Technology" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 28. Available Charts

**Endpoint:** `GET /charts/available`

**Description:** Get list of available chart types and their metadata

**Authentication:** Required

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "available_charts": [
      {
        "type": "trend",
        "name": "Monthly Trend Chart",
        "description": "Line chart showing expense trends over time",
        "endpoint": "/charts/trend",
        "parameters": ["room_id (optional)"]
      },
      {
        "type": "category_breakdown",
        "name": "Category Breakdown",
        "description": "Pie chart showing expense distribution by category",
        "endpoint": "/charts/category-breakdown",
        "parameters": ["room_id (optional)"]
      },
      {
        "type": "heatmap",
        "name": "Cost Center Heatmap",
        "description": "Heatmap showing cost center spending patterns",
        "endpoint": "/charts/heatmap",
        "parameters": ["room_id (optional)"]
      },
      {
        "type": "anomaly_scatter",
        "name": "Anomaly Scatter Plot",
        "description": "Scatter plot highlighting anomalous expenses",
        "endpoint": "/charts/anomaly-scatter",
        "parameters": ["room_id (optional)", "method (optional)"]
      },
      {
        "type": "rca_waterfall",
        "name": "RCA Waterfall Chart",
        "description": "Waterfall chart showing root cause analysis",
        "endpoint": "/charts/rca-waterfall",
        "parameters": ["category", "from_month", "to_month", "room_id (optional)"]
      }
    ],
    "total_charts": 5
  }
}
```

**Example Request:**
```bash
curl -X GET http://localhost:5000/charts/available \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Chat/AI Assistant Endpoints

### 27. Chat with AI Assistant

**Endpoint:** `POST /chat`

**Description:** Interact with AI assistant for expense analysis and insights

**Authentication:** Required (JWT Token)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "string"
}
```

**Success Response (200):**

For general queries:
```json
{
  "response": "AI-generated response based on your query about financial data",
  "intent": "general_inquiry",
  "query": "What are the main expense trends?"
}
```

For anomaly analysis queries:
```json
{
  "response": "Anomaly Analysis Results:\nStatistical anomalies: 25\nML anomalies: 18\nTrend anomalies: 2\n\nRecommendations:\n• Found 25 statistical outliers - investigate unusually high/low expense entries\n• ML algorithm identified 18 anomalous patterns - review for potential fraud or errors",
  "intent": "anomaly_detection",
  "query": "Show me expense anomalies"
}
```

For EDA queries:
```json
{
  "response": "Data Summary:\nTotal Records: 1,500\nTop Functional Areas by Total Spending:\nTechnology: $45,000 (35.2%)\nAdministration: $32,000 (25.1%)\nOperations: $28,000 (21.9%)\n\nAdditional Insights:\nThe data shows a steady increase in technology spending over the past quarter, with the largest spike occurring in October 2023.",
  "intent": "eda_summary",
  "query": "Give me a data overview"
}
```

For Root Cause Analysis queries:
```json
{
  "response": "Comprehensive Root Cause Analysis:\n\nBasic RCA results:\nTop drivers identified: IT Department increased by $15,000 (45% change)\n\nML insights:\nRandom Forest analysis identified cost center changes as the primary factor\n\nRecommendations:\n• Focus investigation on IT Department spending changes\n• Review technology procurement processes",
  "intent": "root_cause_analysis",
  "query": "What caused the expense increase last month?"
}
```

**Error Response (400):**
```json
{
  "error": "No message provided"
}
```

**Error Response (401):**
```json
{
  "msg": "Missing Authorization Header"
}
```

**Example Requests:**

1. **General Query:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main expense trends this quarter?"}'
```

2. **Anomaly Detection Query:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me any expense anomalies or outliers"}'
```

3. **Root Cause Analysis Query:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "What caused the increase in expenses from September to October?"}'
```

4. **EDA Summary Query:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a summary of the expense data"}'
```

---

## Data Model

### FinanceExpense Schema

The main data model used throughout the API:

```json
{
  "id": "integer (primary key)",
  "posting": "string",
  "period": "string (YYYYMM format)",
  "company_code": "string",
  "region": "string",
  "profit_center_id": "string",
  "profit_center_name": "string",
  "cost_center_id": "string",
  "cost_center_name": "string",
  "general_ledger_account": "string",
  "general_ledger_account_name": "string",
  "functional_area": "string",
  "functional_area_name": "string",
  "account_type": "string",
  "company_code_currency_key": "string",
  "debit_credit_ind": "string",
  "company_code_currency_value": "float",
  "supplier": "string",
  "reference": "string",
  "document_header_text": "text",
  "transaction": "string",
  "level_1": "string",
  "level_7": "string",
  "directorate": "string",
  "entity": "string",
  "remapping_directorate": "string",
  "status": "string",
  "month_year": "string (computed property)"
}
```

### Key Fields Used in Analysis

- **cost_center_id, cost_center_name**: Cost center identification and name
- **functional_area, functional_area_name**: Functional area categorization
- **directorate**: High-level organizational grouping
- **company_code_currency_value**: Expense amount (main analysis field)
- **period**: Time period for trend analysis
- **general_ledger_account**: GL account classification

**Note**: The system does not use a "category" field as this was removed from the data model. Expense categorization is handled through functional_area and directorate fields.

---

## Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | Success | Request completed successfully |
| 201 | Created | User registration successful |
| 400 | Bad Request | Missing required parameters, invalid input |
| 401 | Unauthorized | Missing or invalid JWT token |
| 500 | Internal Server Error | Database connection issues, service errors |

---

## Rate Limiting

The API currently does not implement rate limiting, but it's recommended to implement reasonable request throttling in production environments.

---

## Security Considerations

1. **JWT Tokens**: Tokens should be stored securely on the client side
2. **HTTPS**: All API communication should use HTTPS in production
3. **Input Validation**: All user inputs are validated on the server side
4. **SQL Injection**: The API uses SQLAlchemy ORM to prevent SQL injection attacks

---

## Backend Service Architecture

The API is built with the following service architecture:

### Services Location: `backend/app/services/`

1. **EDA Service** (`eda_service.py`): Exploratory data analysis functionality
2. **Anomaly Service** (`anomaly_service.py`): Multiple anomaly detection methods
3. **RCA Service** (`rca_service.py`): Root cause analysis with ML capabilities
4. **Visualization Service** (`visualization_service.py`): Chart data generation

### Routes Location: `backend/app/routes/`

1. **Auth Routes** (`auth.py`): User authentication endpoints
2. **Basic Routes** (`basic.py`): Health check and root endpoints
3. **EDA Routes** (`eda.py`): Data analysis endpoints
4. **Anomaly Routes** (`anomaly.py`): Anomaly detection endpoints
5. **Visualization Routes** (`visualization.py`): Chart and visualization endpoints
6. **Chat Routes** (`chat.py`): AI assistant endpoints

All services have been moved to the backend folder structure and no longer reference non-existent "category" fields or parameters.
