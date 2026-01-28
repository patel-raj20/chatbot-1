"""
Script to create sample FAQs in the database
Run this once to populate the FAQ table
"""
import uuid
from app.database import SessionLocal, engine, Base
from app.models import FAQ

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Sample FAQs
sample_faqs = [
    {
        "question": "What is this chatbot?",
        "answer": "I'm an AI assistant here to help you navigate through various topics and answer your questions!",
        "order": "1"
    },
    {
        "question": "How can I get started?",
        "answer": "Just type your question or select one of the quick questions above to begin!",
        "order": "2"
    },
    {
        "question": "What can you help me with?",
        "answer": "I can assist with general inquiries, provide information, and guide you through different topics. Try asking me anything!",
        "order": "3"
    },
    {
        "question": "How do I contact support?",
        "answer": "For support, you can reach out through our contact page or email support@example.com",
        "order": "4"
    },
    {
        "question": "What are your features?",
        "answer": "I offer conversational chat, quick FAQ answers, and can guide you through various topics interactively!",
        "order": "5"
    }
]

try:
    # Check if FAQs already exist
    existing = db.query(FAQ).count()
    
    if existing == 0:
        for faq_data in sample_faqs:
            faq = FAQ(
                id=uuid.uuid4(),
                question=faq_data["question"],
                answer=faq_data["answer"],
                order=faq_data["order"],
                is_active=True
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Successfully created {len(sample_faqs)} FAQs!")
    else:
        print(f"ℹ️ FAQs already exist ({existing} found). Skipping creation.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
