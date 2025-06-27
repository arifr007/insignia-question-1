# Finance Data Exploration & Root Cause Analysis System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![Svelte](https://img.shields.io/badge/Svelte-5.34.8-orange.svg)](https://svelte.dev/)
[![Vite](https://img.shields.io/badge/Vite-7.0.0-purple.svg)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive finance analytics platform with AI-powered insights, anomaly detection, and interactive visualizations for financial data exploration and root cause analysis.

## ✨ Features

- 🤖 **AI-Powered Chat Assistant** - Natural language queries for financial insights
- 📊 **Interactive Dashboards** - Real-time charts and visualizations
- 🔍 **Anomaly Detection** - Statistical, ML, and trend-based outlier identification
- 📈 **Exploratory Data Analysis** - Comprehensive financial data summaries
- 🔐 **Secure Authentication** - JWT-based user management
- 💬 **Chat Rooms** - Organized conversation history
- 📱 **Responsive Design** - Mobile-first UI with Tailwind CSS
- ⚡ **Modern Development** - Svelte 5, Vite 7, ESLint 9, Prettier

## 📚 Documentation

- 📖 **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete REST API reference
- 🏗️ **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** - Technical architecture and deployment
- ❓ **[FAQ](docs/FAQ.md)** - Frequently asked questions and troubleshooting

## 🛠️ System Requirements

### Backend Requirements
- **Python**: 3.10 or higher
- **PostgreSQL**: 15+ (for financial data storage)
- **MongoDB**: 6.0+ (for user sessions and chat history)

### Frontend Requirements
- **Node.js**: 18+ 
- **npm/pnpm**: Latest version
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+

## 🚀 Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd insignia-question-1
```

### 2. Database Setup

#### PostgreSQL Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE rcadb;
CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE rcadb TO postgres;
\q
```

#### MongoDB Setup
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials
```

#### Environment Configuration (.env)
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=rcadb

# MongoDB
MONGO_URI=mongodb://localhost:27017/rcadb

# JWT Secret (generate a secure key)
JWT_SECRET=your-secret-key-here

# OpenRouter API Key (for AI features)
OPENROUTER_API_KEY=your-openrouter-api-key
```

#### Database Migration
```bash
# Run database migration to load sample data
cd backend
python migrations/migrate.py
```

#### Start Backend Server
```bash
# Development mode
python run.py

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (using npm)
npm install

# Or using pnpm (recommended)
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL
```

#### Frontend Environment Configuration (.env)
```bash
VITE_API_BASE_URL=http://localhost:5000
```

#### Start Frontend Development Server
```bash
# Development mode (with hot reload)
npm run dev
# or
pnpm dev

# Lint and format code
npm run lint
npm run format

# Build for production
npm run build
# or
pnpm build

# Preview production build
npm run preview
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000 (Vite dev server)
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health-check

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Code Quality
```bash
cd frontend

# Lint JavaScript and Svelte files
npm run lint

# Fix linting issues automatically
npm run lint:fix

# Format code with Prettier
npm run format

# Check if code is properly formatted
npm run format:check
```

### API Testing
```bash
# Test API endpoints
curl http://localhost:5000/health-check
```

## 📦 Production Deployment

The system is designed for cloud deployment using free tiers:

### Frontend (Cloudflare Pages):
- ✅ **Unlimited bandwidth** and requests
- ✅ **Global CDN** with 200+ locations
- ✅ **Automatic HTTPS** and DDoS protection
- ✅ **Git integration** with auto-deployments

### Backend (Render.com):
- ✅ **750 hours/month** free tier
- ✅ **Automatic SSL** and health checks
- ✅ **PostgreSQL database** included
- ✅ **Git integration** with auto-deployments

### Databases:
- **PostgreSQL**: Render.com managed database (1GB free)
- **MongoDB**: MongoDB Atlas (512MB free tier)

### Configuration Files:
- `render.yaml` - Backend deployment configuration
- `frontend/public/_redirects` - SPA routing setup
- `frontend/public/_headers` - Security and caching headers

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 3.1.1
- **Database**: PostgreSQL (financial data) + MongoDB (sessions/chat)
- **Authentication**: JWT with Flask-JWT-Extended
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Visualizations**: Plotly, Matplotlib, Seaborn
- **AI Integration**: OpenRouter API

### Frontend
- **Framework**: Svelte 5.34.8 + Vite 7.0.0
- **Styling**: Tailwind CSS 4.1.11 with plugins
- **Charts**: Chart.js 4.5.0 with date adapters
- **HTTP Client**: Axios 1.10.0
- **Content Processing**: Marked 16.0.0, KaTeX 0.16.22, DOMPurify 3.2.6
- **Development Tools**: ESLint 9.29.0, Prettier 3.6.2

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Quick Start Checklist

- [ ] Install Python 3.10+, PostgreSQL, MongoDB
- [ ] Clone repository and install backend dependencies
- [ ] Configure `.env` files for both backend and frontend
- [ ] Run database migrations
- [ ] Start backend server (port 5000)
- [ ] Install frontend dependencies and start dev server (port 5173)
- [ ] Access application at http://localhost:5173