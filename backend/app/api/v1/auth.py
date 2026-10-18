from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database.connection import get_db
from app.database.models import User
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "commander"
    full_name: Optional[str] = "EOC Field Commander"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    full_name: str


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    if not token:
        # For public demo access, return default commander user if unauthenticated
        result = await db.execute(select(User).filter_by(username="commander"))
        return result.scalars().first()

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    username = payload.get("sub")
    result = await db.execute(select(User).filter_by(username=username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter_by(username=form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.username, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name
    }


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).filter_by(username=data.username))
    if existing.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        full_name=data.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(subject=new_user.username, role=new_user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": new_user.username,
        "role": new_user.role,
        "full_name": new_user.full_name
    }


@router.get("/me")
async def read_current_user(user: User = Depends(get_current_user)):
    if not user:
        return {"username": "guest", "role": "observer", "full_name": "Emergency Operations Guest"}
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name
    }
