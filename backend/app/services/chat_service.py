"""
Chat Service
============
Business logic for chat functionality including:
- Fuzzy text matching to find conversation nodes
- Node traversal through conversation tree
- FAQ searching

WHY: Separates chat logic from API routes for better organization
WHERE USED: By routes/chat.py to process chat messages
HOW IT WORKS:
    1. User sends message
    2. Try to find matching conversation node (fuzzy match)
    3. If no node found, search FAQs
    4. Return appropriate response with options
"""

from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from typing import Optional, Tuple
import uuid

from app.models import Node, Edge, FAQ, ChatMessage
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


def find_similar_node(user_message: str, db: Session, threshold: int = None) -> Optional[Node]:
    """
    Find a conversation node with similar trigger text using fuzzy matching.
    
    WHY: Allows flexible matching - users don't need exact keywords
    WHERE: Called when no exact node match is found
    HOW: Uses RapidFuzz to compare user input with all entry node triggers
    
    Args:
        user_message: User's input text
        db: Database session
        threshold: Minimum similarity score (0-100), defaults to settings value
        
    Returns:
        Best matching Node or None if no match above threshold
        
    Example:
        User types "hi there" -> Matches node with trigger "hello" (similarity 75%)
    """
    if threshold is None:
        threshold = settings.FUZZY_MATCH_THRESHOLD
    
    # Query all entry nodes (conversation starters)
    entry_nodes = db.query(Node).filter(
        Node.is_entry == True, 
        Node.trigger_text.isnot(None)
    ).all()
    
    logger.debug(f"Searching {len(entry_nodes)} entry nodes for match with '{user_message}'")
    
    best_match = None
    best_score = 0
    
    # Compare user message with each entry node's trigger text
    for node in entry_nodes:
        # Calculate similarity score (0-100)
        score = fuzz.ratio(user_message.lower(), node.trigger_text.lower())
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = node
            logger.debug(f"Found match: '{node.trigger_text}' (score: {score})")
    
    if best_match:
        logger.info(f"Fuzzy match found: '{best_match.trigger_text}' with score {best_score}")
    else:
        logger.debug(f"No fuzzy match found above threshold {threshold}")
    
    return best_match


def find_faq_answer(user_message: str, db: Session) -> Optional[str]:
    """
    Search FAQs for an answer to user's question.
    
    WHY: Provides quick answers to common questions
    WHERE: Called when no conversation node matches
    HOW: Simple text search in FAQ questions
    
    Args:
        user_message: User's question
        db: Database session
        
    Returns:
        FAQ answer text or None if no match found
    """
    # Search for FAQ with question containing user's message
    faq = db.query(FAQ).filter(
        FAQ.question.ilike(f"%{user_message}%"),
        FAQ.is_active == True
    ).first()
    
    if faq:
        logger.info(f"FAQ match found: '{faq.question}'")
        return faq.answer
    
    logger.debug("No FAQ match found")
    return None


def save_chat_message(
    session_id: uuid.UUID,
    sender: str,
    message_text: str,
    db: Session,
    node_id: Optional[uuid.UUID] = None
) -> ChatMessage:
    """
    Save a chat message to database for history tracking.
    
    WHY: Persists conversation history for admin review
    WHERE: Called by chat routes for every message
    HOW: Creates ChatMessage record in database
    
    Args:
        session_id: Unique session identifier
        sender: "user" or "bot"
        message_text: Message content
        db: Database session
        node_id: Associated conversation node (if any)
        
    Returns:
        Created ChatMessage instance
    """
    message = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        sender=sender,
        message_text=message_text,
        node_id=node_id
    )
    db.add(message)
    db.commit()
    logger.debug(f"Saved {sender} message to session {session_id}")
    return message


def get_node_with_edges(node_id: uuid.UUID, db: Session) -> Tuple[Optional[Node], list]:
    """
    Get a conversation node and its outgoing edges (options).
    
    WHY: Determines what options to show user next
    WHERE: Called after finding a matching node
    HOW: Queries node and its connected edges from database
    
    Args:
        node_id: Node unique identifier
        db: Database session
        
    Returns:
        Tuple of (Node, list of Edges) or (None, [])
    """
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        logger.warning(f"Node {node_id} not found")
        return None, []
    
    edges = db.query(Edge).filter(Edge.from_node_id == node.id).all()
    logger.debug(f"Node '{node.message_text}' has {len(edges)} outgoing edges")
    
    return node, edges


def follow_edge_to_next_node(
    from_node_id: uuid.UUID,
    option_text: str,
    db: Session
) -> Optional[Node]:
    """
    Navigate from one node to another via user's option selection.
    
    WHY: Implements conversation flow through the node graph
    WHERE: Called when user clicks an option button
    HOW: Finds edge matching the option text and returns destination node
    
    Args:
        from_node_id: Current node ID
        option_text: User's selected option
        db: Database session
        
    Returns:
        Next Node or None if edge not found
    """
    # Find edge matching the option text
    edge = db.query(Edge).filter(
        Edge.from_node_id == from_node_id,
        Edge.option_text == option_text
    ).first()
    
    if not edge:
        logger.warning(f"No edge found from node {from_node_id} with option '{option_text}'")
        return None
    
    # Get destination node
    next_node = db.query(Node).filter(Node.id == edge.to_node_id).first()
    
    if next_node:
        logger.debug(f"Navigated to node: '{next_node.message_text}'")
    
    return next_node
