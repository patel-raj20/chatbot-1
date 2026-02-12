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
import time
import json

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
from app.auth.utils import get_current_user

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a chat message and return bot response.
    
    HOW IT WORKS:
        1. Check Redis cache for answer (if new question, not node navigation)
        2. If cache HIT: Return cached answer immediately
        3. If cache MISS: Save user's message to database
        4. Determine which node to use:
           a) If current_node_id provided: Follow edge based on user's option
           b) If no current_node: Find entry node or FAQ
        5. Generate response with options (if node has outgoing edges)
        6. Cache the response (for future requests)
        7. Save bot's response to database
    
    Args:
        payload: ChatRequest containing session_id, message, current_node_id
        db: Database session (injected)
        
    Returns:
        ChatResponse with reply text, node_id, and options
        
    Raises:
        HTTPException: If invalid option selected (400)
    """
    # Start timing for performance monitoring
    request_start_time = time.time()
    
    logger.info(f"Chat message received: session={payload.session_id}, message='{payload.message}'")
    
    # ========== STEP 0: CHECK CACHE (only for new questions, not node navigation) ==========
    if payload.current_node_id is None:
        try:
            # Import cache service from main app
            from app.main import cache_service
            
            cached_answer, cache_retrieval_time = await cache_service.get_cached_answer(payload.message)
            
            if cached_answer:
                # Cache HIT - return cached response immediately
                total_time = (time.time() - request_start_time) * 1000
                logger.info(
                    f"✓ CACHE HIT | Question: '{payload.message[:50]}...' | "
                    f"Cache: {cache_retrieval_time:.2f}ms | Total: {total_time:.2f}ms"
                )
                
                # Save user message to history (for tracking)
                save_chat_message(
                    session_id=payload.session_id,
                    sender="user",
                    message_text=payload.message,
                    db=db
                )
                
                # Parse cached response
                response_dict = json.loads(cached_answer)
                cached_reply = response_dict.get("reply", "")
                
                # Save bot message to history
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=cached_reply,
                    db=db,
                    node_id=response_dict.get("node_id")
                )
                
                # Return cached response
                return ChatResponse(**response_dict)
                
        except Exception as e:
            # Cache error should not break the chat - log and continue
            logger.warning(f"Cache retrieval error (will proceed normally): {e}")
    
    # ========== STEP 2: Determine conversation node ==========
    node = None
    
    if payload.current_node_id is None:
        # User is starting a conversation or asking a new question
        logger.debug("No current node - searching for entry node or FAQ")
        
        # Save user's message for new questions
        save_chat_message(
            session_id=payload.session_id,
            sender="user",
            message_text=payload.message,
            db=db
        )
        
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
                # FAQ found - save response and cache it
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=faq_answer,
                    db=db,
                    node_id=None
                )
                
                # Cache FAQ response for future requests
                faq_response = ChatResponse(reply=faq_answer)
                try:
                    from app.main import cache_service
                    await cache_service.cache_answer(payload.message, faq_response.json())
                    logger.debug(f"FAQ answer cached for question: '{payload.message}'")
                except Exception as e:
                    logger.warning(f"Failed to cache FAQ response: {e}")
                
                logger.info("Returning FAQ answer")
                return faq_response
            
            # Try fuzzy matching for similar entry nodes
            node = find_similar_node(payload.message, db)
            
            if not node:
                # No match found - return default message
                # Frontend will try RAG if document is uploaded
                default_response = "I didn't understand that."
                
                # DON'T save default response to database - it will be replaced
                # by RAG answer if document is available. If RAG is not available,
                # the "I didn't understand that" message isn't useful in history anyway.
                # save_chat_message(
                #     session_id=payload.session_id,
                #     sender="bot",
                #     message_text=default_response,
                #     db=db
                # )
                
                # Cache default response to avoid repeated processing
                default_response_obj = ChatResponse(reply=default_response)
                try:
                    from app.main import cache_service
                    await cache_service.cache_answer(payload.message, default_response_obj.json())
                    logger.debug(f"Default response cached for question: '{payload.message}'")
                except Exception as e:
                    logger.warning(f"Failed to cache default response: {e}")
                
                logger.info("No match found - returning default response")
                return default_response_obj
    
    
    else:
        # User is continuing a conversation by selecting an option
        logger.debug(f"Following edge from node {payload.current_node_id}")
        
        # Save user's message for option selection (before cache check to avoid duplicate)
        save_chat_message(
            session_id=payload.session_id,
            sender="user",
            message_text=payload.message,
            db=db
        )
        
        # ========== CHECK OPTION CACHE ==========
        try:
            from app.main import cache_service
            
            cached_option_response, cache_retrieval_time = await cache_service.get_cached_option_response(
                str(payload.current_node_id),
                payload.message
            )
            
            if cached_option_response:
                # Option cache HIT - return cached response immediately
                total_time = (time.time() - request_start_time) * 1000
                logger.info(
                    f"✓ OPTION CACHE HIT | Node: {payload.current_node_id} | Option: '{payload.message}' | "
                    f"Cache: {cache_retrieval_time:.2f}ms | Total: {total_time:.2f}ms"
                )
                
                # Parse cached response
                response_dict = json.loads(cached_option_response)
                cached_reply = response_dict.get("reply", "")
                
                # Save bot message to history
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=cached_reply,
                    db=db,
                    node_id=response_dict.get("node_id")
                )
                
                # Return cached response
                return ChatResponse(**response_dict)
                
        except Exception as e:
            # Cache error should not break the chat
            logger.warning(f"Option cache retrieval error (will proceed normally): {e}")
        
        # ========== FOLLOW EDGE (Cache MISS) ==========
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
    
    # Build response object
    response = None
    
    # Check for automatic transition (single edge with no option text)
    if len(edges) == 1 and edges[0].option_text is None:
        # Automatically follow to next node
        logger.debug("Automatic transition detected - following edge")
        next_node, next_edges = get_node_with_edges(edges[0].to_node_id, db)
        
        if not next_node:
            logger.warning("Next node not found in automatic transition")
            response = ChatResponse(reply=node.message_text, node_id=node.id)
        elif not next_edges:
            # Next node has no options
            response = ChatResponse(reply=next_node.message_text, node_id=next_node.id)
        else:
            # Return next node with its options
            response = ChatResponse(
                reply=next_node.message_text,
                node_id=next_node.id,
                options=[
                    Option(text=e.option_text, next_node_id=e.to_node_id)
                    for e in next_edges if e.option_text
                ]
            )
    elif not edges:
        # No outgoing edges - end of conversation path
        logger.debug("No outgoing edges - end of conversation path")
        response = ChatResponse(reply=node.message_text, node_id=node.id)
    else:
        # Return current node with options
        logger.debug(f"Returning {len(edges)} options to user")
        response = ChatResponse(
            reply=node.message_text,
            node_id=node.id,
            options=[
                Option(text=e.option_text, next_node_id=e.to_node_id)
                for e in edges if e.option_text
            ]
        )
    
    # ========== STEP 5: CACHE THE RESPONSE ==========
    try:
        from app.main import cache_service
        
        # Serialize response to JSON for caching
        response_json = response.json()
        
        if payload.current_node_id is None:
            # Cache new question response
            await cache_service.cache_answer(payload.message, response_json)
        else:
            # Cache option selection response
            await cache_service.cache_option_response(
                str(payload.current_node_id),
                payload.message,
                response_json
            )
            
    except Exception as e:
        # Cache storage error should not break the chat
        logger.warning(f"Failed to cache response: {e}")
    
    # ========== STEP 6: LOG RESPONSE TIME ==========
    total_time = (time.time() - request_start_time) * 1000
    
    if payload.current_node_id is None:
        # Question-based request
        logger.info(
            f"✗ QUESTION CACHE MISS | Question: '{payload.message[:50]}...' | "
            f"DB retrieval: {total_time:.2f}ms"
        )
    else:
        # Option-based request
        logger.info(
            f"✗ OPTION CACHE MISS | Node: {payload.current_node_id} | Option: '{payload.message}' | "
            f"DB retrieval: {total_time:.2f}ms"
        )
    
    return response


