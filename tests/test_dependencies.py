from app.auth import create_access_token
from app.dependencies import get_current_user
from fastapi import HTTPException
from jose import jwt
import pytest

def test_get_current_user_with_valid_token(client, db_session):
    # Register a test user and log in to get a valid token
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword",
        "role": "user"
    }
    client.post("/signup/", json=user_data)
    response = client.post("/token/", data={"username": "test@example.com", "password": "securepassword"})
    token = response.json().get("access_token")

    # Retrieve the current user with the valid token
    user = get_current_user(db=db_session, token=token)
    assert user.email == "test@example.com"


def test_get_current_user_with_invalid_token(db_session):
    invalid_token = "invalidtoken"
    with pytest.raises(HTTPException):
        get_current_user(db=db_session, token=invalid_token)
