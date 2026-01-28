from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from rapidfuzz import fuzz

from .database import Base, SessionLocal, engine
from .models import ChatMessage, Edge, Node, FAQ
from .schemas import (
    ChatRequest, ChatResponse, Option, FAQResponse, FAQCreate, FAQUpdate,
    NodeCreate, NodeUpdate, NodeResponse, NodeWithEdges,
    EdgeCreate, EdgeResponse,
    ChatMessageResponse, ChatSessionSummary
)
from sqlalchemy import func

app = FastAPI()

# Allow the Next.js dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001","http://192.168.3.166:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Ensure tables exist when the app starts
Base.metadata.create_all(bind=engine)

# ============= RAG SETUP =============
# Include RAG routes
from app.rag.routes import router as rag_router
app.include_router(rag_router)

# Connect to Milvus on startup
@app.on_event("startup")
async def startup_event():
    """Connect to Milvus vector database on startup"""
    try:
        from pymilvus import connections
        connections.connect(
            alias="default",
            host="localhost",
            port="19530"
        )
        print("[OK] Connected to Milvus successfully")
    except Exception as e:
        print(f"[WARNING] Could not connect to Milvus: {e}")

# ============= END RAG SETUP =============


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def find_similar_node(user_message: str, db: Session, threshold: int = 80):
    """Find a node with similar trigger_text using fuzzy matching"""
    entry_nodes = db.query(Node).filter(Node.is_entry == True, Node.trigger_text.isnot(None)).all()
    
    best_match = None
    best_score = 0
    
    for node in entry_nodes:
        score = fuzz.ratio(user_message.lower(), node.trigger_text.lower())
        if score > best_score and score >= threshold:
            best_score = score
            best_match = node
    
    return best_match


@app.get("/")
def root():
    return {"status": "Backend running"}


@app.post("/chat/message", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):

    # Save user message
    db.add(ChatMessage(
        id=uuid.uuid4(),
        session_id=payload.session_id,
        sender="user",
        message_text=payload.message
    ))
    db.commit()

    # Find node
    if payload.current_node_id is None:
        # First try to find an entry node
        node = db.query(Node).filter(
            Node.trigger_text == payload.message,
            Node.is_entry == True
        ).first()
        
        # If no node found, check FAQs
        if not node:
            faq = db.query(FAQ).filter(
                FAQ.question.ilike(f"%{payload.message}%"),
                FAQ.is_active == True
            ).first()
            if faq:
                # Log FAQ answer as a bot message in chat history
                db.add(ChatMessage(
                    id=uuid.uuid4(),
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=faq.answer,
                    node_id=None
                ))
                db.commit()
                return ChatResponse(reply=faq.answer)
            
            # Try fuzzy matching for similar nodes
            node = find_similar_node(payload.message, db)
            if not node:
                return ChatResponse(reply="I didn't understand that.")
    else:
        edge = db.query(Edge).filter(
            Edge.from_node_id == payload.current_node_id,
            Edge.option_text == payload.message
        ).first()
        if not edge:
            raise HTTPException(400, "Invalid option")
        node = db.query(Node).filter(Node.id == edge.to_node_id).first()

    # Save bot message
    db.add(ChatMessage(
        id=uuid.uuid4(),
        session_id=payload.session_id,
        sender="bot",
        message_text=node.message_text,
        node_id=node.id
    ))
    db.commit()

    # Fetch edges
    edges = db.query(Edge).filter(Edge.from_node_id == node.id).all()

    if not edges:
        return ChatResponse(reply=node.message_text, node_id=node.id)

    # If there's a single automatic transition (no option text), follow it and
    # return the next node's message plus any of its options.
    if len(edges) == 1 and edges[0].option_text is None:
        next_node = db.query(Node).filter(Node.id == edges[0].to_node_id).first()
        next_edges = db.query(Edge).filter(Edge.from_node_id == next_node.id).all()

        if not next_edges:
            return ChatResponse(reply=next_node.message_text, node_id=next_node.id)

        return ChatResponse(
            reply=next_node.message_text,
            node_id=next_node.id,
            options=[
                Option(text=e.option_text, next_node_id=e.to_node_id)
                for e in next_edges if e.option_text
            ]
        )

    return ChatResponse(
        reply=node.message_text,
        node_id=node.id,
        options=[
            Option(text=e.option_text, next_node_id=e.to_node_id)
            for e in edges if e.option_text
        ]
    )


@app.get("/faqs", response_model=list[FAQResponse])
def get_faqs(db: Session = Depends(get_db)):
    """Get all active FAQs ordered by their order field"""
    faqs = db.query(FAQ).filter(FAQ.is_active == True).order_by(FAQ.order).all()
    return faqs


