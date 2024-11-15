import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base  # Import Base from database.py
from app.dependencies import get_db  # Import get_db from dependencies

# Create a test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Configure SQLAlchemy for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the dependency with a test database
def override_get_db():
    """
    Provide a new session for each test.
    
    Yields:
        Session: A SQLAlchemy Session object bound to the test database.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency with the testing session
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    """
    Fixture to set up the FastAPI TestClient with the test database.
    
    Returns:
        TestClient: An instance of the FastAPI TestClient.
    """
    Base.metadata.create_all(bind=engine)  # Create tables in the test database
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)  # Drop tables after the test session

@pytest.fixture(scope="function")
def db_session():
    # Set up a fresh database session for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

