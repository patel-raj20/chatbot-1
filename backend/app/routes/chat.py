"""
Chat Routes
===========
API endpoints for chat functionality.

ENDPOINTS:
    POST /chat/message - Send a message and get bot response
    
FLOW:
    1. User sends message with session_id
    2. Try to find matching conversation node (exact or fuzzy)
    3. If no node, search FAQs
    4. If no FAQ, return "I didn't understand" (frontend may fallback to RAG)
    5. Save both user and bot messages to chat history
    6. Return response with options (if any)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, Option
from app.services.chat_service import (
    find_similar_node,
    find_faq_answer,
    save_chat_message,
    get_node_with_edges,
    follow_edge_to_next_node
)
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
def send_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a chat message and return bot response.
    
    HOW IT WORKS:
        1. Save user's message to database
        2. Determine which node to use:
           a) If current_node_id provided: Follow edge based on user's option
           b) If no current_node: Find entry node or FAQ
        3. Generate response with options (if node has outgoing edges)
        4. Save bot's response to database
    
    Args:
        payload: ChatRequest containing session_id, message, current_node_id
        db: Database session (injected)
        
    Returns:
        ChatResponse with reply text, node_id, and options
        
    Raises:
        HTTPException: If invalid option selected (400)
    """
    logger.info(f"Chat message received: session={payload.session_id}, message='{payload.message}'")
    
    # ========== STEP 1: Save user's message ==========
    save_chat_message(
        session_id=payload.session_id,
        sender="user",
        message_text=payload.message,
        db=db
    )
    
    # ========== STEP 2: Determine conversation node ==========
    node = None
    
    if payload.current_node_id is None:
        # User is starting a conversation or asking a new question
        logger.debug("No current node - searching for entry node or FAQ")
        
        # Try exact match with entry node trigger text
        from app.models import Node
        node = db.query(Node).filter(
            Node.trigger_text == payload.message,
            Node.is_entry == True
        ).first()
        
        if node:
            logger.info(f"Exact trigger match found: '{node.trigger_text}'")
        else:
            # Try FAQ search
            faq_answer = find_faq_answer(payload.message, db)
            
            if faq_answer:
                # FAQ found - save response and return
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=faq_answer,
                    db=db,
                    node_id=None
                )
                logger.info("Returning FAQ answer")
                return ChatResponse(reply=faq_answer)
            
            # Try fuzzy matching for similar entry nodes
            node = find_similar_node(payload.message, db)
            
            if not node:
                # No match found - return default message
                # Frontend will try RAG if document is uploaded
                default_response = "I didn't understand that."
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=default_response,
                    db=db
                )
                logger.info("No match found - returning default response")
                return ChatResponse(reply=default_response)
    
    else:
        # User is continuing a conversation by selecting an option
        logger.debug(f"Following edge from node {payload.current_node_id}")
        
        node = follow_edge_to_next_node(
            from_node_id=payload.current_node_id,
            option_text=payload.message,
            db=db
        )
        
        if not node:
            logger.error(f"Invalid option selected: '{payload.message}'")
            raise HTTPException(status_code=400, detail="Invalid option")
    
    # ========== STEP 3: Save bot's response ==========
    save_chat_message(
        session_id=payload.session_id,
        sender="bot",
        message_text=node.message_text,
        db=db,
        node_id=node.id
    )
    
    # ========== STEP 4: Get outgoing edges (options for user) ==========
    _, edges = get_node_with_edges(node.id, db)
    
    # Check for automatic transition (single edge with no option text)
    if len(edges) == 1 and edges[0].option_text is None:
        # Automatically follow to next node
        logger.debug("Automatic transition detected - following edge")
        next_node, next_edges = get_node_with_edges(edges[0].to_node_id, db)
        
        if not next_node:
            logger.warning("Next node not found in automatic transition")
            return ChatResponse(reply=node.message_text, node_id=node.id)
        
        if not next_edges:
            # Next node has no options
            return ChatResponse(reply=next_node.message_text, node_id=next_node.id)
        
        # Return next node with its options
        return ChatResponse(
            reply=next_node.message_text,
            node_id=next_node.id,
            options=[
                Option(text=e.option_text, next_node_id=e.to_node_id)
                for e in next_edges if e.option_text
            ]
        )
    
    # Return current node with options (if any)
    if not edges:
        logger.debug("No outgoing edges - end of conversation path")
        return ChatResponse(reply=node.message_text, node_id=node.id)
    
    logger.debug(f"Returning {len(edges)} options to user")
    return ChatResponse(
        reply=node.message_text,
        node_id=node.id,
        options=[
            Option(text=e.option_text, next_node_id=e.to_node_id)
            for e in edges if e.option_text
        ]
    )