# ============= ADMIN ENDPOINTS =============

@app.get("/admin/nodes", response_model=list[NodeWithEdges])
def get_all_nodes(db: Session = Depends(get_db)):
    """Get all nodes with their edges"""
    nodes = db.query(Node).all()
    result = []
    for node in nodes:
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
    return result


@app.get("/admin/nodes/{node_id}", response_model=NodeWithEdges)
def get_node(node_id: str, db: Session = Depends(get_db)):
    """Get a specific node with its edges"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
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


@app.post("/admin/nodes", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    """Create a new node"""
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
    return new_node


@app.put("/admin/nodes/{node_id}", response_model=NodeResponse)
def update_node(node_id: str, node_update: NodeUpdate, db: Session = Depends(get_db)):
    """Update an existing node"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(404, "Node not found")
    
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
    return node


@app.delete("/admin/nodes/{node_id}")
def delete_node(node_id: str, db: Session = Depends(get_db)):
    """Delete a node and all its edges and related chat messages"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(404, "Node not found")
    
    # Delete all chat messages that reference this node
    db.query(ChatMessage).filter(ChatMessage.node_id == node_id).delete()
    
    # Delete all edges connected to this node
    db.query(Edge).filter(
        (Edge.from_node_id == node_id) | (Edge.to_node_id == node_id)
    ).delete()
    
    db.delete(node)
    db.commit()
    return {"message": "Node deleted successfully"}


@app.get("/admin/edges", response_model=list[EdgeResponse])
def get_all_edges(db: Session = Depends(get_db)):
    """Get all edges"""
    return db.query(Edge).all()


@app.post("/admin/edges", response_model=EdgeResponse)
def create_edge(edge: EdgeCreate, db: Session = Depends(get_db)):
    """Create a new edge (connection between nodes)"""
    # Verify both nodes exist
    from_node = db.query(Node).filter(Node.id == edge.from_node_id).first()
    to_node = db.query(Node).filter(Node.id == edge.to_node_id).first()
    
    if not from_node or not to_node:
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
    return new_edge


@app.delete("/admin/edges/{edge_id}")
def delete_edge(edge_id: str, db: Session = Depends(get_db)):
    """Delete an edge"""
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    if not edge:
        raise HTTPException(404, "Edge not found")
    
    db.delete(edge)
    db.commit()
    return {"message": "Edge deleted successfully"}


# ============= ADMIN FAQ ENDPOINTS =============

@app.get("/admin/faqs", response_model=list[FAQResponse])
def get_all_faqs(db: Session = Depends(get_db)):
    """Get all FAQs (including inactive ones for admin)"""
    return db.query(FAQ).order_by(FAQ.order).all()


@app.post("/admin/faqs", response_model=FAQResponse)
def create_faq(faq: FAQCreate, db: Session = Depends(get_db)):
    """Create a new FAQ"""
    new_faq = FAQ(
        id=uuid.uuid4(),
        question=faq.question,
        answer=faq.answer,
        order=faq.order,
        is_active=faq.is_active
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq


@app.put("/admin/faqs/{faq_id}", response_model=FAQResponse)
def update_faq(faq_id: str, faq_update: FAQUpdate, db: Session = Depends(get_db)):
    """Update an existing FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
    if faq_update.question is not None:
        faq.question = faq_update.question
    if faq_update.answer is not None:
        faq.answer = faq_update.answer
    if faq_update.order is not None:
        faq.order = faq_update.order
    if faq_update.is_active is not None:
        faq.is_active = faq_update.is_active
    
    db.commit()
    db.refresh(faq)
    return faq


@app.delete("/admin/faqs/{faq_id}")
def delete_faq(faq_id: str, db: Session = Depends(get_db)):
    """Delete an FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
    db.delete(faq)
    db.commit()
    return {"message": "FAQ deleted successfully"}


# ============= ADMIN CHAT HISTORY ENDPOINTS =============

@app.get("/admin/chat/sessions", response_model=list[ChatSessionSummary])
def get_chat_sessions(db: Session = Depends(get_db)):
    """Return session summaries ordered by latest activity (descending)."""
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

    # SQLAlchemy returns Row objects; FastAPI/Pydantic can map dict-like
    return [
        ChatSessionSummary(
            session_id=row.session_id,
            last_message_at=row.last_message_at,
            message_count=row.message_count,
        )
        for row in rows
    ]


@app.get("/admin/chat/sessions/{session_id}", response_model=list[ChatMessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Return all messages within a session ordered by time ascending."""
    try:
        session_uuid = uuid.UUID(session_id)
    except Exception:
        raise HTTPException(400, "Invalid session_id")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_uuid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return [
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