from sqlalchemy import Column, Text, Boolean, ForeignKey, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_text = Column(Text, nullable=False)
    trigger_text = Column(Text, nullable=True)
    is_entry = Column(Boolean, default=False)
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Edge(Base):
    __tablename__ = "edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    to_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    option_text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    sender = Column(Text, nullable=False)
    message_text = Column(Text, nullable=False)
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    order = Column(Text, default="0")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class PDFDocument(Base):
    __tablename__ = "pdf_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(Text, nullable=False)
    minio_object_name = Column(Text, nullable=False, unique=True)
    upload_date = Column(TIMESTAMP, server_default=func.now())
    chunk_count = Column(Text, default="0")
