# Task 14 - Create Auth Endpoints (Completed)
import hashlib
import random
import string
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, BackgroundTasks
from pyrate_limiter import Duration, Rate, Limiter
from app.rate_limiter import PatchedRateLimiter as RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, TokenResponse, TokenRefreshRequest, UserResponse, OTPVerifyRequest, OTPResendRequest
from app.email_utils import is_disposable_email, send_otp_email
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)

router = APIRouter()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# ==========================================
# Task 24 - Rate Limiting Completed
# ==========================================
# Rate limiters for auth endpoints
_register_limiter = Limiter(Rate(3, Duration.MINUTE))
_login_limiter = Limiter(Rate(5, Duration.MINUTE))
_otp_limiter = Limiter(Rate(3, Duration.MINUTE))

@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(limiter=_register_limiter))],
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email or username already registered, or invalid password length"}
    }
)
async def register(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Check for disposable email
    if is_disposable_email(user_in.email):
        raise HTTPException(status_code=400, detail="Disposable email addresses are not allowed")

    # Check if user exists
    stmt = select(User).where((User.email == user_in.email) | (User.username == user_in.username))
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Hash password with validation
    try:
        hashed_pw = hash_password(user_in.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate OTP
    otp_code = "".join(random.choices(string.digits, k=6))

    # Create new user
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=hashed_pw,
        is_verified=False,
        otp_code=otp_code,
        otp_expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send OTP in the background to avoid blocking the API response
    background_tasks.add_task(send_otp_email, new_user.email, otp_code)
    
    return new_user

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: OTPVerifyRequest, response: Response, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")
        
    if user.otp_code != request.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
        
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.otp_expires_at and user.otp_expires_at < now:
        raise HTTPException(status_code=400, detail="OTP code has expired")
        
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    user.refresh_token = hashlib.sha256(refresh_token.encode()).hexdigest()
    user.token_expires_at = now + timedelta(days=7)
    await db.commit()
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/resend-otp", dependencies=[Depends(RateLimiter(limiter=_otp_limiter))])
async def resend_otp(request: OTPResendRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return {"message": "If an account exists, a new OTP has been sent."}
        
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")
        
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Enforce 60-second cooldown on the backend
    if user.otp_expires_at and now < user.otp_expires_at - timedelta(minutes=14):
        raise HTTPException(status_code=429, detail="Please wait 60 seconds before requesting another OTP.")
        
    # Generate new OTP
    otp_code = "".join(random.choices(string.digits, k=6))
    user.otp_code = otp_code
    user.otp_expires_at = now + timedelta(minutes=15)
    
    await db.commit()
    
    # Send email in background
    background_tasks.add_task(send_otp_email, user.email, otp_code)
    
    return {"message": "If an account exists, a new OTP has been sent."}

@router.post(
    "/login", 
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(limiter=_login_limiter))],
    responses={
        200: {"description": "Successfully authenticated, tokens generated"},
        401: {"description": "Invalid email or password"},
        403: {"description": "Account is temporarily locked due to too many failed attempts"}
    }
)
async def login(response: Response, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(
        or_(User.email == user_in.username_or_email, User.username == user_in.username_or_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email first.")
    
    # Check lockout
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=403, detail="Account is temporarily locked. Try again later.")
        
    if not verify_password(user_in.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        await db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    # Reset lockout counters
    user.failed_login_attempts = 0
    user.locked_until = None
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in DB (using SHA-256 instead of bcrypt to avoid 72-byte limit)
    user.refresh_token = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.commit()
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="lax",
        max_age=7 * 24 * 60 * 60 # 7 days
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post(
    "/refresh", 
    response_model=TokenResponse,
    responses={
        200: {"description": "Tokens successfully refreshed"},
        401: {"description": "Refresh token missing, invalid, or session expired"}
    }
)
async def refresh(response: Response, refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    if hashlib.sha256(refresh_token.encode()).hexdigest() != user.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Issue new tokens (Token Rotation)
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    user.refresh_token = hashlib.sha256(new_refresh_token.encode()).hexdigest()
    await db.commit()
    
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True, 
        secure=True, 
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post(
    "/logout",
    responses={
        200: {"description": "Successfully logged out"},
        401: {"description": "Not authenticated"}
    }
)
async def logout(response: Response, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.refresh_token = None
    await db.commit()
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}

@router.get(
    "/me", 
    response_model=UserResponse,
    responses={
        200: {"description": "Current user profile retrieved"},
        401: {"description": "Not authenticated"}
    }
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
