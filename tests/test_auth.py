from app.auth import get_password_hash, verify_password, create_access_token
from app.schemas import UserCreate
from jose import jwt
from datetime import timedelta
from app.dependencies import SECRET_KEY, ALGORITHM

def test_password_hashing():
    password = "mysecurepassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)

def test_token_creation():
    data = {"sub": "test@example.com"}
    token = create_access_token(data=data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "test@example.com"
