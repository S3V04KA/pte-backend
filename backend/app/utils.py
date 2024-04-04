from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
import os

from app.DB import get_user

# Секретный ключ для создания JWT токена
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not await verify_password(password, user.hashed_password):
        return False
    return user

async def get_password_hash(password):
    return pwd_context.hash(password)

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

