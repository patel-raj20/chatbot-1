"""
FAQ Routes
==========
User-facing FAQ endpoints.

ENDPOINTS:
    GET /faqs - Get all active FAQs for display in chat interface
    
WHY: Provides quick answers to common questions
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import FAQResponse, WorkflowQuestionResponse
from app.services.faq_service import get_active_faqs
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["faqs"])


@router.get("/faqs", response_model=list[FAQResponse])
def list_faqs(db: Session = Depends(get_db)):
    """
    Retrieve all active FAQs for display in chat interface.
    
    WHY: Users can browse FAQs to quickly find answers
    WHERE: Called by frontend to display FAQ list
    HOW: Returns only active FAQs ordered by the 'order' field
    
    Returns:
        List of active FAQ objects with question, answer, order
    """
    logger.debug("Fetching active FAQs")
    faqs = get_active_faqs(db)
    logger.info(f"Returning {len(faqs)} active FAQs")
    return faqs


@router.get("/faqs/search", response_model=list[FAQResponse])
def search_faqs_endpoint(query: str, db: Session = Depends(get_db)):
    """Search FAQs by question text for dynamic suggestions."""
    from app.services.faq_service import search_faqs
    
    if len(query) < 2:
        return []
    
    logger.debug(f"Searching FAQs with query: {query}")
    results = search_faqs(query, db, limit=8)
    logger.info(f"Found {len(results)} matching FAQs")
    return results


@router.get("/workflow-questions", response_model=list[WorkflowQuestionResponse])
def get_workflow_questions(db: Session = Depends(get_db)):
    """Get all workflow entry questions for display on chatbot load."""
    from app.models import Node
    
    logger.info("Fetching workflow entry questions")
    nodes = db.query(Node).filter(
        Node.is_entry == True,
        Node.trigger_text.isnot(None)
    ).order_by(Node.position_y, Node.position_x).all()
    
    logger.info(f"Found {len(nodes)} workflow entry nodes")
    
    result = [
        WorkflowQuestionResponse(
            id=node.id,
            trigger_text=node.trigger_text,
            message_text=node.message_text
        )
        for node in nodes
    ]
    
    return result
