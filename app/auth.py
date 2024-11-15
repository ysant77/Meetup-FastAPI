from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    """
    Generate a JWT access token with an expiration time.

    Args:
        data (dict): The data payload to encode into the token, typically containing user information.

    Returns:
        str: The encoded JWT token as a string.
    
    The token will include an expiration time based on ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password for secure storage.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password as a string.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches a stored hashed password.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The stored hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
