from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import User, get_db

from app.config import settings

# ── Config ──────────────────────────────────────────────────────────────────
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# ── Password Hashing ─────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Helpers ──────────────────────────────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user(db, email)
    if user is None:
        raise credentials_exception
    return user

async def register_user(db: AsyncSession, email: str, password: str, full_name: str):
    existing_user = await get_user(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    db_user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        is_active=True,
        plan="Free",
        verifications_used=0,
        verifications_limit=100
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
