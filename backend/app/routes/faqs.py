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
from app.schemas import FAQResponse
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
