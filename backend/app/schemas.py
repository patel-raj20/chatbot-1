from pydantic import BaseModel
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

class WorkflowQuestionResponse(BaseModel):
    id: UUID
    trigger_text: str
    message_text: str

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
