# Setup Guide - AI Business Decision & Management Platform

## Quick Start Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Edit .env and set JWT_SECRET_KEY to a strong random string
# For local development, SQLite is already configured

# Generate demo data
python scripts/generate_demo_data.py

# Run the backend
uvicorn main:app --reload
```

The backend will start on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

The frontend will start on http://localhost:5173

### 3. Access the Application

- Open http://localhost:5173 in your browser
- Login with demo account:
  - Email: demo@example.com
  - Password: demo123

## Features Implemented

### ✅ Stage 1: Project Scaffold & Authentication
- Backend structure with FastAPI
- Frontend structure with React + TypeScript
- Database models (SQLAlchemy)
- JWT authentication
- Role-based access control (Admin, Manager, Employee)
- User registration and login

### ✅ Stage 2: Business Data & CRUD APIs
- Complete database schema with 15+ tables
- RESTful APIs for:
  - Sales management
  - Customer management
  - Product & inventory management
  - Expense tracking
  - Marketing campaigns
- Synthetic demo data generator
- Business-level data isolation

### ✅ Stage 3: Frontend Pages & Charts
- Dashboard with real-time metrics
- Sales management page
- Customer management page
- Products & inventory page
- Financial analytics page
- ML models management page
- Interactive charts with Recharts
- Responsive design with Tailwind CSS

### ✅ Stage 4: ML Modules
- **Sales Prediction**: Random Forest model with time-series features
- **Churn Prediction**: Random Forest classifier with RFM features
- **Demand Forecasting**: Random Forest with rolling statistics
- **Customer Segmentation**: K-Means clustering with RFM analysis
- **Anomaly Detection**: Isolation Forest for unusual patterns
- Model persistence with Joblib
- Training metrics (MAE, RMSE, R2, precision, recall, F1, etc.)

### ✅ Stage 5: AI Features
- **AI Chatbot**: Available on every page
  - Natural language queries about business data
  - CSV file upload for analysis
  - Rule-based responses (works without LLM API)
  - LLM integration ready (OpenAI/Anthropic)
- **AI Recommendations**: Priority-based business insights
- **Reports**: Executive summaries, CSV exports
- **Alerts**: Low stock, high churn risk, anomalies

### ✅ Stage 6: Infrastructure
- Docker configuration with docker-compose
- PostgreSQL support (with SQLite fallback)
- API tests with pytest
- Comprehensive README.md
- Environment configuration
- Security best practices

## How to Use Key Features

### Training ML Models

1. Navigate to "ML Models" page
2. Click "Train Model" for any of the 5 models
3. Wait for training to complete
4. View metrics (MAE, RMSE, R2, etc.)
5. Models are saved and can be reloaded

### Using the AI Chatbot

1. Click the chat icon in the bottom-right corner (available on all pages)
2. Ask questions like:
   - "What were our total sales this month?"
   - "Which products generate the highest profit?"
   - "Which customers have high churn risk?"
   - "What products need replenishment?"
3. Upload CSV files for additional analysis
4. The AI responds with data from your business database

### Managing Business Data

- **Sales**: View, filter, and export sales transactions
- **Customers**: View customer profiles, segments, and churn risk
- **Products**: Manage inventory, view low-stock warnings
- **Analytics**: View financial trends, expense categories

### Viewing Reports

- Go to any page
- Click "Export" buttons to download CSV reports
- View dashboard metrics and trends
- Check AI insights for recommendations

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if added)
cd frontend
npm test
```

## Docker Deployment

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify .env file exists with JWT_SECRET_KEY
- Ensure Python 3.11+ is installed

### Frontend won't start
- Check if port 5173 is available
- Verify Node.js 18+ is installed
- Run `npm install` to ensure dependencies

### Database errors
- Delete business_platform.db and regenerate demo data
- Check DATABASE_URL in .env
- Ensure SQLite or PostgreSQL is accessible

### ML training fails
- Ensure sufficient data exists (30+ records for most models)
- Check that models directory exists
- Verify required dependencies are installed

## Next Steps (Optional Enhancements)

1. **LLM Integration**: Configure OPENAI_API_KEY in .env for advanced AI responses
2. **Email Notifications**: Configure SMTP settings for alert emails
3. **Scheduled Jobs**: Set up cron jobs for periodic ML retraining
4. **Real-time Updates**: Add WebSocket support for live dashboard updates
5. **Advanced Analytics**: Add more sophisticated ML models and visualizations
6. **Multi-language Support**: Add i18n for international users
7. **Mobile App**: Build React Native mobile application

## Architecture Overview

```
Frontend (React + TypeScript)
    ↓ HTTP/REST API
Backend (FastAPI + Python)
    ↓ SQLAlchemy ORM
Database (PostgreSQL/SQLite)
    ↓
ML Models (Scikit-learn, XGBoost)
    ↓
Joblib (Model Persistence)
```

## Security Notes

- JWT tokens expire after 30 minutes (configurable)
- Passwords are hashed with Argon2
- All private routes require authentication
- Business data is isolated per business
- Never commit .env file with real secrets
- Use HTTPS in production
- Configure rate limiting for production

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review API documentation at /docs
3. Check browser console for frontend errors
4. Check backend logs for API errors
5. Ensure all dependencies are installed correctly

## Project Status

All core features have been implemented:
- ✅ Authentication & Authorization
- ✅ Complete CRUD operations
- ✅ All 5 ML modules with training
- ✅ AI chatbot with data upload
- ✅ Real-time dashboard
- ✅ Reports and exports
- ✅ Docker configuration
- ✅ Comprehensive documentation

The application is fully functional and ready for use!
