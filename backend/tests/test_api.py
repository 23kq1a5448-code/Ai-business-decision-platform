"""
Basic API tests for the Business Platform.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def setup_database():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Business Decision & Management Platform" in response.json()["message"]


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register(setup_database):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "test12345",
            "role": "employee"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login(setup_database):
    """Test user login."""
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "test12345",
            "role": "employee"
        }
    )

    # Then login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "test12345"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_protected_route_without_auth(setup_database):
    """Test that protected routes require authentication."""
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 401


def test_protected_route_with_auth(setup_database):
    """Test protected route with authentication."""
    # Register and login
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "test12345",
            "role": "employee"
        }
    )
    token = register_response.json()["access_token"]

    # Access protected route
    response = client.get(
        "/api/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
