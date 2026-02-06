"""
Authentication Routes
=====================
API endpoints for user authentication and registration.

ENDPOINTS:
    POST /auth/register - Create new user account
    POST /auth/login    - Login and get JWT token
    GET  /auth/me       - Get current user info

WHY: Provide authentication API for frontend
WHERE: Mounted in main.py as /auth route prefix  
HOW: Uses auth_service for business logic, returns JWT tokens
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.services import auth_service
from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.models import User
from app.core.logger import get_logger

logger = get_logger(__name__)

# Create router with /auth prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    WHY: Allow public user registration
    WHERE: Called from frontend registration form
    HOW:
        1. Validate email/username not already taken
        2. Create user with hashed password
        3. Default role is 'user' (not admin)
        4. Return created user info (no password)
    
    REQUEST BODY:
        {
            "email": "john@example.com",
            "username": "john_doe",
            "password": "secure123"
        }
    
    RESPONSE (201 Created):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "username": "john_doe",
            "role": "user",
            "is_active": true,
            "created_at": "2024-01-29T10:30:00"
        }
    
    ERRORS:
        400 Bad Request: Email or username already exists
        422 Unprocessable Entity: Invalid email format
        
    SECURITY:
        - Password is hashed before storage
        - All new users get 'user' role (not admin)
        - Email and username must be unique
        
    FLOW:
        1. User fills registration form → POST /auth/register
        2. Backend creates user account (role='user')
        3. User redirected to login page
        4. User logs in → receives JWT token
    """
    logger.info(f"Registration attempt: {user_data.email}")
    
    # Check if email already exists
    existing_user = auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already exists - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or login."
        )
    
    # Check if username already exists
    existing_username = auth_service.get_user_by_username(db, user_data.username)
    if existing_username:
        logger.warning(f"Registration failed: Username already exists - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken. Please choose a different username."
        )
    
    try:
        # Create new user (role='user' by default)
        new_user = auth_service.create_user(db, user_data)
        logger.info(f"User registered successfully: {new_user.email}")
        return new_user
        
    except IntegrityError as e:
        logger.error(f"Database integrity error during registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email or username may already exist."
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and receive JWT access token.
    
    WHY: Authenticate users and provide access token
    WHERE: Called from frontend login form
    HOW:
        1. Verify email and password
        2. Generate JWT token with user info + Hasura claims
        3. Return token for frontend to store
    
    REQUEST BODY:
        {
            "email": "john@example.com",
            "password": "secure123"
        }
    
    RESPONSE (200 OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    
    ERRORS:
        401 Unauthorized: Invalid email or password
        403 Forbidden: Account is deactivated
        
    TOKEN PAYLOAD:
        The JWT token contains:
        - sub: user_id
        - email: user@example.com
        - role: "user" or "admin"
        - exp: expiration timestamp
        - https://hasura.io/jwt/claims: Hasura authorization claims
        
    FRONTEND USAGE:
        1. Store token in localStorage/cookie
        2. Include in all API requests:
           Authorization: Bearer <access_token>
        3. Decode token to show user info (without verification)
        4. Remove token on logout
        
    SECURITY:
        - Credentials sent over HTTPS
        - Password verified using bcrypt constant-time comparison
        - Token expires after ACCESS_TOKEN_EXPIRE_MINUTES (default 30)
        - Token includes Hasura claims for GraphQL authorization
    """
    logger.info(f"Login attempt: {credentials.email}")
    
    # Authenticate user
    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        logger.warning(f"Login failed: Invalid credentials - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active (redundant check, but explicit)
    if not user.is_active:
        logger.warning(f"Login failed: Account deactivated - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support."
        )
    
    # Generate JWT access token with user data and Hasura claims
    access_token = create_access_token(
        data={
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value  # Convert enum to string
        }
    )
    
    logger.info(f"Login successful: {user.email} (role: {user.role})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    WHY: Frontend needs to know who is logged in
    WHERE: Called after login to get user details
    HOW: Extract user from JWT token, return user info
    
    HEADERS REQUIRED:
        Authorization: Bearer <access_token>
    
    RESPONSE (200 OK):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "username": "john_doe",
            "role": "user",
            "is_active": true,
            "created_at": "2024-01-29T10:30:00"
        }
    
    ERRORS:
        401 Unauthorized: Invalid or missing token
        403 Forbidden: Account is deactivated
        
    FRONTEND USAGE:
        // After login, get user info
        const response = await fetch('/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const user = await response.json();
        
        // Show user info in UI
        console.log(`Logged in as: ${user.username}`);
        console.log(`Role: ${user.role}`);
        
        // Check role for conditional rendering
        if (user.role === 'admin') {
            // Show admin navigation
        }
        
    USE CASES:
        - Display user info in navbar/profile
        - Check user role for UI permissions
        - Verify token is still valid
        - Refresh user data after updates
    """
    logger.debug(f"Fetching user info for: {current_user.email}")
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh JWT access token.
    
    WHY: Issue new token before old one expires
    WHERE: Called by frontend when token is about to expire
    HOW: Validate current token, issue new one with updated expiration
    
    HEADERS REQUIRED:
        Authorization: Bearer <current_access_token>
    
    RESPONSE (200 OK):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    
    ERRORS:
        401 Unauthorized: Invalid or expired token
        
    FRONTEND USAGE:
        // Before token expires, refresh it
        const newToken = await refreshToken(currentToken);
        localStorage.setItem('token', newToken.access_token);
        
    NOTE:
        This is a simple implementation. For production, consider:
        - Separate refresh tokens with longer expiration
        - Token rotation (invalidate old token)
        - Refresh token stored in httpOnly cookie
    """
    logger.info(f"Token refresh for user: {current_user.email}")
    
    # Generate new token with same user data
    new_token = create_access_token(
        data={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value
        }
    )
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }
