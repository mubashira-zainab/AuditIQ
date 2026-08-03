"""
Authentication router.

Endpoints:
  POST /api/auth/register  — create account, returns JWT
  POST /api/auth/login     — verify credentials, returns JWT
  GET  /api/auth/me        — return current user from JWT
  PATCH /api/auth/profile  — update username / avatar
"""
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSessionType

from app.config import Settings, get_settings
from app.db import get_db
from app.models import User
from app.schemas import (
    ProfileUpdate, TokenResponse, UserLogin,
    UserRegister, UserResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

# ─── PASSWORD HASHING ─────────────────────────────────────────────────────────
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ─── JWT HELPERS ──────────────────────────────────────────────────────────────
security = HTTPBearer(auto_error=False)

def create_token(user_id: int, email: str, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str, settings: Settings) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )

def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username or "",
        avatar=user.avatar or "",
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


# ─── DEPENDENCY: get current user from Bearer token ───────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
    db: DBSessionType = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials, settings)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ─── REGISTER ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    body: UserRegister,
    db: DBSessionType = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    email = body.email.strip().lower()
    if not email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(
        email=email,
        username=body.username.strip() or email.split("@")[0],
        password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.email, settings)
    logger.info("Registered new user: %s", email)
    return TokenResponse(token=token, user=_user_response(user))


# ─── LOGIN ────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
def login(
    body: UserLogin,
    db: DBSessionType = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    email = body.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_token(user.id, user.email, settings)
    logger.info("Login: %s", email)
    return TokenResponse(token=token, user=_user_response(user))


# ─── ME ───────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)


# ─── PROFILE UPDATE ───────────────────────────────────────────────────────────
@router.patch("/profile", response_model=UserResponse)
def update_profile(
    body: ProfileUpdate,
    db: DBSessionType = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.username is not None:
        current_user.username = body.username.strip()
    if body.avatar is not None:
        current_user.avatar = body.avatar

    db.commit()
    db.refresh(current_user)
    logger.info("Profile updated: %s", current_user.email)
    return _user_response(current_user)
