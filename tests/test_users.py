import pytest
from app.schemas import UserCreate

def test_signup_user(client):
    response = client.post("/signup/", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword",
        "role": "admin"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_duplicate_signup(client):
    client.post("/signup/", json={
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "securepassword",
        "role": "admin"
    })
    response = client.post("/signup/", json={
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "securepassword",
        "role": "admin"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login(client):
    client.post("/signup/", json={
        "name": "Login Test",
        "email": "login@example.com",
        "password": "securepassword",
        "role": "user"
    })
    response = client.post("/token/", data={
        "username": "login@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
