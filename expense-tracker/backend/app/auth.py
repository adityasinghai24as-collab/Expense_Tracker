# Task 12 - Create backend/app/auth.py (Completed)
import os
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import get_db
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Bcrypt cost factor (OWASP ASVS recommends >= 12)
BCRYPT_ROUNDS = 12

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_super_secret_key_change_in_prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def validate_password_strength(password: str) -> None:
    """Validate a password against a strong security policy.

    Enforces two layers of validation:
      1. **Length check**: Rejects passwords shorter than 12 characters
         (aligned with OWASP ASVS v4.0 §2.1.1).
      2. **Breach check**: Uses the HaveIBeenPwned Pwned Passwords API
         with a k-Anonymity model. The password is SHA-1 hashed locally,
         and only the first 5 hex characters (the prefix) are sent to the
         API. The response contains all known hash suffixes matching that
         prefix, which are compared locally — so the full password hash
         never leaves the client.

    If the HaveIBeenPwned API is unreachable (timeout, DNS failure, etc.),
    the function **fails open** — the length requirement is still enforced,
    but the breach check is silently skipped so users are not blocked.

    Args:
        password: The plaintext password to validate.

    Raises:
        ValueError: If the password is too short or has appeared in known
            data breaches.
    """
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password cannot be longer than 72 bytes.")
    
    # Check HaveIBeenPwned
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1_password[:5], sha1_password[5:]
    
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Expense-Tracker-App'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                body = response.read().decode('utf-8')
                for line in body.splitlines():
                    if line:
                        h, count = line.split(':')
                        if h == suffix:
                            raise ValueError(f"Password has been found in {count} data breaches. Please choose a different password.")
    except urllib.error.URLError:
        # If API is unreachable, we fail open rather than blocking users, 
        # but the length requirement is still enforced.
        pass


def hash_password(password: str) -> str:
    """Hash a plaintext password for secure storage.

    First validates the password against the strength policy
    (length + breach check via ``validate_password_strength``),
    then hashes it using bcrypt with a cost factor of 12. The
    resulting hash includes a randomly generated salt, so
    identical passwords produce different hashes.

    Args:
        password: The plaintext password to hash.

    Returns:
        A bcrypt hash string (e.g. ``$2b$12$...``) safe for
        storage in the database.

    Raises:
        ValueError: If the password fails strength validation.
    """
    validate_password_strength(password)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    Uses bcrypt's built-in constant-time comparison to prevent
    timing-based side-channel attacks. The salt and cost factor
    are extracted from the stored hash automatically.

    Args:
        plain_password: The plaintext password provided by the user
            during login.
        hashed_password: The bcrypt hash retrieved from the database
            (e.g. ``$2b$12$...``).

    Returns:
        ``True`` if the password matches the hash, ``False`` otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict) -> str:
    """Create a short-lived JWT access token.

    Generates a JSON Web Token intended for authenticating API
    requests. The token embeds the provided ``data`` payload
    (typically ``{"sub": user_id}``) and an ``exp`` (expiration)
    claim set to ``ACCESS_TOKEN_EXPIRE_MINUTES`` minutes from now
    (default: 15 minutes).

    The token is signed with the application ``SECRET_KEY`` using
    the configured ``ALGORITHM`` (default: HS256). It should be
    stored **in memory only** on the client (never in localStorage
    or cookies) to limit exposure to XSS attacks.

    Args:
        data: A dictionary of claims to embed in the token.
            Must include ``"sub"`` (subject / user identifier).

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token.

    Generates a JSON Web Token intended for obtaining new access
    tokens without requiring the user to re-authenticate. The
    ``exp`` claim is set to ``REFRESH_TOKEN_EXPIRE_DAYS`` days
    from now (default: 7 days).

    This token should be delivered to the client via an
    ``HttpOnly``, ``Secure``, ``SameSite=Strict`` cookie to
    prevent JavaScript access (XSS mitigation). A copy of the
    token is stored in the ``users.refresh_token`` database
    column to support server-side revocation ("logout everywhere").

    Args:
        data: A dictionary of claims to embed in the token.
            Must include ``"sub"`` (subject / user identifier).

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token.

    Validates the token's signature against the application
    ``SECRET_KEY`` and checks that the ``exp`` claim has not
    passed. If either check fails, a ``ValueError`` is raised
    with a generic message to avoid leaking token internals.

    Args:
        token: The raw JWT string (from an Authorization header
            or a cookie).

    Returns:
        The decoded payload dictionary (e.g.
        ``{"sub": "user_id", "exp": 1234567890}``).

    Raises:
        ValueError: If the token is expired, tampered with, or
            otherwise invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")


# Task 13 - Create Auth Middleware / Dependency (Completed)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user.
    
    Validates the provided JWT access token, extracts the user ID,
    and fetches the corresponding User object from the database.
    If the token is invalid, expired, or the user does not exist,
    a 401 Unauthorized exception is raised.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

class RoleChecker:
    """Dependency for Role-Based Access Control (RBAC)."""
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return user
