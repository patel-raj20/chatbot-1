"""
Authentication Dependencies
===========================
FastAPI dependencies for user authentication and authorization.

WHY: Provides reusable dependencies to protect routes
WHERE: Added to route functions via Depends()
HOW: Extracts JWT token, validates it, returns current user

USAGE EXAMPLES:
    # Require any authenticated user:
    @app.get("/profile")
    async def get_profile(current_user: User = Depends(get_current_user)):
        return {"user": current_user}
    
    # Require admin user:
    @app.delete("/users/{user_id}")
    async def delete_user(admin: User = Depends(require_admin)):
        # Only admins can access this
        pass
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import User, UserRole
from app.core.security import decode_access_token
from app.core.logger import get_logger

logger = get_logger(__name__)

# ============= HTTP BEARER AUTHENTICATION =============
# WHY: Extract JWT token from Authorization header
# WHERE: Used as dependency in protected routes
# HOW: Looks for "Authorization: Bearer <token>" header

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get currently authenticated user from JWT token.
    
    WHY: Verify user identity on protected routes
    WHERE: Used as dependency in routes that require authentication
    HOW: 
        1. Extract token from Authorization header
        2. Decode and verify token signature
        3. Look up user in database
        4. Return user if valid, raise 401 if not
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object for authenticated user
        
    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user account is deactivated
        
    TOKEN FORMAT:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
    EXAMPLE USAGE:
        @router.get("/me")
        async def read_users_me(current_user: User = Depends(get_current_user)):
            return {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            }
            
    SECURITY:
        - Validates token signature (prevents tampering)
        - Checks token expiration
        - Verifies user exists and is active
        - Returns 401 for any authentication failure
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Decode and verify JWT token
        payload = decode_access_token(token)
        if payload is None:
            logger.warning("Invalid token provided")
            raise credentials_exception
        
        # Extract user ID from token payload
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.warning(f"Invalid UUID in token: {user_id_str}")
            raise credentials_exception
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise credentials_exception
    
    # Look up user in database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise credentials_exception
    
    # Check if user account is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    logger.debug(f"User authenticated: {user.email} (role: {user.role})")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify account is active.
    
    WHY: Extra layer to ensure only active users can access resources
    WHERE: Can be used instead of get_current_user for stricter checks
    HOW: Relies on get_current_user, adds additional active check
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object if account is active
        
    Raises:
        HTTPException 403: If user account is deactivated
        
    NOTE: get_current_user already checks is_active, so this is redundant
          but provided for explicit clarity in route definitions
          
    EXAMPLE USAGE:
        @router.post("/important-action")
        async def important_action(user: User = Depends(get_current_active_user)):
            # Only active users can perform this action
            pass
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to have admin role.
    
    WHY: Restrict certain routes to administrators only
    WHERE: Used on admin panel routes and privileged operations
    HOW: Checks if current user's role is 'admin'
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object if user is admin
        
    Raises:
        HTTPException 403: If user is not an admin
        
    ACCESS CONTROL:
        - role='admin': Access granted
        - role='user': Access denied (403 Forbidden)
        
    EXAMPLE USAGE:
        @router.get("/admin/users")
        async def list_all_users(admin: User = Depends(require_admin)):
            # Only admins can see all users
            return db.query(User).all()
            
        @router.delete("/admin/nodes/{node_id}")
        async def delete_node(
            node_id: UUID,
            admin: User = Depends(require_admin),
            db: Session = Depends(get_db)
        ):
            # Only admins can delete nodes
            pass
            
    SECURITY:
        - First authenticates user (via get_current_user)
        - Then checks role authorization
        - Returns clear error message for non-admins
    """
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"Non-admin user attempted admin access: {current_user.email} "
            f"(role: {current_user.role})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You do not have permission to access this resource."
        )
    
    logger.debug(f"Admin access granted: {current_user.email}")
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None if not.
    
    WHY: Some routes should work for both authenticated and anonymous users
    WHERE: Routes that have optional authentication (e.g., public content with personalization)
    HOW: Same as get_current_user but doesn't raise exception if no token
    
    Args:
        credentials: Optional HTTP Bearer token
        db: Database session
        
    Returns:
        User object if authenticated, None if not authenticated
        
    DOES NOT RAISE: Returns None instead of raising 401 for missing/invalid tokens
    
    EXAMPLE USAGE:
        @router.get("/content")
        async def get_content(user: Optional[User] = Depends(get_optional_user)):
            if user:
                # Return personalized content
                return {"message": f"Hello, {user.username}!"}
            else:
                # Return public content
                return {"message": "Hello, guest!"}
                
    USE CASES:
        - Public endpoints with optional personalization
        - Content accessible to both logged-in and anonymous users
        - Analytics tracking for authenticated users
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
        
    except Exception as e:
        logger.debug(f"Optional auth failed (expected): {e}")
    
    return None
