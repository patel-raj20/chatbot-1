"""
Admin Routes
============
Administrative API endpoints for managing conversation flow and viewing analytics.

ENDPOINTS:
    Nodes:
        GET    /admin/nodes              - Get all conversation nodes
        GET    /admin/nodes/{node_id}    - Get specific node with edges
        POST   /admin/nodes              - Create new node
        PUT    /admin/nodes/{node_id}    - Update node
        DELETE /admin/nodes/{node_id}    - Delete node
        
    Edges:
        GET    /admin/edges              - Get all edges (connections)
        POST   /admin/edges              - Create new edge
        DELETE /admin/edges/{edge_id}    - Delete edge
        
    FAQs:
        GET    /admin/faqs               - Get all FAQs (including inactive)
        POST   /admin/faqs               - Create new FAQ
        PUT    /admin/faqs/{faq_id}      - Update FAQ
        DELETE /admin/faqs/{faq_id}      - Delete FAQ
        
    Chat History:
        GET    /admin/chat/sessions              - Get all chat sessions
        GET    /admin/chat/sessions/{session_id} - Get messages in a session

WHY: Admins need tools to manage conversation flows and monitor usage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.database import get_db
from app.models import Node, Edge, FAQ, ChatMessage, User
from app.schemas import (
    NodeCreate, NodeUpdate, NodeResponse, NodeWithEdges,
    EdgeCreate, EdgeResponse,
    FAQResponse, FAQCreate, FAQUpdate,
    ChatSessionSummary, ChatMessageResponse
)
from app.services.faq_service import get_all_faqs, create_faq, update_faq, delete_faq
from app.core.auth import require_admin
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ============= NODE MANAGEMENT =============

@router.get("/nodes", response_model=list[NodeWithEdges])
def get_all_nodes(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get all conversation nodes with their edges for admin visualization.
    
    WHY: Admins need to see the entire conversation flow graph
    WHERE: Called by admin panel to display conversation tree
    HOW: Queries all nodes and their incoming/outgoing edges
    
    Returns:
        List of nodes with complete edge information
    """
    logger.debug("Fetching all nodes with edges")
    nodes = db.query(Node).all()
    result = []
    
    for node in nodes:
        # Get all edges connected to this node
        outgoing = db.query(Edge).filter(Edge.from_node_id == node.id).all()
        incoming = db.query(Edge).filter(Edge.to_node_id == node.id).all()
        
        result.append(NodeWithEdges(
            id=node.id,
            message_text=node.message_text,
            trigger_text=node.trigger_text,
            is_entry=node.is_entry,
            position_x=node.position_x,
            position_y=node.position_y,
            outgoing_edges=[
                EdgeResponse(
                    id=e.id,
                    from_node_id=e.from_node_id,
                    to_node_id=e.to_node_id,
                    option_text=e.option_text
                ) for e in outgoing
            ],
            incoming_edges=[
                EdgeResponse(
                    id=e.id,
                    from_node_id=e.from_node_id,
                    to_node_id=e.to_node_id,
                    option_text=e.option_text
                ) for e in incoming
            ]
        ))
    
    logger.info(f"Returning {len(result)} nodes")
    return result


