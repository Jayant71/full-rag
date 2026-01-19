from git import Optional
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from app.core.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALOGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALOGORITHM])
        return payload
    except PyJWTError:
        return None
