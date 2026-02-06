"""
Authentication Service
======================
Business logic for user authentication and registration.

WHY: Separates authentication logic from route handlers
WHERE: Called by routes/auth.py for registration and login
HOW: Handles user creation, password verification, database operations

ARCHITECTURE:
    routes/auth.py → services/auth_service.py → models.py → database
    (API layer)     (Business logic)            (ORM)       (PostgreSQL)
"""

from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.models import User, UserRole
from app.schemas import UserCreate
from app.core.security import hash_password, verify_password
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Find user by email address.
    
    WHY: Email is unique identifier for login
    WHERE: Used during login to find user account
    HOW: Database query with email filter
    
    Args:
        db: Database session
        email: User's email address
        
    Returns:
        User object if found, None if not found
        
    EXAMPLE:
        user = get_user_by_email(db, "john@example.com")
        if user:
            print(f"Found user: {user.username}")
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Find user by username.
    
    WHY: Username is unique and may be used for login in future
    WHERE: Used during registration to check for duplicates
    HOW: Database query with username filter
    
    Args:
        db: Database session
        username: User's username
        
    Returns:
        User object if found, None if not found
        
    EXAMPLE:
        user = get_user_by_username(db, "john_doe")
        if user:
            print("Username already taken")
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """
    Find user by ID.
    
    WHY: JWT tokens contain user ID, need to look up full user object
    WHERE: Used by authentication middleware to get current user
    HOW: Database query with ID filter
    
    Args:
        db: Database session
        user_id: User's UUID
        
    Returns:
        User object if found, None if not found
        
    EXAMPLE:
        user = get_user_by_id(db, UUID("abc-123..."))
        if user:
            print(f"User: {user.email}")
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user account.
    
    WHY: Handle user registration
    WHERE: Called from registration endpoint
    HOW: 
        1. Hash password
        2. Create User model instance
        3. Save to database
        4. Return created user
    
    Args:
        db: Database session
        user_data: UserCreate schema with email, username, password
        
    Returns:
        Newly created User object
        
    RAISES:
        SQLAlchemy IntegrityError: If email/username already exists
        
    SECURITY:
        - Password is hashed before storage (never store plain text)
        - Default role is 'user' (not admin)
        - Account is active by default
        
    EXAMPLE:
        user_data = UserCreate(
            email="john@example.com",
            username="john_doe",
            password="secure123"
        )
        
        user = create_user(db, user_data)
        print(f"Created user: {user.email} with role: {user.role}")
        
    VALIDATION:
        - Email format validated by Pydantic schema
        - Duplicate email/username raises IntegrityError
        - Password strength should be validated before calling this
    """
    logger.info(f"Creating new user: {user_data.email}")
    
    # Hash the password before storing
    hashed_password = hash_password(user_data.password)
    
    # Create user model instance
    # NOTE: role defaults to UserRole.USER (not admin)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=UserRole.USER,  # All new users are regular users by default
        is_active=True
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get auto-generated fields (id, created_at)
    
    logger.info(f"User created successfully: {db_user.email} (ID: {db_user.id})")
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password.
    
    WHY: Verify user credentials during login
    WHERE: Called from login endpoint
    HOW:
        1. Find user by email
        2. Verify password against stored hash
        3. Return user if valid, None if not
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password from login form
        
    Returns:
        User object if credentials are valid, None if invalid
        
    AUTHENTICATION FLOW:
        1. User submits email + password
        2. authenticate_user() verifies credentials
        3. If valid, generate JWT token
        4. If invalid, return error (wrong email or password)
        
    EXAMPLE:
        user = authenticate_user(db, "john@example.com", "secure123")
        if user:
            # Credentials valid - generate token
            token = create_access_token({"user_id": user.id, ...})
            return {"access_token": token}
        else:
            # Credentials invalid
            raise HTTPException(401, "Incorrect email or password")
            
    SECURITY:
        - Uses constant-time password comparison (prevents timing attacks)
        - Never reveals whether email or password is wrong (prevents enumeration)
        - Logs authentication attempts for security monitoring
        - Checks if account is active before allowing login
    """
    logger.debug(f"Authentication attempt for: {email}")
    
    # Find user by email
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Authentication failed: User not found - {email}")
        return None
    
    # Check if account is active
    if not user.is_active:
        logger.warning(f"Authentication failed: Account deactivated - {email}")
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password - {email}")
        return None
    
    logger.info(f"Authentication successful: {email} (role: {user.role})")
    return user


def update_user_role(db: Session, user_id: UUID, new_role: UserRole) -> Optional[User]:
    """
    Update a user's role (user or admin).
    
    WHY: Allow promoting users to admin or demoting admins to user
    WHERE: Can be called from admin management endpoints
    HOW: Find user, update role, save to database
    
    Args:
        db: Database session
        user_id: User's UUID
        new_role: New role to assign (UserRole.USER or UserRole.ADMIN)
        
    Returns:
        Updated User object if successful, None if user not found
        
    SECURITY:
        - Should only be callable by existing admins
        - Requires admin authentication in route
        - Logs all role changes for audit trail
        
    EXAMPLE:
        # Promote user to admin
        user = update_user_role(
            db,
            user_id=UUID("abc-123..."),
            new_role=UserRole.ADMIN
        )
        print(f"User {user.email} is now an admin")
        
    NOTE:
        For now, you mentioned manually updating roles in the database.
        This function is provided for future use if you want an API endpoint.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        logger.warning(f"Cannot update role: User not found - {user_id}")
        return None
    
    old_role = user.role
    user.role = new_role
    db.commit()
    db.refresh(user)
    
    logger.info(f"User role updated: {user.email} ({old_role} → {new_role})")
    return user


def deactivate_user(db: Session, user_id: UUID) -> Optional[User]:
    """
    Deactivate a user account.
    
    WHY: Disable access without deleting account (soft delete)
    WHERE: Can be called from admin management endpoints
    HOW: Set is_active to False
    
    Args:
        db: Database session
        user_id: User's UUID
        
    Returns:
        Updated User object if successful, None if user not found
        
    SECURITY:
        - Should only be callable by admins
        - Deactivated users cannot log in
        - Deactivated users' tokens become invalid
        
    EXAMPLE:
        user = deactivate_user(db, user_id=UUID("abc-123..."))
        print(f"User {user.email} has been deactivated")
    """
    user = get_user_by_id(db, user_id)
    if not user:
        logger.warning(f"Cannot deactivate: User not found - {user_id}")
        return None
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    logger.info(f"User deactivated: {user.email}")
    return user


def activate_user(db: Session, user_id: UUID) -> Optional[User]:
    """
    Reactivate a previously deactivated user account.
    
    WHY: Restore access to deactivated account
    WHERE: Can be called from admin management endpoints
    HOW: Set is_active to True
    
    Args:
        db: Database session
        user_id: User's UUID
        
    Returns:
        Updated User object if successful, None if user not found
        
    EXAMPLE:
        user = activate_user(db, user_id=UUID("abc-123..."))
        print(f"User {user.email} has been reactivated")
    """
    user = get_user_by_id(db, user_id)
    if not user:
        logger.warning(f"Cannot activate: User not found - {user_id}")
        return None
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    logger.info(f"User activated: {user.email}")
    return user
