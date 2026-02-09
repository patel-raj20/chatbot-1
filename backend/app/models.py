"""
Database Models
===============
SQLAlchemy ORM models defining the database schema.

TABLES:
    - users: User accounts and authentication
    - nodes: Conversation nodes (bot messages)
    - edges: Connections between nodes (conversation flow)
    - chat_messages: Chat history for all sessions
    - faqs: Frequently Asked Questions
    - pdf_documents: Metadata for uploaded PDFs

WHY: Define database structure using Python classes
WHERE: Used by SQLAlchemy to create tables and query data
HOW: Each class represents a table, columns define data types
"""

from sqlalchemy import Column, Text, Boolean, ForeignKey, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base


class User(Base):
    """
    User Model
    ==========
    Stores user accounts for authentication and authorization.
    
    WHY: Enable user authentication and role-based access control
    WHERE: Used by auth routes for signup, login, and authorization
    HOW: Stores username, hashed password, and role
    
    FIELDS:
        id: Unique identifier (UUID) - used as x-hasura-user-id
        username: Unique username for login
        hashed_password: bcrypt-hashed password (never store plain text)
        role: User role (default: 'USER', can be 'ADMIN')
        is_active: Whether account is active (for future soft delete)
        created_at: Timestamp when account was created
        
    ROLES:
        - USER: Can access chatbot page only
        - ADMIN: Can access chatbot + admin pages
        
    SECURITY:
        - Passwords are hashed using bcrypt before storage
        - JWT tokens include Hasura claims with user_id and role
        - Authorization is enforced by Hasura GraphQL engine
        
    EXAMPLE:
        username="john_doe"
        hashed_password="$2b$12$..."  (bcrypt hash)
        role="USER"  (default, can be manually changed to "ADMIN")
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    role = Column(Text, default="USER", nullable=False)  # 'USER' or 'ADMIN'
    
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Node(Base):
    """
    Conversation Node Model
    =======================
    Represents a single message in the conversation tree.
    
    WHY: Nodes form the conversation flow structure
    WHERE: Queried by chat service to determine bot responses
    HOW: Connected via edges to create conversation paths
    
    FIELDS:
        id: Unique identifier (UUID)
        message_text: Bot's response text shown to user
        trigger_text: User input that triggers this node (for entry nodes)
        is_entry: Whether this is a conversation starting point
        position_x, position_y: Visual position in admin graph editor
        created_at: Timestamp when node was created
        
    EXAMPLE FLOW:
        User types "hello" → Matches node with trigger_text="hello"
        → Bot responds with message_text="Hi! How can I help?"
    """
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_text = Column(Text, nullable=False)  # Bot's response
    trigger_text = Column(Text, nullable=True)   # User input to trigger (entry nodes only)
    is_entry = Column(Boolean, default=False)    # Can start conversation here?
    position_x = Column(Float, default=0.0)      # X position in graph editor
    position_y = Column(Float, default=0.0)      # Y position in graph editor
    created_at = Column(TIMESTAMP, server_default=func.now())


class Edge(Base):
    """
    Conversation Edge Model
    =======================
    Represents a connection between two nodes (conversation flow).
    
    WHY: Defines how conversation transitions from one node to another
    WHERE: Used to determine available options for user
    HOW: Links from_node_id to to_node_id with optional option text
    
    FIELDS:
        id: Unique identifier (UUID)
        from_node_id: Source node (where user currently is)
        to_node_id: Destination node (where user goes next)
        option_text: Button text shown to user (null for automatic transitions)
        created_at: Timestamp when edge was created
        
    EDGE TYPES:
        1. Option Edge: Has option_text (user clicks button)
        2. Automatic Edge: No option_text (automatically follows to next node)
        
    EXAMPLE:
        Node A: "What do you need help with?"
        Edge 1: option_text="Technical Support" → Node B
        Edge 2: option_text="Billing" → Node C
    """
    __tablename__ = "edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    to_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    option_text = Column(Text, nullable=True)  # Button text or None for auto-transition
    created_at = Column(TIMESTAMP, server_default=func.now())


class ChatMessage(Base):
    """
    Chat Message Model
    ==================
    Stores conversation history for all chat sessions.
    
    WHY: Persist chat history for admin review and analytics
    WHERE: Saved by chat routes for every message sent
    HOW: Groups messages by session_id, tracks sender (user/bot)
    
    FIELDS:
        id: Unique identifier (UUID)
        session_id: Groups messages in same conversation
        sender: "user" or "bot"
        message_text: Content of the message
        node_id: Associated conversation node (null for FAQ/RAG responses)
        created_at: Timestamp when message was sent
        
    EXAMPLE SESSION:
        session_id=abc-123
        - Message 1: sender="user", message_text="hello"
        - Message 2: sender="bot", message_text="Hi! How can I help?"
        - Message 3: sender="user", message_text="I need support"
        - Message 4: sender="bot", message_text="What kind of support?"
    """
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)  # Groups messages together
    sender = Column(Text, nullable=False)         # "user" or "bot"
    message_text = Column(Text, nullable=False)   # Message content
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class FAQ(Base):
    """
    FAQ Model
    =========
    Stores Frequently Asked Questions and answers.
    
    WHY: Provide quick answers to common questions without conversation flow
    WHERE: Searched when user message doesn't match any conversation node
    HOW: Simple text search in question field, returns answer
    
    FIELDS:
        id: Unique identifier (UUID)
        question: FAQ question text (searchable)
        answer: FAQ answer text (returned to user)
        order: Display order (lower numbers shown first)
        is_active: Whether FAQ is currently visible
        created_at: Timestamp when FAQ was created
        
    USAGE FLOW:
        1. User sends message
        2. No matching conversation node found
        3. Search FAQs for keyword match
        4. Return FAQ answer if found
        
    EXAMPLE:
        question="What are your business hours?"
        answer="We are open Mon-Fri, 9 AM to 5 PM EST."
    """
    __tablename__ = "faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    order = Column(Text, default="0")           # Display order (string for flexibility)
    is_active = Column(Boolean, default=True)   # Active FAQs shown to users
    created_at = Column(TIMESTAMP, server_default=func.now())


class PDFDocument(Base):
    """
    PDF Document Model
    ==================
    Stores metadata for uploaded PDF documents (RAG system).
    
    WHY: Track which PDFs have been uploaded and processed
    WHERE: Created when PDF is successfully ingested into RAG system
    HOW: Links MinIO storage object with original filename and chunk count
    
    FIELDS:
        id: Unique identifier (UUID)
        original_filename: User's original PDF filename
        minio_object_name: Unique name in MinIO storage bucket
        upload_date: When PDF was uploaded
        chunk_count: Number of text chunks extracted from PDF
        
    RAG FLOW:
        1. User uploads PDF → Saved to MinIO
        2. PDF processed into text chunks → Stored in Milvus
        3. PDFDocument record created with metadata
        4. User asks question → Searches chunks in Milvus
        
    EXAMPLE:
        original_filename="company_handbook.pdf"
        minio_object_name="2024-01-29_abc123_company_handbook.pdf"
        chunk_count="45"  (PDF split into 45 searchable chunks)
    """
    __tablename__ = "pdf_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(Text, nullable=False)
    minio_object_name = Column(Text, nullable=False, unique=True)
    upload_date = Column(TIMESTAMP, server_default=func.now())
    chunk_count = Column(Text, default="0")  # Number of text chunks created
