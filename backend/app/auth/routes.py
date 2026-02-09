"""
Authentication Routes
====================
REST API endpoints for user signup and login.

ENDPOINTS:
    POST /auth/signup - Register new user account
    POST /auth/login  - Authenticate and receive JWT token

WHY: Provide authentication entry points for frontend
WHERE: Mounted in main.py under /auth prefix
HOW: Validates credentials, manages user records, generates JWT tokens

SECURITY FLOW:
    Signup:
        1. Validate username doesn't exist
        2. Hash password using bcrypt
        3. Create user with role='user' (default)
        4. Return success message
        
    Login:
        1. Find user by username
        2. Verify password against stored hash
        3. Generate JWT token with Hasura claims
        4. Return token + user info
        
NOTE ON AUTHORIZATION:
    - This module ONLY handles AUTHENTICATION (who you are)
    - AUTHORIZATION (what you can do) is handled by Hasura
    - Backend does not enforce role-based permissions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.schemas import UserSignup, UserLogin, Token, UserResponse
from app.auth.utils import hash_password, verify_password, create_access_token
from app.core.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router with /auth prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    User Signup Endpoint
    ===================
    Register a new user account.
    
    FLOW:
        1. Check if username already exists → Return 400 if exists
        2. Hash the password using bcrypt
        3. Create user record with role='user' (default)
        4. Save to database
        5. Return success message
        
    Args:
        user_data: UserSignup schema (username, password)
        db: Database session (injected)
        
    Returns:
        Success message with user info
        
    Raises:
        HTTPException 400: Username already exists
        HTTPException 500: Database error
        
    EXAMPLE REQUEST:
        POST /auth/signup
        {
            "username": "john_doe",
            "password": "securepassword123"
        }
        
    EXAMPLE RESPONSE:
        {
            "message": "User created successfully",
            "user": {
                "username": "john_doe",
                "role": "USER"
            }
        }
        
    SECURITY NOTES:
        - Password is hashed before storage (never stored in plain text)
        - Default role is 'USER' (ADMIN role must be manually assigned later)
        - Username uniqueness is enforced at database level
    """
    logger.info(f"Signup attempt for username: {user_data.username}")
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning(f"Signup failed: Username already exists - {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Hash password
    hashed_pwd = hash_password(user_data.password)
    
    # Create new user with default role='USER'
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd,
        role="USER"  # Default role (can be changed manually to 'ADMIN')
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created successfully: {new_user.username} (ID: {new_user.id})")
        
        return {
            "message": "User created successfully",
            "user": {
                "username": new_user.username,
                "role": new_user.role
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User Login Endpoint
    ==================
    Authenticate user and return JWT token.
    
    FLOW:
        1. Find user by username → Return 401 if not found
        2. Verify password → Return 401 if incorrect
        3. Check if account is active → Return 403 if inactive
        4. Generate JWT token with Hasura claims
        5. Return token + user info
        
    Args:
        credentials: UserLogin schema (username, password)
        db: Database session (injected)
        
    Returns:
        Token response with JWT and user information
        
    Raises:
        HTTPException 401: Invalid username or password
        HTTPException 403: Account is inactive
        
    EXAMPLE REQUEST:
        POST /auth/login
        {
            "username": "john_doe",
            "password": "securepassword123"
        }
        
    EXAMPLE RESPONSE:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "username": "john_doe",
            "role": "user"
        }
        
    JWT TOKEN INCLUDES:
        - sub: user_id
        - username: john_doe
        - role: user
        - exp: expiration timestamp
        - https://hasura.io/jwt/claims: {
            "x-hasura-user-id": user_id,
            "x-hasura-default-role": role,
            "x-hasura-allowed-roles": ["user", "admin"]
          }
          
    FRONTEND USAGE:
        1. Store access_token in localStorage
        2. Include in requests: Authorization: Bearer <token>
        3. Hasura validates token and enforces permissions
        4. Frontend checks role for client-side route protection
    """
    logger.info(f"Login attempt for username: {credentials.username}")
    
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid credentials for {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if account is active
    if not user.is_active:
        logger.warning(f"Login failed: Inactive account - {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Generate JWT token with Hasura claims
    access_token = create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role
    )
    
    logger.info(f"Login successful: {user.username} (Role: {user.role})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "username": user.username,
        "role": user.role
    }
