# AI Business Decision & Management Platform

A comprehensive full-stack web application that helps businesses analyze sales, revenue, profit, customers, inventory, and expenses using machine learning for predictions and AI-powered recommendations.

## Features

### Core Functionality
- **Dashboard**: Real-time business metrics, revenue trends, sales analytics, inventory warnings
- **Sales Management**: Track sales transactions, manage orders, export reports
- **Customer Management**: Customer profiles, purchase history, RFM segmentation, churn risk analysis
- **Product & Inventory**: Product catalog, stock management, low-stock alerts, demand forecasting
- **Financial Analytics**: Revenue, costs, profit margins, expense tracking
- **AI Chatbot**: Available on every page for natural language queries about business data
- **Data Upload**: Upload CSV files for analysis and insights

### Machine Learning Models
- **Sales Prediction**: Forecast future sales using historical data
- **Customer Churn Prediction**: Identify customers at risk of leaving
- **Demand Forecasting**: Predict product demand for inventory planning
- **Customer Segmentation**: RFM-based customer clustering
- **Anomaly Detection**: Identify unusual business activities

### AI Features
- **AI Business Assistant**: Chat interface for natural language queries
- **AI Recommendations**: Prioritized actionable business insights
- **Rule-based Fallback**: Works without LLM API keys

## Technology Stack

### Frontend
- React.js with Vite
- TypeScript
- Tailwind CSS
- React Router
- Axios
- Recharts (Data visualization)
- Lucide React (Icons)
- React Hook Form + Zod (Form validation)

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (Validation)
- JWT Authentication
- Argon2 (Password hashing)
- Pandas & NumPy (Data processing)

### Database
- PostgreSQL (Production)
- SQLite (Development)

### Machine Learning
- Scikit-learn
- XGBoost
- Prophet (Time-series forecasting)
- Statsmodels
- Joblib (Model persistence)

## Project Structure

```
ai-business-decision-platform/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API clients
│   │   └── utils/         # Utilities
│   ├── package.json
│   └── vite.config.ts
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, security
│   │   ├── db/            # Database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── ml/            # ML models
│   │   └── utils/         # Utilities
│   ├── scripts/           # Demo data generator
│   ├── tests/             # Tests
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)

### Local Development

#### 1. Clone the repository
```bash
git clone <repository-url>
cd ai-business-decision-platform
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Edit .env with your configuration
# For SQLite (default):
# DATABASE_URL=sqlite:///./business_platform.db
# JWT_SECRET_KEY=your-secret-key-min-32-chars

# Generate demo data
python scripts/generate_demo_data.py

# Run the backend
uvicorn main:app --reload
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

#### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### Demo Account
- Email: demo@example.com
- Password: demo123

### Docker Setup

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up

# The application will be available at:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# PostgreSQL: localhost:5432
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=sqlite:///./business_platform.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/business_platform

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=http://localhost:5173

# LLM API (Optional - rule-based fallback if not configured)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview

# File Upload
MAX_UPLOAD_SIZE_MB=10
```

## API Documentation

The API documentation is available at `/docs` when the backend is running.

### Main Endpoints

- **Authentication**: `/api/auth`
- **Dashboard**: `/api/dashboard`
- **Sales**: `/api/sales`
- **Customers**: `/api/customers`
- **Products**: `/api/products`
- **Inventory**: `/api/inventory`
- **Expenses**: `/api/expenses`
- **Analytics**: `/api/analytics`
- **ML Models**: `/api/ml`
- **Chat**: `/api/chat`
- **Reports**: `/api/reports`
- **Alerts**: `/api/alerts`

## ML Model Training

### Train Models via API

```bash
# Sales Prediction
curl -X POST http://localhost:8000/api/ml/sales-forecast/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "sales_forecast", "algorithm": "RandomForest"}'

# Churn Prediction
curl -X POST http://localhost:8000/api/ml/churn-prediction/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "churn_model", "algorithm": "XGBoost"}'

# Demand Forecast
curl -X POST http://localhost:8000/api/ml/demand-forecast/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "demand_model", "algorithm": "Prophet"}'

# Customer Segmentation
curl -X POST http://localhost:8000/api/ml/segmentation/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "segmentation_model", "algorithm": "KMeans"}'

# Anomaly Detection
curl -X POST http://localhost:8000/api/ml/anomalies/train \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model_name": "anomaly_model", "algorithm": "IsolationForest"}'
```

## AI Chatbot Features

The AI Business Assistant is available on every page and supports:

- Natural language queries about business data
- CSV file upload for analysis
- Rule-based responses (works without LLM API)
- Questions like:
  - "What were our total sales this month?"
  - "Which products generate the highest profit?"
  - "Which customers have high churn risk?"
  - "What products need replenishment?"
  - "How is revenue changing?"

### Using the Chatbot

1. Click the chat icon in the bottom-right corner
2. Type your question in natural language
3. The AI will respond with data from your business
4. Upload CSV files for additional analysis

## Security

- JWT authentication with access tokens
- Password hashing with Argon2
- Role-based access control (Admin, Manager, Employee)
- Business-level data isolation
- CORS configuration
- SQL injection prevention
- File upload validation
- Environment variable secrets management

## Deployment

### Production Checklist

1. **Security**
   - Change JWT_SECRET_KEY to a strong random string
   - Use HTTPS
   - Configure CORS for production domain
   - Set up rate limiting
   - Enable audit logging

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Set up database backups
   - Configure connection pooling

3. **LLM Integration**
   - Configure OpenAI or Anthropic API key
   - Set up API usage monitoring
   - Implement rate limits for AI endpoints

4. **Monitoring**
   - Set up application monitoring
   - Configure error tracking
   - Monitor resource usage

### Docker Deployment

```bash
# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

### Backend Architecture
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **JWT**: Stateless authentication
- **Alembic**: Database migrations

### Frontend Architecture
- **React**: Component-based UI
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **Recharts**: Data visualization
- **Tailwind CSS**: Utility-first styling

### ML Pipeline
- **Feature Engineering**: Extract features from business data
- **Model Training**: Train models with historical data
- **Model Persistence**: Save models with Joblib
- **Prediction Generation**: Generate predictions on demand
- **Result Storage**: Store predictions in database

## Limitations

1. **ML Models**: Currently use placeholder metrics in API responses. Full implementation in Stage 4.
2. **LLM Integration**: Rule-based fallback when LLM API key not configured.
3. **Email Notifications**: Optional feature requiring SMTP configuration.
4. **Scheduled Jobs**: ML retraining requires external scheduler.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify DATABASE_URL in .env
- Ensure Python dependencies are installed

### Frontend won't start
- Check if port 5173 is available
- Verify Node.js version (18+)
- Clear node_modules and reinstall

### Database connection errors
- Verify DATABASE_URL is correct
- Check if PostgreSQL is running (if using PostgreSQL)
- Ensure database exists

### AI Chatbot not responding
- Check backend API is running
- Verify authentication token is valid
- Check browser console for errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the repository.

## Acknowledgments

- FastAPI
- React
- Scikit-learn
- Recharts
- Tailwind CSS
