from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

class ChatRequest(BaseModel):
    session_id: UUID
    message: str
    current_node_id: Optional[UUID] = None
    
class Option(BaseModel):
    text: str
    next_node_id: UUID

class ChatResponse(BaseModel):
    reply: str
    node_id: Optional[UUID] = None
    options: Optional[List[Option]] = None

class FAQResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    order: str
    is_active: bool

class FAQCreate(BaseModel):
    question: str
    answer: str
    order: Optional[str] = "0"
    is_active: Optional[bool] = True

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    order: Optional[str] = None
    is_active: Optional[bool] = None

# Admin schemas for node management
class NodeCreate(BaseModel):
    message_text: str
    trigger_text: Optional[str] = None
    is_entry: bool = False
    position_x: Optional[float] = 0.0
    position_y: Optional[float] = 0.0

class NodeUpdate(BaseModel):
    message_text: Optional[str] = None
    trigger_text: Optional[str] = None
    is_entry: Optional[bool] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None

class NodeResponse(BaseModel):
    id: UUID
    message_text: str
    trigger_text: Optional[str]
    is_entry: bool
    position_x: float
    position_y: float

class EdgeCreate(BaseModel):
    from_node_id: UUID
    to_node_id: UUID
    option_text: Optional[str] = None

class EdgeResponse(BaseModel):
    id: UUID
    from_node_id: UUID
    to_node_id: UUID
    option_text: Optional[str]

class NodeWithEdges(BaseModel):
    id: UUID
    message_text: str
    trigger_text: Optional[str]
    is_entry: bool
    position_x: float
    position_y: float
    outgoing_edges: List[EdgeResponse]
    incoming_edges: List[EdgeResponse]

# Admin schemas for chat history
from datetime import datetime

class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    sender: str
    message_text: str
    node_id: Optional[UUID]
    created_at: datetime

class ChatSessionSummary(BaseModel):
    session_id: UUID
    last_message_at: datetime
    message_count: int


# ============= AUTHENTICATION SCHEMAS =============
# WHY: Define request/response formats for authentication endpoints
# WHERE: Used by routes/auth.py for login, register, token endpoints
# HOW: Pydantic validates incoming data and serializes responses

class UserCreate(BaseModel):
    """
    User Registration Schema
    ========================
    Request body for creating a new user account.
    
    FIELDS:
        email: Valid email address (unique)
        username: Display name (unique, 3-50 characters)
        password: Plain text password (will be hashed, min 6 characters)
        
    VALIDATION:
        - Email format validated by EmailStr
        - Duplicate email/username rejected by database unique constraint
        - Password hashed before storage (never stored as plain text)
        
    EXAMPLE:
        {
            "email": "john@example.com",
            "username": "john_doe",
            "password": "secure123"
        }
    """
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """
    User Login Schema
    =================
    Request body for user authentication.
    
    FIELDS:
        email: User's registered email
        password: Plain text password (verified against hashed password)
        
    FLOW:
        1. User submits email + password
        2. Backend finds user by email
        3. Verify password against stored hash
        4. Return JWT token if valid
        
    EXAMPLE:
        {
            "email": "john@example.com",
            "password": "secure123"
        }
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    JWT Token Response Schema
    ==========================
    Response after successful login.
    
    FIELDS:
        access_token: JWT token for authentication
        token_type: Always "bearer" (for Authorization header)
        
    USAGE:
        Frontend stores access_token and includes it in requests:
        Authorization: Bearer <access_token>
        
    EXAMPLE:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    JWT Token Payload Schema
    =========================
    Data extracted from decoded JWT token.
    
    FIELDS:
        user_id: User's UUID (from token 'sub' claim)
        email: User's email (optional)
        role: User's role (user or admin)
        
    USAGE:
        When token is decoded, this data is available for authorization checks
        
    EXAMPLE:
        {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "role": "user"
        }
    """
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """
    User Information Response Schema
    =================================
    Response format for user data (without sensitive info).
    
    FIELDS:
        id: User's UUID
        email: User's email
        username: User's display name
        role: User's role (user or admin)
        is_active: Whether account is active
        created_at: Account creation timestamp
        
    SECURITY:
        - Never includes hashed_password
        - Safe to return to authenticated users
        
    EXAMPLE:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "john@example.com",
            "username": "john_doe",
            "role": "user",
            "is_active": true,
            "created_at": "2024-01-29T10:30:00"
        }
    """
    id: UUID
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models
