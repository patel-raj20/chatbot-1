"""
Hasura GraphQL Integration
===========================
Utilities for integrating with Hasura GraphQL Engine.

WHY: Hasura provides GraphQL API with automatic CRUD and authorization
WHERE: Used when making GraphQL queries from backend to Hasura
HOW: Includes JWT token in requests for authenticated queries

HASURA SETUP:
    Your Hasura instance should be configured with:
    - HASURA_GRAPHQL_JWT_SECRET matching SECRET_KEY
    - Permission rules using x-hasura-user-id for row-level security
    
EXAMPLE HASURA PERMISSION:
    Table: chat_messages
    Role: user
    Select permission: {"user_id": {"_eq": "X-Hasura-User-Id"}}
    (Users can only see their own messages)
"""

import requests
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.security import create_hasura_jwt_token
from app.core.logger import get_logger

logger = get_logger(__name__)


def execute_hasura_query(
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    user_role: str = "user"
) -> Dict[str, Any]:
    """
    Execute a GraphQL query against Hasura with authentication.
    
    WHY: Backend needs to make authenticated GraphQL queries to Hasura
    WHERE: Used in services that need to query/mutate data via Hasura
    HOW: 
        1. Generate JWT token with Hasura claims
        2. Include token in Authorization header
        3. Send GraphQL query to Hasura endpoint
        4. Return response data
    
    Args:
        query: GraphQL query or mutation string
        variables: Optional variables for the query
        user_id: User ID for authentication (required for user-specific queries)
        user_email: User email (optional, for logging)
        user_role: User role (user or admin)
        
    Returns:
        Dictionary containing query response data
        
    Raises:
        Exception: If Hasura returns errors or request fails
        
    EXAMPLE USAGE:
        # Query user's chat messages
        query = '''
            query GetUserChats($userId: uuid!) {
                chat_messages(where: {user_id: {_eq: $userId}}) {
                    id
                    message_text
                    sender
                    created_at
                }
            }
        '''
        
        result = execute_hasura_query(
            query=query,
            variables={"userId": "abc-123"},
            user_id="abc-123",
            user_email="john@example.com",
            user_role="user"
        )
        
        messages = result["data"]["chat_messages"]
        
    ADMIN QUERIES:
        # Admin can query all messages (no user_id filter)
        query = '''
            query GetAllChats {
                chat_messages {
                    id
                    user_id
                    message_text
                    sender
                }
            }
        '''
        
        result = execute_hasura_query(
            query=query,
            user_id="admin-123",
            user_role="admin"
        )
        
    SECURITY:
        - JWT token includes Hasura claims for authorization
        - Hasura enforces row-level security based on claims
        - Admin role can bypass user-specific filters
    """
    # Build headers with authentication
    headers = {
        "Content-Type": "application/json"
    }
    
    # If user_id provided, add JWT authentication
    if user_id:
        token = create_hasura_jwt_token(
            user_id=user_id,
            email=user_email or "",
            role=user_role
        )
        headers["Authorization"] = f"Bearer {token}"
    
    # If admin secret configured, use it (for admin-level operations)
    elif settings.HASURA_GRAPHQL_ADMIN_SECRET:
        headers["x-hasura-admin-secret"] = settings.HASURA_GRAPHQL_ADMIN_SECRET
    
    # Prepare request body
    body = {
        "query": query,
        "variables": variables or {}
    }
    
    # Execute GraphQL request
    try:
        logger.debug(f"Executing Hasura query for user: {user_id} (role: {user_role})")
        
        response = requests.post(
            settings.HASURA_GRAPHQL_URL,
            json=body,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Check for GraphQL errors
        if "errors" in result:
            logger.error(f"Hasura GraphQL errors: {result['errors']}")
            raise Exception(f"Hasura query failed: {result['errors']}")
        
        logger.debug("Hasura query executed successfully")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Hasura request failed: {e}")
        raise Exception(f"Failed to connect to Hasura: {e}")


def execute_admin_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a GraphQL query with admin privileges.
    
    WHY: Some operations need full access without user-specific filtering
    WHERE: Backend services that need to perform admin-level operations
    HOW: Uses admin secret instead of JWT token
    
    Args:
        query: GraphQL query or mutation string
        variables: Optional variables for the query
        
    Returns:
        Dictionary containing query response data
        
    NOTE: Requires HASURA_GRAPHQL_ADMIN_SECRET to be configured
    
    EXAMPLE USAGE:
        # Create admin-level mutation
        mutation = '''
            mutation CreateNode($messageText: String!) {
                insert_nodes_one(object: {message_text: $messageText}) {
                    id
                    message_text
                }
            }
        '''
        
        result = execute_admin_query(
            query=mutation,
            variables={"messageText": "Welcome!"}
        )
        
    SECURITY:
        - Only use for trusted backend operations
        - Bypasses all permission rules
        - Admin secret should never be exposed to frontend
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    if not settings.HASURA_GRAPHQL_ADMIN_SECRET:
        raise Exception("HASURA_GRAPHQL_ADMIN_SECRET not configured")
    
    headers["x-hasura-admin-secret"] = settings.HASURA_GRAPHQL_ADMIN_SECRET
    
    body = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        logger.debug("Executing Hasura admin query")
        
        response = requests.post(
            settings.HASURA_GRAPHQL_URL,
            json=body,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "errors" in result:
            logger.error(f"Hasura admin query errors: {result['errors']}")
            raise Exception(f"Hasura admin query failed: {result['errors']}")
        
        logger.debug("Hasura admin query executed successfully")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Hasura admin request failed: {e}")
        raise Exception(f"Failed to connect to Hasura: {e}")


def get_hasura_user_claims(user_id: str, user_role: str) -> Dict[str, Any]:
    """
    Generate Hasura JWT claims for a user.
    
    WHY: Frontend needs to know what claims to include in JWT
    WHERE: Can be returned to frontend for debugging/verification
    HOW: Returns the Hasura claims structure
    
    Args:
        user_id: User's UUID
        user_role: User's role (user or admin)
        
    Returns:
        Dictionary of Hasura claims
        
    EXAMPLE USAGE:
        claims = get_hasura_user_claims("abc-123", "user")
        # Returns:
        # {
        #     "x-hasura-allowed-roles": ["user"],
        #     "x-hasura-default-role": "user",
        #     "x-hasura-user-id": "abc-123"
        # }
        
    USE CASE:
        # Include in login response for frontend debugging
        return {
            "access_token": token,
            "user": user_data,
            "hasura_claims": get_hasura_user_claims(user.id, user.role)
        }
    """
    if user_role == "admin":
        allowed_roles = ["user", "admin"]
    else:
        allowed_roles = ["user"]
    
    return {
        "x-hasura-allowed-roles": allowed_roles,
        "x-hasura-default-role": user_role,
        "x-hasura-user-id": user_id
    }
