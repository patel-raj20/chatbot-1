"""
Authentication Schemas
=====================
Pydantic models for request validation and response serialization.

WHY: Ensure data validation and provide clear API contracts
WHERE: Used by auth routes for request/response handling
HOW: Define expected fields, types, and validation rules
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserSignup(BaseModel):
    """
    Signup Request Schema
    ====================
    Validates user registration input.
    
    FIELDS:
        username: Unique username (3-50 characters)
        password: Password (min 6 characters for basic security)
    """
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """
    Login Request Schema
    ===================
    Validates user login credentials.
    
    FIELDS:
        username: User's username
        password: User's password (will be verified against hashed password)
    """
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }


class Token(BaseModel):
    """
    Token Response Schema
    ====================
    JWT token response returned after successful login.
    
    FIELDS:
        access_token: JWT token string
        token_type: Always "bearer"
        user_id: User's UUID
        username: User's username
        role: User's role (user/admin)
    """
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "role": "user"
            }
        }


class UserResponse(BaseModel):
    """
    User Response Schema
    ===================
    Public user information (no sensitive data).
    
    FIELDS:
        id: User's UUID
        username: User's username
        role: User's role
        is_active: Whether account is active
        created_at: Account creation timestamp
    """
    id: uuid.UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "role": "user",
                "is_active": True,
                "created_at": "2024-02-09T10:30:00"
            }
        }
