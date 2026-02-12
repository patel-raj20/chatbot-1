"""
Authentication Utilities
=======================
JWT token creation/verification and password hashing utilities.

WHY: Centralize security functions for reuse across auth module
WHERE: Used by auth routes for signup, login, and token validation
HOW: Uses passlib for bcrypt password hashing, jose for JWT handling

SECURITY NOTES:
    - Passwords are hashed using bcrypt (slow by design to prevent brute force)
    - JWT tokens include Hasura-compatible claims for GraphQL authorization
    - Tokens expire after 7 days (configurable via ACCESS_TOKEN_EXPIRE_DAYS)
    - Secret key should be stored in environment variable for production
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# ============= PASSWORD HASHING CONFIGURATION =============
# WHY: bcrypt is industry standard for password hashing
# HOW: CryptContext handles hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============= JWT CONFIGURATION =============
# WHY: JWT tokens enable stateless authentication
# SECRET_KEY: MUST be changed in production (use env variable)
# ALGORITHM: HS256 is standard for symmetric signing
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production-use-minimum-32-characters")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    WHY: Never store passwords in plain text
    WHERE: Called during user signup
    HOW: Uses bcrypt with automatic salt generation
    
    Args:
        password: Plain text password from user
        
    Returns:
        Hashed password string (safe to store in database)
        
    EXAMPLE:
        plain = "mypassword123"
        hashed = hash_password(plain)
        # Result: "$2b$12$KIX..."
    
    NOTE: bcrypt has a 72-byte limit, so we truncate longer passwords
    """
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    WHY: Authenticate users during login
    WHERE: Called when user attempts to log in
    HOW: bcrypt handles secure comparison
    
    Args:
        plain_password: Password provided by user
        hashed_password: Hashed password from database
    
    NOTE: Truncate to 72 bytes to match hash_password behavior
        
    Returns:
        True if passwords match, False otherwise
        
    EXAMPLE:
        stored_hash = "$2b$12$KIX..."
        user_input = "mypassword123"
        is_valid = verify_password(user_input, stored_hash)  # True
    """
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password_truncated, hashed_password)


def create_access_token(
    user_id: str,
    username: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token with Hasura-compatible claims.
    
    WHY: Enable stateless authentication and Hasura authorization
    WHERE: Called after successful login
    HOW: Encodes user info + Hasura claims into JWT
    
    Args:
        user_id: User's UUID (as string)
        username: User's username
        role: User's role ('user' or 'admin')
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
        
    TOKEN STRUCTURE:
        {
            "sub": user_id,              # Standard JWT subject claim
            "username": username,         # For display purposes
            "role": role,                 # Quick role check
            "exp": expiration_timestamp,  # Token expiry
            "https://hasura.io/jwt/claims": {
                "x-hasura-user-id": user_id,
                "x-hasura-default-role": role,
                "x-hasura-allowed-roles": ["user", "admin"]
            }
        }
        
    HASURA INTEGRATION:
        - Hasura reads JWT claims to enforce GraphQL permissions
        - x-hasura-user-id: Used in permission rules (e.g., user can only see their own data)
        - x-hasura-default-role: Role used for this request
        - x-hasura-allowed-roles: All roles user can assume
        
    EXAMPLE:
        token = create_access_token("uuid-123", "john_doe", "admin")
        # Frontend stores this token and sends in Authorization header
        # Hasura validates token and enforces admin-level permissions
    """
    if expires_delta is None:
        expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    # Build JWT payload with Hasura-compatible claims
    to_encode = {
        "sub": user_id,                    # Subject: user identifier
        "username": username,               # User-friendly name
        "role": role,                       # User role for quick checks
        "exp": expire,                      # Expiration timestamp
        # Hasura-specific claims for GraphQL authorization
        "https://hasura.io/jwt/claims": {
            "x-hasura-user-id": user_id,
            "x-hasura-default-role": role,
            "x-hasura-allowed-roles": ["USER", "ADMIN"]
        }
    }
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    WHY: Validate tokens and extract user information
    WHERE: Used by authentication middleware (if needed in backend)
    HOW: Verifies signature and expiration, returns payload
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Token payload (dict) if valid, None if invalid/expired
        
    EXAMPLE:
        token = "eyJhbGciOiJIUzI1NiIs..."
        payload = decode_access_token(token)
        # Result: {"sub": "uuid-123", "username": "john_doe", ...}
        
    NOTE:
        This function is optional in our architecture since Hasura
        handles token verification for GraphQL requests.
        Useful if backend REST endpoints need to verify tokens directly.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extract and validate JWT token from Authorization header.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        Token payload dict
        
    Raises:
        HTTPException 401: Invalid or expired token
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Require admin role for endpoint access.
    
    Raises:
        HTTPException 401: Invalid token
        HTTPException 403: User is not admin
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    if payload.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return payload
