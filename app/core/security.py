import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(sub: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": datetime.now(timezone.utc) + expires_delta}

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
