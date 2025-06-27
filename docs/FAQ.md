# Frequently Asked Questions (FAQ)

## General Technical Questions

### Why use Flask instead of production servers like Gunicorn or uWSGI?
This application is designed as a proof-of-concept for demonstration purposes, prioritizing simplicity and ease of setup. For production deployment, the system includes Gunicorn configuration in the requirements.txt and is designed to run on Render.com with proper WSGI server support.

### Why weren't all columns from the original data spreadsheet included in the database model?
The database schema focuses on the most critical columns for financial analysis and querying. The included fields (posting_period, functional_area, cost_center, directorate, etc.) provide comprehensive coverage for expense analysis, anomaly detection, and root cause analysis. Additional columns can be easily integrated based on specific business requirements.

### Why doesn't user registration include email verification?
The current implementation prioritizes rapid prototyping and demonstration. For production deployment, email verification, password complexity requirements, and additional security measures would be implemented following enterprise security standards.

### Why use AI-powered intent classification instead of manual classification?
The system uses Large Language Model (LLM) intent classification to handle complex, multi-intent user queries accurately. While this approach may have slight performance overhead, it significantly improves accuracy in understanding user requests for financial analysis, especially when users ask complex questions combining multiple analysis types (EDA, anomaly detection, RCA).

### Why use PostgreSQL and MongoDB instead of reading Google Sheets directly?
This hybrid database approach optimizes for different use cases:
- **PostgreSQL**: Optimized for complex financial data aggregations, analytical queries, and high-performance data processing
- **MongoDB**: Handles user authentication, chat history, and session management with flexible document storage
- **Performance**: Database queries significantly outperform real-time spreadsheet API calls for analytical workloads

### Why not use MongoDB for all data storage?
MongoDB is not optimal for heavy financial data aggregations and analytical queries. PostgreSQL provides superior performance for:
- Complex JOIN operations across financial dimensions
- Statistical calculations and aggregations
- Time-series analysis
- Large dataset processing with proper indexing

## Architecture & Deployment

### What is the system's deployment architecture?
The system uses a cost-effective, cloud-native architecture:
- **Frontend**: Cloudflare Pages (global CDN, unlimited bandwidth)
- **Backend API**: Render.com (managed Flask hosting, 750 free hours/month)
- **PostgreSQL**: Render.com managed database (1GB storage)
- **MongoDB**: Atlas free tier (512MB cluster)

This setup provides production-grade infrastructure capabilities while remaining within free-tier limits for demonstration purposes.

### How does the system ensure security?
The application implements multiple security layers:
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Password Hashing**: bcrypt encryption for user passwords
- **CORS Protection**: Properly configured cross-origin resource sharing
- **Input Sanitization**: XSS protection with DOMPurify on frontend
- **Database Security**: Parameterized queries preventing SQL injection
- **Environment Variables**: Secure configuration management

### What technologies power the frontend?
The frontend uses modern web technologies:
- **Framework**: Svelte 4.2.7 with Vite build system
- **Styling**: Tailwind CSS for responsive design
- **Charts**: Chart.js for interactive financial visualizations
- **HTTP Client**: Axios for API communication
- **Content Processing**: Marked for markdown, KaTeX for mathematical expressions

### How scalable is the current architecture?
The current architecture supports horizontal scaling:
- **Frontend**: CDN distribution handles global traffic
- **Backend**: Stateless API design enables multiple instance deployment
- **Database**: PostgreSQL supports read replicas and connection pooling
- **Caching**: MongoDB provides fast session and chat history access

For enterprise deployment, the system can be enhanced with:
- Load balancers
- Database clustering
- Redis caching layers
- Microservice decomposition

## API & Integration

### What API endpoints are available?
The system provides comprehensive REST APIs:
- **Authentication**: Registration, login, token refresh, logout
- **EDA**: Data summaries, breakdowns, time-series analysis
- **Anomaly Detection**: Statistical, ML-based, and trend analysis
- **Visualizations**: Chart data for trends, categories, heatmaps, scatter plots
- **Chat**: AI-powered financial analysis conversations
- **Chat Rooms**: Session management and message history

### How does the AI chat system work?
The chat system integrates multiple analysis engines:
1. **Intent Classification**: LLM determines whether user wants EDA, anomaly detection, or RCA
2. **Data Processing**: Appropriate service processes financial data
3. **Response Generation**: AI generates human-readable insights and recommendations
4. **Visualization**: Charts and graphs generated for complex analysis results
5. **History**: Conversations saved in MongoDB for future reference

### What anomaly detection methods are supported?
The system offers three anomaly detection approaches:
- **Statistical**: Z-score based outlier identification (configurable threshold)
- **Machine Learning**: Isolation Forest algorithm for multi-dimensional anomalies
- **Trend-based**: Month-over-month change analysis for business anomalies
- **Comprehensive**: Combined analysis with actionable recommendations

### How is financial data structured?
The PostgreSQL database contains a comprehensive financial schema:
- **Core Fields**: Posting period, ledger, company codes, amounts
- **Organizational**: Cost centers, profit centers, directorates, functional areas
- **Temporal**: Fiscal years, posting periods with computed month_year fields
- **Descriptive**: Supplier information, transaction references, document text
- **Performance**: Optimized indexes for common analytical queries

## Data Analysis Capabilities

### What types of financial analysis are supported?
The system provides comprehensive financial analytics:
- **Exploratory Data Analysis (EDA)**: Statistical summaries, data quality metrics
- **Dimensional Breakdowns**: Analysis by any organizational or financial dimension
- **Time Series Analysis**: Trends, growth rates, seasonal patterns
- **Anomaly Detection**: Multi-method outlier identification
- **Root Cause Analysis**: Variance analysis and driver identification
- **Interactive Visualizations**: Charts, heatmaps, scatter plots, waterfall diagrams

### How accurate is the anomaly detection?
The system uses multiple detection methods for high accuracy:
- **Statistical methods** catch extreme outliers using configurable Z-score thresholds
- **Machine Learning** (Isolation Forest) identifies complex multi-dimensional patterns
- **Trend analysis** detects business-relevant month-over-month changes
- **Combined analysis** provides comprehensive coverage with reduced false positives

### Can the system handle large datasets?
Yes, the architecture is optimized for performance:
- **Database Indexing**: Strategic indexes on commonly queried fields
- **Efficient Queries**: Optimized SQL with proper aggregations
- **Pandas Processing**: Vectorized operations for data analysis
- **Chunked Processing**: Large datasets processed in manageable chunks
- **Caching**: MongoDB stores computed results for faster access

### What visualization options are available?
The system generates multiple chart types:
- **Trend Charts**: Time-series expense patterns
- **Category Breakdowns**: Pie charts for functional area distributions
- **Heatmaps**: Cost center spending patterns
- **Scatter Plots**: Anomaly visualization with normal vs. outlier points
- **Waterfall Charts**: Root cause analysis variance breakdowns



