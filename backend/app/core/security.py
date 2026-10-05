from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core.config import settings
pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
def hash_password(value: str): return pwd.hash(value)
def verify_password(value: str, hashed: str): return pwd.verify(value, hashed)
def token(subject: str, role: str, minutes: int = 30):
    return jwt.encode({"sub":subject,"role":role,"exp":datetime.now(timezone.utc)+timedelta(minutes=minutes)}, settings.secret_key, algorithm="HS256")
def decode(value: str):
    try: return jwt.decode(value, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError: raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
