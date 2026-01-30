"""
FAQ Service
===========
Business logic for FAQ management.

WHY: Centralizes FAQ-related operations
WHERE USED: By routes/faqs.py and routes/admin.py
HOW IT WORKS: Provides CRUD operations for FAQ entities
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.models import FAQ
from app.schemas import FAQCreate, FAQUpdate
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_active_faqs(db: Session) -> List[FAQ]:
    """
    Retrieve all active FAQs ordered by display order.
    
    WHY: Shows FAQs to users in the chat interface
    WHERE: Called by /faqs endpoint for user-facing FAQ display
    HOW: Queries database for active FAQs and sorts them
    
    Args:
        db: Database session
        
    Returns:
        List of active FAQ objects
    """
    faqs = db.query(FAQ).filter(
        FAQ.is_active == True
    ).order_by(FAQ.order).all()
    
    logger.debug(f"Retrieved {len(faqs)} active FAQs")
    return faqs


def get_all_faqs(db: Session) -> List[FAQ]:
    """
    Retrieve all FAQs including inactive ones (admin view).
    
    WHY: Admins need to see all FAQs to manage them
    WHERE: Called by /admin/faqs endpoint
    HOW: Queries all FAQs regardless of active status
    
    Args:
        db: Database session
        
    Returns:
        List of all FAQ objects
    """
    faqs = db.query(FAQ).order_by(FAQ.order).all()
    logger.debug(f"Retrieved {len(faqs)} total FAQs (including inactive)")
    return faqs


def create_faq(faq_data: FAQCreate, db: Session) -> FAQ:
    """
    Create a new FAQ entry.
    
    WHY: Allows admins to add new FAQs
    WHERE: Called by POST /admin/faqs endpoint
    HOW: Creates new FAQ record in database
    
    Args:
        faq_data: FAQ data from request
        db: Database session
        
    Returns:
        Created FAQ object
    """
    new_faq = FAQ(
        id=uuid.uuid4(),
        question=faq_data.question,
        answer=faq_data.answer,
        order=faq_data.order,
        is_active=faq_data.is_active
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    
    logger.info(f"Created new FAQ: '{new_faq.question}'")
    return new_faq


def update_faq(faq_id: str, faq_data: FAQUpdate, db: Session) -> Optional[FAQ]:
    """
    Update an existing FAQ entry.
    
    WHY: Allows admins to modify FAQ content
    WHERE: Called by PUT /admin/faqs/{faq_id} endpoint
    HOW: Updates specified fields in database
    
    Args:
        faq_id: FAQ unique identifier
        faq_data: Updated FAQ data
        db: Database session
        
    Returns:
        Updated FAQ object or None if not found
    """
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    if not faq:
        logger.warning(f"FAQ {faq_id} not found for update")
        return None
    
    # Update only provided fields
    if faq_data.question is not None:
        faq.question = faq_data.question
    if faq_data.answer is not None:
        faq.answer = faq_data.answer
    if faq_data.order is not None:
        faq.order = faq_data.order
    if faq_data.is_active is not None:
        faq.is_active = faq_data.is_active
    
    db.commit()
    db.refresh(faq)
    
    logger.info(f"Updated FAQ {faq_id}: '{faq.question}'")
    return faq


def delete_faq(faq_id: str, db: Session) -> bool:
    """
    Delete an FAQ entry.
    
    WHY: Allows admins to remove outdated FAQs
    WHERE: Called by DELETE /admin/faqs/{faq_id} endpoint
    HOW: Removes FAQ record from database
    
    Args:
        faq_id: FAQ unique identifier
        db: Database session
        
    Returns:
        True if deleted, False if not found
    """
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    if not faq:
        logger.warning(f"FAQ {faq_id} not found for deletion")
        return False
    
    db.delete(faq)
    db.commit()
    
    logger.info(f"Deleted FAQ {faq_id}: '{faq.question}'")
    return True
