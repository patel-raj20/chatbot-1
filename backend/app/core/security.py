"""
Security Utilities
==================
Password hashing and JWT token management.

WHY: Secure authentication requires:
     1. Hashed passwords (never store plain text)
     2. JWT tokens for stateless authentication
     3. Hasura claims for GraphQL authorization

WHERE USED: 
     - services/auth_service.py: Password hashing and verification
     - routes/auth.py: Token generation on login
     - core/auth.py: Token validation on protected routes

HOW IT WORKS:
     - Bcrypt hashes passwords with salt (one-way encryption)
     - JWT tokens contain user data, signed with SECRET_KEY
     - Hasura claims enable row-level security in GraphQL
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# ============= PASSWORD HASHING =============
# WHY: Never store passwords as plain text (security best practice)
# WHERE: Used when creating users and verifying login
# HOW: Bcrypt algorithm with automatic salt generation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    WHY: Passwords must be hashed before storing in database
    WHERE: Called during user registration
    HOW: Bcrypt generates salt automatically and produces secure hash
    
    Args:
        password: Plain text password from user
        
    Returns:
        Hashed password string (safe to store in database)
        
    EXAMPLE:
        Input:  "mypassword123"
        Output: "$2b$12$LQv3c1yqBWVH... (60 character hash)"
        
    SECURITY:
        - Each hash includes random salt (prevents rainbow table attacks)
        - Computationally expensive (slows down brute force attacks)
        - One-way function (cannot reverse hash to get password)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against stored hash.
    
    WHY: Check if user entered correct password during login
    WHERE: Called during user authentication
    HOW: Bcrypt re-hashes plain password with same salt and compares
    
    Args:
        plain_password: Password entered by user
        hashed_password: Stored hash from database
        
    Returns:
        True if password matches, False otherwise
        
    EXAMPLE:
        verify_password("mypassword123", "$2b$12$LQv3c1...")  # True
        verify_password("wrongpassword", "$2b$12$LQv3c1...")  # False
        
    SECURITY:
        - Timing-safe comparison (prevents timing attacks)
        - No information leaked about stored password
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============= JWT TOKEN MANAGEMENT =============
# WHY: Stateless authentication (no session storage needed)
# WHERE: Used for API authentication
# HOW: Encode user data into signed token, verify signature on each request


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with user data and Hasura claims.
    
    WHY: Provide secure, stateless authentication token
    WHERE: Called after successful login to generate token
    HOW: Encodes user data + expiration + Hasura claims, signs with SECRET_KEY
    
    Args:
        data: Dictionary with user information (user_id, email, role)
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string (to be sent to frontend)
        
    TOKEN STRUCTURE:
        Header:    {"alg": "HS256", "typ": "JWT"}
        Payload:   {
            "sub": "user_id",
            "email": "user@example.com", 
            "role": "user",
            "exp": 1234567890,
            "https://hasura.io/jwt/claims": {
                "x-hasura-allowed-roles": ["user"],
                "x-hasura-default-role": "user",
                "x-hasura-user-id": "user_id"
            }
        }
        Signature: HMACSHA256(header + payload, SECRET_KEY)
        
    EXAMPLE USAGE:
        token = create_access_token({
            "user_id": "abc-123",
            "email": "john@example.com",
            "role": "user"
        })
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
    SECURITY:
        - Token is signed (tampering detectable)
        - Token includes expiration (limited validity)
        - Hasura claims enable row-level security in GraphQL
    """
    to_encode = data.copy()
    
    # Set token expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Add subject (user ID) as 'sub' claim (JWT standard)
    if "user_id" in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])
    
    # ============= ADD HASURA CLAIMS =============
    # WHY: Hasura uses these claims for authorization and row-level security
    # WHERE: Hasura GraphQL validates token and extracts these claims
    # HOW: Custom claims namespace required by Hasura spec
    
    user_role = to_encode.get("role", "user")
    user_id = str(to_encode.get("user_id", ""))
    
    # Determine allowed roles based on user's role
    if user_role == "admin":
        allowed_roles = ["user", "admin"]  # Admins can access both user and admin resources
    else:
        allowed_roles = ["user"]
    
    # Add Hasura-specific claims
    # STRUCTURE: https://hasura.io/docs/latest/auth/authentication/jwt/
    to_encode["https://hasura.io/jwt/claims"] = {
        "x-hasura-allowed-roles": allowed_roles,
        "x-hasura-default-role": user_role,
        "x-hasura-user-id": user_id,
    }
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT access token.
    
    WHY: Validate token and extract user data for authorization
    WHERE: Called on every protected route to authenticate user
    HOW: Verifies signature and expiration, returns decoded payload
    
    Args:
        token: JWT token string from Authorization header
        
    Returns:
        Decoded token payload (dict) if valid, None if invalid
        
    VALIDATION CHECKS:
        1. Signature verification (token not tampered with)
        2. Expiration check (token not expired)
        3. Algorithm check (prevent algorithm confusion attacks)
        
    EXAMPLE USAGE:
        payload = decode_access_token("eyJhbGciOiJIUzI1...")
        if payload:
            user_id = payload.get("sub")
            role = payload.get("role")
            
    SECURITY:
        - Returns None for any invalid token (expired, tampered, malformed)
        - Verifies signature with SECRET_KEY
        - Protects against common JWT attacks
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid (expired, tampered, or malformed)
        return None


def create_hasura_jwt_token(user_id: str, email: str, role: str) -> str:
    """
    Create a JWT token specifically for Hasura GraphQL Engine.
    
    WHY: Hasura requires specific claim format for authorization
    WHERE: Can be used to generate tokens for direct Hasura access
    HOW: Similar to create_access_token but optimized for Hasura
    
    Args:
        user_id: User's UUID
        email: User's email  
        role: User's role (user or admin)
        
    Returns:
        JWT token with Hasura claims
        
    HASURA INTEGRATION:
        1. Frontend sends this token in Authorization header
        2. Hasura validates token signature
        3. Hasura extracts x-hasura-* claims for permissions
        4. Queries filtered by user_id automatically
        
    EXAMPLE:
        token = create_hasura_jwt_token(
            user_id="abc-123",
            email="john@example.com", 
            role="user"
        )
        # Use in GraphQL request:
        # headers = {"Authorization": f"Bearer {token}"}
    """
    return create_access_token({
        "user_id": user_id,
        "email": email,
        "role": role
    })