@router.get("/nodes/{node_id}", response_model=NodeWithEdges)
def get_node(node_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get a specific conversation node with its edges.
    
    WHY: View detailed information about a single node
    WHERE: Called when admin clicks on a node in the graph
    HOW: Queries node and its edges from database
    
    Args:
        node_id: Node unique identifier
        
    Returns:
        Node with edge information
        
    Raises:
        HTTPException: 404 if node not found
    """
    logger.debug(f"Fetching node {node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        logger.warning(f"Node {node_id} not found")
        raise HTTPException(404, "Node not found")
    
    outgoing = db.query(Edge).filter(Edge.from_node_id == node.id).all()
    incoming = db.query(Edge).filter(Edge.to_node_id == node.id).all()
    
    return NodeWithEdges(
        id=node.id,
        message_text=node.message_text,
        trigger_text=node.trigger_text,
        is_entry=node.is_entry,
        position_x=node.position_x,
        position_y=node.position_y,
        outgoing_edges=[
            EdgeResponse(
                id=e.id,
                from_node_id=e.from_node_id,
                to_node_id=e.to_node_id,
                option_text=e.option_text
            ) for e in outgoing
        ],
        incoming_edges=[
            EdgeResponse(
                id=e.id,
                from_node_id=e.from_node_id,
                to_node_id=e.to_node_id,
                option_text=e.option_text
            ) for e in incoming
        ]
    )


@router.post("/nodes", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Create a new conversation node.
    
    WHY: Admins need to build conversation flows
    WHERE: Called when admin adds a node in the graph editor
    HOW: Creates new Node record in database
    
    Args:
        node: Node data (message_text, trigger_text, is_entry, position)
        
    Returns:
        Created node
    """
    logger.info(f"Creating new node: '{node.message_text}'")
    new_node = Node(
        id=uuid.uuid4(),
        message_text=node.message_text,
        trigger_text=node.trigger_text,
        is_entry=node.is_entry,
        position_x=node.position_x,
        position_y=node.position_y
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    
    logger.info(f"Created node {new_node.id}")
    return new_node


@router.put("/nodes/{node_id}", response_model=NodeResponse)
def update_node(node_id: str, node_update: NodeUpdate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Update an existing conversation node.
    
    WHY: Admins need to modify conversation content
    WHERE: Called when admin edits a node
    HOW: Updates specified fields in database
    
    Args:
        node_id: Node to update
        node_update: Fields to update (only provided fields are changed)
        
    Returns:
        Updated node
        
    Raises:
        HTTPException: 404 if node not found
    """
    logger.debug(f"Updating node {node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        logger.warning(f"Node {node_id} not found for update")
        raise HTTPException(404, "Node not found")
    
    # Update only provided fields
    if node_update.message_text is not None:
        node.message_text = node_update.message_text
    if node_update.trigger_text is not None:
        node.trigger_text = node_update.trigger_text
    if node_update.is_entry is not None:
        node.is_entry = node_update.is_entry
    if node_update.position_x is not None:
        node.position_x = node_update.position_x
    if node_update.position_y is not None:
        node.position_y = node_update.position_y
    
    db.commit()
    db.refresh(node)
    
    logger.info(f"Updated node {node_id}")
    return node


@router.delete("/nodes/{node_id}")
def delete_node(node_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Delete a conversation node and cleanup related data.
    
    WHY: Remove unwanted nodes from conversation flow
    WHERE: Called when admin deletes a node
    HOW: Deletes node and cascades to edges and chat messages
    
    IMPORTANT: This also deletes:
        - All edges connected to this node
        - All chat messages that reference this node
    
    Args:
        node_id: Node to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if node not found
    """
    logger.info(f"Deleting node {node_id}")
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        logger.warning(f"Node {node_id} not found for deletion")
        raise HTTPException(404, "Node not found")
    
    # Delete related chat messages
    messages_deleted = db.query(ChatMessage).filter(
        ChatMessage.node_id == node_id
    ).delete()
    logger.debug(f"Deleted {messages_deleted} chat messages")
    
    # Delete connected edges
    edges_deleted = db.query(Edge).filter(
        (Edge.from_node_id == node_id) | (Edge.to_node_id == node_id)
    ).delete()
    logger.debug(f"Deleted {edges_deleted} edges")
    
    # Delete node
    db.delete(node)
    db.commit()
    
    logger.info(f"Successfully deleted node {node_id}")
    return {"message": "Node deleted successfully"}


# ============= EDGE MANAGEMENT =============

@router.get("/edges", response_model=list[EdgeResponse])
def get_all_edges(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get all edges (connections between nodes).
    
    WHY: View all connections in the conversation flow
    WHERE: Called by admin panel for graph visualization
    HOW: Queries all edges from database
    
    Returns:
        List of all edges
    """
    logger.debug("Fetching all edges")
    edges = db.query(Edge).all()
    logger.info(f"Returning {len(edges)} edges")
    return edges


@router.post("/edges", response_model=EdgeResponse)
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Create a new edge (connection between two nodes).
    
    WHY: Connect nodes to create conversation flow
    WHERE: Called when admin draws a connection in graph editor
    HOW: Creates new Edge record after validating both nodes exist
    
    Args:
        edge: Edge data (from_node_id, to_node_id, option_text)
        
    Returns:
        Created edge
        
    Raises:
        HTTPException: 404 if either node doesn't exist
    """
    logger.info(f"Creating edge from {edge.from_node_id} to {edge.to_node_id}")
    
    # Verify both nodes exist
    from_node = db.query(Node).filter(Node.id == edge.from_node_id).first()
    to_node = db.query(Node).filter(Node.id == edge.to_node_id).first()
    
    if not from_node or not to_node:
        logger.warning("One or both nodes not found for edge creation")
        raise HTTPException(404, "One or both nodes not found")
    
    new_edge = Edge(
        id=uuid.uuid4(),
        from_node_id=edge.from_node_id,
        to_node_id=edge.to_node_id,
        option_text=edge.option_text
    )
    db.add(new_edge)
    db.commit()
    db.refresh(new_edge)
    
    logger.info(f"Created edge {new_edge.id}")
    return new_edge


@router.delete("/edges/{edge_id}")
def delete_edge(edge_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Delete an edge (connection).
    
    WHY: Remove unwanted connections from conversation flow
    WHERE: Called when admin deletes a connection
    HOW: Removes edge from database
    
    Args:
        edge_id: Edge to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if edge not found
    """
    logger.info(f"Deleting edge {edge_id}")
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    
    if not edge:
        logger.warning(f"Edge {edge_id} not found for deletion")
        raise HTTPException(404, "Edge not found")
    
    db.delete(edge)
    db.commit()
    
    logger.info(f"Successfully deleted edge {edge_id}")
    return {"message": "Edge deleted successfully"}


# ============= FAQ MANAGEMENT =============

@router.get("/faqs", response_model=list[FAQResponse])
def get_all_faqs_admin(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get all FAQs including inactive ones (admin view).
    
    WHY: Admins need to see all FAQs to manage them
    WHERE: Called by admin FAQ management panel
    HOW: Returns all FAQs regardless of active status
    
    Returns:
        List of all FAQs
    """
    logger.debug("Fetching all FAQs for admin")
    return get_all_faqs(db)


@router.post("/faqs", response_model=FAQResponse)
def create_faq_admin(faq: FAQCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Create a new FAQ entry.
    
    WHY: Add new frequently asked questions
    WHERE: Called from admin FAQ management panel
    
    Args:
        faq: FAQ data (question, answer, order, is_active)
        
    Returns:
        Created FAQ
    """
    return create_faq(faq, db)


@router.put("/faqs/{faq_id}", response_model=FAQResponse)
def update_faq_admin(faq_id: str, faq_update: FAQUpdate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Update an existing FAQ entry.
    
    WHY: Modify FAQ content or status
    WHERE: Called from admin FAQ management panel
    
    Args:
        faq_id: FAQ to update
        faq_update: Fields to update
        
    Returns:
        Updated FAQ
        
    Raises:
        HTTPException: 404 if FAQ not found
    """
    faq = update_faq(faq_id, faq_update, db)
    if not faq:
        raise HTTPException(404, "FAQ not found")
    return faq


@router.delete("/faqs/{faq_id}")
def delete_faq_admin(faq_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Delete an FAQ entry.
    
    WHY: Remove outdated FAQs
    WHERE: Called from admin FAQ management panel
    
    Args:
        faq_id: FAQ to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if FAQ not found
    """
    success = delete_faq(faq_id, db)
    if not success:
        raise HTTPException(404, "FAQ not found")
    return {"message": "FAQ deleted successfully"}


# ============= CHAT HISTORY =============

@router.get("/chat/sessions", response_model=list[ChatSessionSummary])
def get_chat_sessions(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get all chat sessions with summary information.
    
    WHY: Admins can monitor chat usage and review conversations
    WHERE: Called by admin analytics panel
    HOW: Groups chat messages by session and provides statistics
    
    Returns:
        List of session summaries (session_id, last_message_at, message_count)
        Ordered by most recent activity first
    """
    logger.debug("Fetching chat session summaries")
    
    rows = (
        db.query(
            ChatMessage.session_id.label("session_id"),
            func.max(ChatMessage.created_at).label("last_message_at"),
            func.count(ChatMessage.id).label("message_count")
        )
        .group_by(ChatMessage.session_id)
        .order_by(func.max(ChatMessage.created_at).desc())
        .all()
    )
    
    result = [
        ChatSessionSummary(
            session_id=row.session_id,
            last_message_at=row.last_message_at,
            message_count=row.message_count,
        )
        for row in rows
    ]
    
    logger.info(f"Returning {len(result)} chat sessions")
    return result


@router.get("/chat/sessions/{session_id}", response_model=list[ChatMessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    """
    Get all messages within a specific chat session.
    
    WHY: View complete conversation history
    WHERE: Called when admin clicks on a session to review it
    HOW: Queries all messages for the session ordered chronologically
    
    Args:
        session_id: Session UUID
        
    Returns:
        List of messages ordered by time (oldest first)
        
    Raises:
        HTTPException: 400 if session_id is invalid UUID
    """
    logger.debug(f"Fetching messages for session {session_id}")
    
    # Validate UUID format
    try:
        session_uuid = uuid.UUID(session_id)
    except Exception:
        logger.warning(f"Invalid session ID format: {session_id}")
        raise HTTPException(400, "Invalid session_id")
    
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_uuid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    
    result = [
        ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            sender=m.sender,
            message_text=m.message_text,
            node_id=m.node_id,
            created_at=m.created_at,
        )
        for m in messages
    ]
    
    logger.info(f"Returning {len(result)} messages for session {session_id}")
    return result
