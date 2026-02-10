# 🚀 Complete Project Flow Documentation
# Intelligent RAG-Powered Chatbot System

**Last Updated:** February 10, 2026  
**Architecture:** FastAPI Backend + Next.js Frontend + RAG System

---

## 📑 Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Authentication Flow](#authentication-flow)
4. [Chat Flow - Conversation Tree & FAQ](#chat-flow)
5. [RAG Flow - Document-Based Q&A](#rag-flow)
6. [Admin Panel Flow](#admin-panel-flow)
7. [Caching System](#caching-system)
8. [Module-by-Module Deep Dive](#module-deep-dive)
9. [Complete Function Call Sequences](#function-call-sequences)
10. [Data Models & Database Schema](#data-models)

---

## 🏗️ System Architecture Overview {#system-architecture-overview}

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Landing  │  │ Auth     │  │ Chatbot  │  │ Admin    │       │
│  │ Page     │  │ (Login/  │  │ Page     │  │ Panel    │       │
│  │          │  │ Signup)  │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│         │             │             │              │            │
│         └─────────────┴─────────────┴──────────────┘            │
│                          │ HTTP/WS                               │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                  BACKEND (FastAPI)                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Auth       │  │ Chat       │  │ RAG        │  │ Admin     │ │
│  │ Routes     │  │ Routes     │  │ Routes     │  │ Routes    │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
│         │              │                │               │        │
│  ┌──────┴──────────────┴────────────────┴───────────────┴─────┐ │
│  │              Service Layer & Business Logic                 │ │
│  │  • chat_service.py  • faq_service.py  • cache_service.py  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│         │                                                         │
│  ┌──────┴──────────────────────────────────────────────────────┐│
│  │                  Data Access Layer                           ││
│  │  • PostgreSQL (Users, Nodes, Edges, FAQs, Chat History)    ││
│  │  • Redis (Caching + Pub/Sub for streaming)                  ││
│  │  • RabbitMQ (Job queue for async RAG processing)            ││
│  └──────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     RAG WORKER SERVICE                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Processes RAG jobs from RabbitMQ queue                     │ │
│  │  • Retrieves chunks from Milvus                             │ │
│  │  • Streams Groq LLM responses via Redis Pub/Sub             │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     VECTOR DATABASE & STORAGE                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │ Milvus     │  │ MinIO      │  │ Groq API   │                │
│  │ (Vectors)  │  │ (PDF Files)│  │ (LLM)      │                │
│  └────────────┘  └────────────┘  └────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

### Request Flow Types

**Type 1: Authentication Flow**
```
Frontend → Backend API → PostgreSQL → JWT Token → Frontend (stored)
```

**Type 2: Chat Flow (Tree/FAQ)**
```
Frontend → Backend API → Redis Cache (check) → Chat Service → PostgreSQL → Response
```

**Type 3: RAG Flow (Streaming)**
```
Frontend → HTTP Request → RabbitMQ Queue → Worker → Milvus + Groq → Redis Pub/Sub → WebSocket → Frontend
```

**Type 4: Admin Operations**
```
Frontend Admin Panel → Backend Admin API → PostgreSQL CRUD → Response
```

---

## 🛠️ Technology Stack {#technology-stack}

### Frontend Stack
- **Framework:** Next.js 14 (React 18)
- **Styling:** Tailwind CSS
- **State Management:** React Hooks (useState, useEffect)
- **Routing:** Next.js App Router
- **WebSocket:** Native WebSocket API

### Backend Stack
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL
- **Cache:** Redis (dual purpose: caching + pub/sub)
- **Message Queue:** RabbitMQ
- **Vector DB:** Milvus
- **Object Storage:** MinIO
- **LLM API:** Groq (llama-3.1-70b-versatile)

### RAG Components
- **Embeddings:** Sentence Transformers (bge-base-en-v1.5)
- **PDF Processing:** PyPDF2 + pdfplumber
- **Chunking:** Word-based chunking (300-word chunks, 75-word overlap)
- **Retrieval:** Cosine similarity search (top-5, threshold 0.3)

---

## 🔐 Authentication Flow {#authentication-flow}

### Overview
JWT-based authentication with role-based access control (USER/ADMIN roles).

### Components Involved
- **Frontend:** `app/auth/login/page.js`, `app/auth/signup/page.js`
- **Backend:** `backend/app/auth/routes.py`, `backend/app/auth/utils.py`
- **Database:** `users` table

---

### 1. User Signup Flow

#### Step-by-Step Process

**Frontend → Backend → Database**

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Signup     │      │   Backend    │      │  PostgreSQL  │
│   Form       │      │   /auth/     │      │    users     │
└──────────────┘      └──────────────┘      └──────────────┘
      │                      │                      │
      │ POST /auth/signup    │                      │
      │ {username, password} │                      │
      │─────────────────────>│                      │
      │                      │                      │
      │                      │ Check username exists │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │<─────────────────────│
      │                      │ (not exists)         │
      │                      │                      │
      │                      │ Hash password        │
      │                      │ (bcrypt)             │
      │                      │                      │
      │                      │ INSERT new user      │
      │                      │ role='USER'          │
      │                      │─────────────────────>│
      │                      │                      │
      │                      │<─────────────────────│
      │                      │ User created         │
      │                      │                      │
      │<─────────────────────│                      │
      │ 201 Created          │                      │
      │ {message, user}      │                      │
```

#### Function Call Sequence

**Frontend (`app/auth/signup/page.js`):**
```javascript
1. User fills form: username, password
2. handleSubmit() triggered
3. fetch(API_BASE_URL + '/auth/signup', {
     method: 'POST',
     body: JSON.stringify({ username, password })
   })
4. On success → Navigate to /auth/login
5. On error → Display error message
```

**Backend (`backend/app/auth/routes.py`):**
```python
@router.post("/signup")
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # STEP 1: Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(400, "Username already exists")
    
    # STEP 2: Hash password
    hashed_pwd = hash_password(user_data.password)  # bcrypt with salt
    
    # STEP 3: Create user with default role
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd,
        role="USER"  # Default role
    )
    
    # STEP 4: Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "user": {
            "username": new_user.username,
            "role": new_user.role
        }
    }
```

**Password Hashing (`backend/app/auth/utils.py`):**
```python
def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with automatic salt generation.
    
    Security:
        - bcrypt algorithm (industry standard)
        - Automatic salt generation (unique per password)
        - Cost factor 12 (2^12 = 4096 rounds)
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

#### Key Parameters
- **username:** Unique identifier (must be unique in database)
- **password:** Plain text (hashed before storage)
- **role:** Default "USER" (can be manually changed to "ADMIN" via `promote_admin.py`)
- **hashed_password:** bcrypt hash with salt

---

### 2. User Login Flow

#### Step-by-Step Process

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Login      │      │   Backend    │      │  PostgreSQL  │
│   Form       │      │   /auth/     │      │    users     │
└──────────────┘      └──────────────┘      └──────────────┘
      │                      │                      │
      │ POST /auth/login     │                      │
      │ {username, password} │                      │
      │─────────────────────>│                      │
      │                      │                      │
      │                      │ Find user by username│
      │                      │─────────────────────>│
      │                      │                      │
      │                      │<─────────────────────│
      │                      │ User record          │
      │                      │                      │
      │                      │ Verify password      │
      │                      │ (compare bcrypt hash)│
      │                      │                      │
      │                      │ Generate JWT token   │
      │                      │ with Hasura claims   │
      │                      │                      │
      │<─────────────────────│                      │
      │ 200 OK               │                      │
      │ {access_token, user} │                      │
      │                      │                      │
Store token in                │                      │
localStorage                  │                      │
```

#### Function Call Sequence

**Frontend (`app/auth/login/page.js`):**
```javascript
1. User enters username and password
2. handleSubmit() triggered
3. fetch(API_BASE_URL + '/auth/login', {
     method: 'POST',
     body: JSON.stringify({ username, password })
   })
4. On success:
   - Store token: localStorage.setItem('token', data.access_token)
   - Store user: localStorage.setItem('user', JSON.stringify(data.user))
   - Navigate to /chatbot
5. On error → Display error message
```

**Backend (`backend/app/auth/routes.py`):**
```python
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # STEP 1: Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user:
        raise HTTPException(401, "Invalid username or password")
    
    # STEP 2: Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(401, "Invalid username or password")
    
    # STEP 3: Check if account is active
    if not user.is_active:
        raise HTTPException(403, "Account is disabled")
    
    # STEP 4: Generate JWT token with Hasura claims
    token_payload = {
        "sub": str(user.id),  # Subject (user ID)
        "username": user.username,
        "role": user.role,
        # Hasura claims for GraphQL authorization
        "https://hasura.io/jwt/claims": {
            "x-hasura-allowed-roles": [user.role, "anonymous"],
            "x-hasura-default-role": user.role,
            "x-hasura-user-id": str(user.id)
        }
    }
    
    access_token = create_access_token(token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "role": user.role
        }
    }
```

**JWT Token Creation (`backend/app/auth/utils.py`):**
```python
def create_access_token(data: dict) -> str:
    """
    Create JWT access token.
    
    Token Structure:
        Header: {"alg": "HS256", "typ": "JWT"}
        Payload: {sub, username, role, hasura claims, exp}
        Signature: HMAC-SHA256(header + payload, SECRET_KEY)
    
    Expiration: 24 hours (configurable)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt
```

#### Key Parameters
- **username:** User's login identifier
- **password:** Plain text password (verified against hash)
- **access_token:** JWT token containing user ID, role, and Hasura claims
- **token_type:** "bearer" (standard for JWT)
- **user:** User object with id, username, role

---

### 3. Protected Routes (Authentication Guard)

**Frontend (`app/lib/authGuard.js`):**
```javascript
export function useAuthGuard() {
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (!token || !storedUser) {
            // Not authenticated → redirect to login
            router.push('/auth/login');
            return;
        }

        // Authenticated → parse user data
        setUser(JSON.parse(storedUser));
        setLoading(false);
    }, [router]);

    return { loading, user };
}
```

**Usage in Pages:**
```javascript
// app/chatbot/page.js
export default function ChatbotPage() {
    const { loading, user } = useAuthGuard();
    
    if (loading) return <Loading />;
    
    // User is authenticated, render page
    return <ChatInterface user={user} />;
}
```

**Backend (JWT Verification):**
```python
# Every API call includes: Authorization: Bearer <token>
# FastAPI automatically verifies JWT signature
# If invalid/expired → 401 Unauthorized
```

---

## 💬 Chat Flow - Conversation Tree & FAQ {#chat-flow}

### Overview
Three-tier response system with caching:
1. **Redis Cache Check** (fastest)
2. **Conversation Tree Match** (rule-based)
3. **FAQ Search** (keyword-based)
4. **RAG Fallback** (if document available)

### Components Involved
- **Frontend:** `app/chatbot/page.js`, `app/hooks/useChat.js`
- **Backend:** `backend/app/routes/chat.py`, `backend/app/services/chat_service.py`
- **Cache:** `backend/app/cache/cache_service.py`

---

### Complete Chat Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     USER SENDS MESSAGE                          │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│  FRONTEND: useChat.js → sendMessage()                          │
│  • Generate session_id (UUID) if first message                 │
│  • Add user message to UI                                       │
│  • Show typing indicator                                        │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 │ HTTP POST /chat/message
                 │ {session_id, message, current_node_id}
                 ▼
┌────────────────────────────────────────────────────────────────┐
│  BACKEND: routes/chat.py → send_chat_message()                 │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 1: REDIS CACHE CHECK (only if new question)              │
│  • Skip if current_node_id provided (navigating tree)          │
│  • Generate cache key: SHA256(normalized_question)             │
│  • Check Redis: chatbot:qa:<hash>                              │
└────────────────┬───────────────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    CACHE HIT      CACHE MISS
         │               │
         ▼               ▼
┌─────────────┐   ┌─────────────────────────────────────────────┐
│ Return      │   │  STEP 2: DETERMINE CONVERSATION NODE         │
│ cached      │   │  a) If current_node_id → Follow edge         │
│ response    │   │  b) If no node → Find entry node or FAQ     │
│ immediately │   └────────────┬────────────────────────────────┘
└─────────────┘                │
                               ▼
                    ┌──────────────────────────┐
                    │ Node Navigation?         │
                    │ (current_node_id exists) │
                    └──────────┬───────────────┘
                               │
                       ┌───────┴───────┐
                       │               │
                      YES              NO
                       │               │
                       ▼               ▼
            ┌─────────────────┐  ┌────────────────────────┐
            │ Follow Edge to  │  │ New Question:          │
            │ Next Node       │  │ • Exact trigger match  │
            │                 │  │ • Fuzzy match (80%)    │
            │ Service:        │  │ • FAQ search           │
            │ follow_edge_to_ │  └────────┬───────────────┘
            │ next_node()     │           │
            └─────────┬───────┘           │
                      │                   │
                      └───────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Node Found?         │
                    └─────────┬───────────┘
                              │
                      ┌───────┴───────┐
                      │               │
                     YES              NO
                      │               │
                      ▼               ▼
          ┌─────────────────┐  ┌─────────────────────┐
          │ Get Node with   │  │ FAQ Found?          │
          │ Outgoing Edges  │  └──────┬──────────────┘
          │                 │         │
          │ Service:        │   ┌─────┴─────┐
          │ get_node_with_  │   │           │
          │ edges()         │  YES          NO
          └────────┬────────┘   │           │
                   │            ▼           ▼
                   │    ┌──────────┐  ┌──────────────┐
                   │    │ Return   │  │ Return       │
                   │    │ FAQ      │  │ "I don't     │
                   │    │ Answer   │  │ understand"  │
                   │    └──────────┘  └──────┬───────┘
                   │                         │
                   └────────┬────────────────┘
                            │
                            ▼
                ┌─────────────────────────────┐
                │ Build Response with Options │
                │ • reply (message_text)      │
                │ • options (edge labels)     │
                │ • node_id                   │
                └────────────┬────────────────┘
                             │
                             ▼
                ┌──────────────────────────────┐
                │ Save to Database:            │
                │ • User message               │
                │ • Bot response               │
                │ (chat_messages table)        │
                └────────────┬─────────────────┘
                             │
                             ▼
                ┌──────────────────────────────┐
                │ Cache Response (if new Q)    │
                │ Key: chatbot:qa:<hash>       │
                │ TTL: 600 seconds (10 min)    │
                └────────────┬─────────────────┘
                             │
                             ▼
                ┌──────────────────────────────┐
                │ Return to Frontend           │
                │ {reply, options[], node_id}  │
                └────────────┬─────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  FRONTEND: Display Response                                       │
│  • Show bot message                                               │
│  • Render option buttons (if any)                                │
│  • Hide typing indicator                                         │
│  • Auto-scroll to bottom                                         │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  IF "Don't Understand" + Document Available                       │
│  → TRIGGER RAG FALLBACK (See RAG Flow Section)                   │
└──────────────────────────────────────────────────────────────────┘
```

---

### Detailed Function Calls

#### Frontend: Sending a Message

**File:** `frontend/app/hooks/useChat.js`

```javascript
async function sendMessage(text, fromOption = false, nodeContext = null, isFaqClick = false) {
    // PARAMETERS:
    //   text: User's message text
    //   fromOption: True if clicking option button (navigating tree)
    //   nodeContext: Current node_id (for tree navigation)
    //   isFaqClick: True if clicking FAQ link
    
    if (!text || !sessionId) return;

    // 1. Add user message to UI
    setMessages((prev) => [...prev, { sender: "user", text }]);
    setIsTyping(true);

    try {
        // 2. Send to backend
        const data = await sendChatMessage(
            sessionId,           // UUID v4
            text,                // User's message
            fromOption ? nodeContext : null  // Node ID if navigating tree
        );

        // 3. Check if response indicates no match
        const replyLower = data.reply.toLowerCase();
        const didntMatch = replyLower.includes("don't understand") ||
                          replyLower.includes("didn't understand") ||
                          replyLower.includes("i'm not sure");

        // 4. Try RAG fallback if no match and document available
        if (didntMatch && hasDocument && !isFaqClick) {
            // RAG STREAMING FLOW (See RAG section)
            await askRAGQuestionStreaming(text, user?.id, sessionId, ...);
            return;
        }

        // 5. Show FAQ/Tree response
        setIsTyping(false);
        setMessages((prev) => [
            ...prev,
            {
                sender: "bot",
                text: data.reply,
                options: data.options || [],
                nodeId: data.node_id ?? null,
            },
        ]);

        setCurrentNodeId(data.node_id ?? null);
        
    } catch (err) {
        console.error("Chat error:", err);
        setIsTyping(false);
        // Show error message
    }
}
```

**API Call:** `frontend/app/lib/api.js`

```javascript
export async function sendChatMessage(sessionId, message, currentNodeId = null) {
    const response = await fetch(`${API_BASE_URL}/chat/message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`  // JWT token
        },
        body: JSON.stringify({
            session_id: sessionId,        // UUID v4 (generated on first message)
            message: message,              // User's text
            current_node_id: currentNodeId // null or UUID (for tree navigation)
        })
    });

    if (!response.ok) {
        if (response.status === 401) {
            throw new Error('Authentication required');
        }
        throw new Error(`Chat API error: ${response.status}`);
    }

    return response.json();  // {reply, options[], node_id}
}
```

---

#### Backend: Processing Chat Message

**File:** `backend/app/routes/chat.py`

```python
@router.post("/message", response_model=ChatResponse)
async def send_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Process chat message with caching, tree navigation, and FAQ fallback.
    
    PARAMETERS:
        payload.session_id: UUID (tracks conversation)
        payload.message: User's text
        payload.current_node_id: UUID or null (for tree navigation)
        
    RETURNS:
        ChatResponse {
            reply: str (bot's response text)
            options: list[Option] (buttons to show user)
            node_id: UUID or null (current node for next request)
        }
    """
    request_start_time = time.time()
    
    # ====== STEP 0: CHECK REDIS CACHE ======
    # Only check cache for new questions (not tree navigation)
    if payload.current_node_id is None:
        from app.main import cache_service
        
        cached_answer, cache_retrieval_time = await cache_service.get_cached_answer(
            payload.message
        )
        
        if cached_answer:
            # CACHE HIT - Return immediately
            total_time = (time.time() - request_start_time) * 1000
            logger.info(f"✓ CACHE HIT | {cache_retrieval_time:.2f}ms | Total: {total_time:.2f}ms")
            
            # Save user message to history
            save_chat_message(
                session_id=payload.session_id,
                sender="user",
                message_text=payload.message,
                db=db
            )
            
            # Parse and return cached response
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
            
            return ChatResponse(**response_dict)
    
    # ====== STEP 1: DETERMINE CONVERSATION NODE ======
    node = None
    
    if payload.current_node_id is None:
        # NEW QUESTION - Search for entry node or FAQ
        
        # Save user message
        save_chat_message(
            session_id=payload.session_id,
            sender="user",
            message_text=payload.message,
            db=db
        )
        
        # Try exact trigger match
        node = db.query(Node).filter(
            Node.trigger_text == payload.message,
            Node.is_entry == True
        ).first()
        
        if node:
            logger.info(f"Exact trigger match: '{node.trigger_text}'")
        else:
            # Try FAQ search
            faq_answer = find_faq_answer(payload.message, db)
            
            if faq_answer:
                # FAQ FOUND - Cache and return
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=faq_answer,
                    db=db,
                    node_id=None
                )
                
                response = ChatResponse(
                    reply=faq_answer,
                    options=[],
                    node_id=None
                )
                
                # Cache the response
                await cache_service.cache_answer(
                    payload.message,
                    response.json()
                )
                
                return response
            
            # Try fuzzy match (80% similarity)
            node = find_similar_node(payload.message, db)
            
            if not node:
                # NO MATCH FOUND
                no_match_reply = (
                    "I didn't understand that. Could you rephrase? "
                    "Or try asking from the FAQ section."
                )
                
                save_chat_message(
                    session_id=payload.session_id,
                    sender="bot",
                    message_text=no_match_reply,
                    db=db,
                    node_id=None
                )
                
                # DON'T cache "don't understand" responses
                return ChatResponse(
                    reply=no_match_reply,
                    options=[],
                    node_id=None
                )
    
    else:
        # NAVIGATING TREE - Follow edge from current node
        node = follow_edge_to_next_node(
            from_node_id=payload.current_node_id,
            option_text=payload.message,
            db=db
        )
        
        # Save user's option selection
        save_chat_message(
            session_id=payload.session_id,
            sender="user",
            message_text=payload.message,
            db=db,
            node_id=payload.current_node_id
        )
        
        if not node:
            raise HTTPException(400, "Invalid option selected")
    
    # ====== STEP 2: BUILD RESPONSE WITH OPTIONS ======
    node, edges = get_node_with_edges(node.id, db)
    
    # Build option buttons from outgoing edges
    options = [
        Option(text=edge.option_text, node_id=str(edge.to_node_id))
        for edge in edges
    ]
    
    # Save bot response
    save_chat_message(
        session_id=payload.session_id,
        sender="bot",
        message_text=node.message_text,
        db=db,
        node_id=node.id
    )
    
    response = ChatResponse(
        reply=node.message_text,
        options=options,
        node_id=str(node.id)
    )
    
    # ====== STEP 3: CACHE RESPONSE (only for new questions) ======
    if payload.current_node_id is None:
        await cache_service.cache_answer(
            payload.message,
            response.json()
        )
    
    return response
```

---

#### Service Layer Functions

**File:** `backend/app/services/chat_service.py`

##### 1. Fuzzy Matching

```python
def find_similar_node(user_message: str, db: Session, threshold: int = 80) -> Optional[Node]:
    """
    Find conversation node with similar trigger text using fuzzy matching.
    
    ALGORITHM: RapidFuzz (Levenshtein distance)
    THRESHOLD: 80% similarity (configurable)
    
    PARAMETERS:
        user_message: User's input text
        db: Database session
        threshold: Minimum similarity score (0-100)
        
    RETURNS:
        Best matching Node or None
        
    EXAMPLE:
        User: "hi there" → Matches node with trigger: "hello" (75% similar)
    """
    # Query all entry nodes
    entry_nodes = db.query(Node).filter(
        Node.is_entry == True,
        Node.trigger_text.isnot(None)
    ).all()
    
    best_match = None
    best_score = 0
    
    # Compare user message with each trigger
    for node in entry_nodes:
        # Calculate similarity score (0-100)
        score = fuzz.ratio(
            user_message.lower(),
            node.trigger_text.lower()
        )
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = node
    
    return best_match
```

##### 2. FAQ Search

```python
def find_faq_answer(user_message: str, db: Session) -> Optional[str]:
    """
    Search FAQs using simple keyword matching.
    
    ALGORITHM: SQL ILIKE (case-insensitive substring match)
    
    PARAMETERS:
        user_message: User's question
        db: Database session
        
    RETURNS:
        FAQ answer text or None
    """
    faq = db.query(FAQ).filter(
        FAQ.question.ilike(f"%{user_message}%"),
        FAQ.is_active == True
    ).first()
    
    if faq:
        return faq.answer
    
    return None
```

##### 3. Tree Navigation

```python
def follow_edge_to_next_node(
    from_node_id: UUID,
    option_text: str,
    db: Session
) -> Optional[Node]:
    """
    Navigate from one node to another via user's option selection.
    
    PARAMETERS:
        from_node_id: Current node UUID
        option_text: User's selected option (edge label)
        db: Database session
        
    RETURNS:
        Destination Node or None
        
    FLOW:
        Current Node → Edge (matching option_text) → Next Node
    """
    # Find edge matching the option
    edge = db.query(Edge).filter(
        Edge.from_node_id == from_node_id,
        Edge.option_text == option_text
    ).first()
    
    if not edge:
        return None
    
    # Get destination node
    next_node = db.query(Node).filter(Node.id == edge.to_node_id).first()
    
    return next_node
```

##### 4. Chat History

```python
def save_chat_message(
    session_id: UUID,
    sender: str,
    message_text: str,
    db: Session,
    node_id: Optional[UUID] = None
) -> ChatMessage:
    """
    Save chat message to database for history tracking.
    
    PARAMETERS:
        session_id: Conversation UUID
        sender: "user" or "bot"
        message_text: Message content
        db: Database session
        node_id: Associated node (if any)
        
    RETURNS:
        Created ChatMessage instance
        
    USAGE:
        Every message (user and bot) is saved for admin review
    """
    message = ChatMessage(
        id=uuid.uuid4(),
        session_id=session_id,
        sender=sender,
        message_text=message_text,
        node_id=node_id,
        timestamp=datetime.utcnow()
    )
    
    db.add(message)
    db.commit()
    
    return message
```

---

### Cache Service Details

**File:** `backend/app/cache/cache_service.py`

#### Cache Key Generation

```python
def _generate_cache_key(self, question: str) -> str:
    """
    Generate cache key from question using SHA256 hash.
    
    WHY SHA256:
        - Consistent key length regardless of question length
        - Virtually zero collision probability
        - Fast computation
    
    PROCESS:
        1. Normalize question (lowercase, strip whitespace)
        2. Generate SHA256 hash
        3. Add prefix: chatbot:qa:<hash>
    
    EXAMPLES:
        "What is AI?" → "chatbot:qa:a7b3c8d9e1f2..."
        "what is ai?" → "chatbot:qa:a7b3c8d9e1f2..." (same key)
        "What  is  AI?" → "chatbot:qa:a7b3c8d9e1f2..." (normalized spaces)
    """
    # Normalize: lowercase + strip + collapse spaces
    normalized = " ".join(question.lower().strip().split())
    
    # Generate SHA256 hash
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # Add prefix
    cache_key = f"{settings.CACHE_KEY_PREFIX}:{hash_hex}"
    
    return cache_key
```

#### Cache Retrieval

```python
async def get_cached_answer(self, question: str) -> Tuple[Optional[str], float]:
    """
    Retrieve cached answer for a question.
    
    RETURNS:
        Tuple of (cached_answer, retrieval_time_ms)
        
    PERFORMANCE:
        - Typical retrieval: 1-5ms
        - Cache miss: Still very fast (just hash computation)
    """
    start_time = time.time()
    
    if not self.enabled or not self.redis_client.is_connected:
        return None, 0.0
    
    # Generate cache key
    cache_key = self._generate_cache_key(question)
    
    # Retrieve from Redis
    cached_value = await self.redis_client.get(cache_key)
    
    retrieval_time = (time.time() - start_time) * 1000  # ms
    
    if cached_value:
        logger.debug(f"Cache HIT: {cache_key} ({retrieval_time:.2f}ms)")
        return cached_value, retrieval_time
    else:
        logger.debug(f"Cache MISS: {cache_key}")
        return None, retrieval_time
```

#### Cache Storage

```python
async def cache_answer(self, question: str, answer: str) -> bool:
    """
    Store answer in cache with TTL.
    
    PARAMETERS:
        question: User's question
        answer: Answer to cache (JSON string)
        
    TTL: 600 seconds (10 minutes) - configurable
    
    RETURNS:
        True if successfully cached
    """
    if not self.enabled or not self.redis_client.is_connected:
        return False
    
    cache_key = self._generate_cache_key(question)
    
    # Store with TTL
    await self.redis_client.set(
        cache_key,
        answer,
        ex=self.ttl  # Expire after TTL seconds
    )
    
    logger.debug(f"Cached answer: {cache_key} (TTL: {self.ttl}s)")
    
    return True
```

---

## 🤖 RAG Flow - Document-Based Q&A {#rag-flow}

### Overview
RAG (Retrieval-Augmented Generation) allows the chatbot to answer questions from uploaded PDF documents using vector similarity search and LLM generation with streaming.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  INGESTION PATH  │  │   QUERY PATH     │  │  STREAMING PATH  │
└──────────────────┘  └──────────────────┘  └──────────────────┘

INGESTION (Upload PDF):
  PDF File
    │
    ▼
  MinIO Storage ────────────────┐ (Persistent storage)
    │                             │
    ▼                             │
  Text Extraction                 │
  (PyPDF2 + pdfplumber)           │
    │                             │
    ▼                             │
  Chunking                        │
  (300 words, 75 overlap)         │
    │                             │
    ▼                             │
  Embedding                       │
  (bge-base-en-v1.5)              │
  768-dim vectors                 │
    │                             │
    ▼                             │
  Milvus Vector DB ◄──────────────┘
  (Stored with metadata)


QUERY (Ask Question - Synchronous):
  User Question
    │
    ▼
  Embedding (768-dim vector)
    │
    ▼
  Milvus Search
  (Top 5, cosine similarity > 0.3)
    │
    ▼
  Retrieved Chunks
    │
    ▼
  Groq LLM
  (llama-3.1-70b-versatile)
    │
    ▼
  Complete Answer


STREAMING (Ask Question - Async):
  User Question
    │
    ▼
  HTTP Request → RabbitMQ Queue
    │               │
    │               ▼
    │          RAG Worker
    │          (processes job)
    │               │
    │               ▼
    │          Milvus Retrieval
    │               │
    │               ▼
    │          Groq Streaming LLM
    │               │
    │               ▼
    │          Redis Pub/Sub ─────┐
    │          (publish tokens)    │
    ▼                              ▼
  WebSocket Connection ◄───────────┘
    │
    ▼
  Frontend (display tokens)
```

---

### 1. PDF Upload & Ingestion Flow

#### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    PDF UPLOAD & INGESTION                         │
└──────────────────────────────────────────────────────────────────┘

┌────────────┐         ┌────────────┐         ┌────────────────┐
│  Frontend  │         │  Backend   │         │  Storage &     │
│  Upload    │         │  /rag/     │         │  Processing    │
└────────────┘         └────────────┘         └────────────────┘
     │                       │                        │
     │ POST /rag/upload-pdf  │                        │
     │ FormData(file)        │                        │
     │──────────────────────>│                        │
     │                       │                        │
     │                       │ Validate PDF           │
     │                       │ (filetype, size)       │
     │                       │                        │
     │                       │ Save temporary file    │
     │                       │ temp_<filename>.pdf    │
     │                       │                        │
     │                       │ Upload to MinIO        │
     │                       │────────────────────────>│
     │                       │                        │
     │                       │<────────────────────────│
     │                       │ MinIO object name      │
     │                       │                        │
     │                       │ Process PDF:           │
     │                       │ • load_pdf()           │
     │                       │   (extract text)       │
     │                       │────────────────────────>│
     │                       │                        │
     │                       │<────────────────────────│
     │                       │ Extracted text         │
     │                       │                        │
     │                       │ • chunk_text()         │
     │                       │   (300 words each)     │
     │                       │                        │
     │                       │ • embed()              │
     │                       │   (generate vectors)   │
     │                       │────────────────────────>│
     │                       │                        │
     │                       │<────────────────────────│
     │                       │ 768-dim embeddings     │
     │                       │                        │
     │                       │ • Insert to Milvus     │
     │                       │   (chunks + embeddings)│
     │                       │────────────────────────>│
     │                       │                        │
     │                       │ Save metadata          │
     │                       │ to PostgreSQL          │
     │                       │ (pdf_documents table)  │
     │                       │                        │
     │                       │ Clean up temp file     │
     │                       │ (delete local copy)    │
     │                       │                        │
     │<──────────────────────│                        │
     │ 200 OK                │                        │
     │ {status, chunks}      │                        │
```

#### Function Call Sequence

**Frontend** (`app/admin/page.js` or RAG upload component):

```javascript
async function handlePDFUpload(file) {
    /*
    PARAMETERS:
        file: File object from <input type="file">
        
    VALIDATION:
        - Must be .pdf extension
        - File size > 0 bytes
    */
    
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/rag/upload-pdf`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getToken()}`  // JWT auth
        },
        body: formData  // multipart/form-data
    });
    
    if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
    }
    
    const result = await response.json();
    // result = {status, minio_object, filename, chunks}
    
    console.log(`Uploaded: ${result.chunks} chunks created`);
}
```

**Backend** (`backend/app/rag/routes.py`):

```python
@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF for RAG system.
    
    PARAMETERS:
        file: Uploaded PDF file (FastAPI UploadFile object)
        
    RETURNS:
        {
            status: "PDF indexed successfully",
            minio_object: "pdfs/filename_123456.pdf",
            filename: "original_filename.pdf",
            chunks: 42  # Number of chunks created
        }
        
    RAISES:
        HTTPException 400: Invalid file type or empty file
        HTTPException 500: Processing error
    """
    
    temp_path = f"temp_{file.filename}"
    minio_object_name = None
    
    try:
        # STEP 1: Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Only PDF files allowed")
        
        # STEP 2: Check if file is empty
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(400, "Empty file uploaded")
        
        # STEP 3: Save temporarily
        await file.seek(0)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # STEP 4: Upload to MinIO (persistent storage)
        minio_object_name = upload_pdf_to_minio(temp_path, file.filename)
        logger.info(f"Stored in MinIO: {minio_object_name}")
        
        # STEP 5: Process through RAG pipeline
        chunk_count = ingest_pdf(
            pdf_path=temp_path,
            source_file=minio_object_name,
            original_filename=file.filename
        )
        
        # STEP 6: Save metadata to database
        pdf_doc = PDFDocument(
            id=uuid.uuid4(),
            original_filename=file.filename,
            minio_object_name=minio_object_name,
            chunk_count=str(chunk_count),
            upload_date=datetime.utcnow()
        )
        
        db = next(get_db())
        db.add(pdf_doc)
        db.commit()
        db.close()
        
        return {
            "status": "PDF indexed successfully",
            "minio_object": minio_object_name,
            "filename": file.filename,
            "chunks": chunk_count
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

---

#### RAG Pipeline Functions

**File:** `backend/app/rag/pipeline.py`

```python
def ingest_pdf(pdf_path: str, source_file: str, original_filename: str) -> int:
    """
    Complete PDF ingestion pipeline.
    
    PARAMETERS:
        pdf_path: Local path to PDF file
        source_file: MinIO object name (for tracking)
        original_filename: Original user-provided filename
        
    RETURNS:
        Number of chunks created
        
    PROCESS:
        1. Extract text from PDF
        2. Split into chunks
        3. Generate embeddings
        4. Store in Milvus with metadata
    """
    
    # STEP 1: Extract text
    text = load_pdf(pdf_path)
    logger.info(f"Extracted {len(text)} characters")
    
    # STEP 2: Split into chunks
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No text extracted from PDF")
    logger.info(f"Created {len(chunks)} chunks")
    
    # STEP 3: Generate embeddings
    embeddings = embed(chunks)
    if not embeddings:
        raise ValueError("No embeddings generated")
    logger.debug(f"Generated {len(embeddings)} embeddings (768-dim)")
    
    # STEP 4: Store in Milvus
    col = get_collection()
    
    # Prepare metadata for each chunk
    source_files = [source_file] * len(chunks)
    original_filenames = [original_filename] * len(chunks)
    
    # Insert into Milvus
    # NOTE: Appending to collection (not clearing old data)
    col.insert([
        chunks,              # Text content
        embeddings,          # 768-dim vectors
        source_files,        # MinIO object names
        original_filenames   # Original filenames
    ])
    
    col.flush()  # Ensure data is persisted
    logger.info(f"Inserted {len(chunks)} chunks to Milvus")
    
    return len(chunks)
```

**File:** `backend/app/rag/pdf_loader.py`

```python
def load_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using multiple strategies.
    
    STRATEGIES:
        1. PyPDF2 (for digital PDFs)
        2. pdfplumber (for tables and complex layouts)
        3. Fallback to empty string if both fail
    
    PARAMETERS:
        pdf_path: Local file path to PDF
        
    RETURNS:
        Extracted text as string
    """
    text = ""
    
    try:
        # Try PyPDF2 first (fast, works for most PDFs)
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            logger.info(f"Extracted {len(text)} chars using PyPDF2")
            return text
        
        # Fallback to pdfplumber (better for tables)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        logger.info(f"Extracted {len(text)} chars using pdfplumber")
        return text
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""
```

**File:** `backend/app/rag/chunker.py`

```python
def chunk_text(text: str) -> list[str]:
    """
    Word-based chunking with overlap.
    
    STRATEGY:
        - Chunk size: 300 words
        - Overlap: 75 words (25% overlap for context)
        - Minimum chunk: 50 words
    
    WHY OVERLAP:
        - Preserves context across chunk boundaries
        - Helps with questions that span multiple sections
        
    PARAMETERS:
        text: Full text from PDF
        
    RETURNS:
        List of text chunks
        
    EXAMPLE:
        Text: 1000 words
        → Chunk 1: words 0-299
        → Chunk 2: words 225-524 (75-word overlap with chunk 1)
        → Chunk 3: words 450-749
        → Chunk 4: words 675-999
    """
    # Configuration
    CHUNK_SIZE_WORDS = 300
    CHUNK_OVERLAP_WORDS = 75
    MIN_CHUNK_SIZE_WORDS = 50
    
    # Split into words
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return []
    
    chunks = []
    start_idx = 0
    
    while start_idx < total_words:
        # Get words for this chunk
        end_idx = min(start_idx + CHUNK_SIZE_WORDS, total_words)
        chunk_words = words[start_idx:end_idx]
        
        # Skip if chunk is too small (unless last chunk)
        if len(chunk_words) < MIN_CHUNK_SIZE_WORDS and end_idx < total_words:
            start_idx = end_idx
            continue
        
        # Join words back into text
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        # Move to next chunk with overlap
        start_idx += (CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS)
    
    logger.info(f"Created {len(chunks)} chunks from {total_words} words")
    
    return chunks
```

**File:** `backend/app/rag/embedder.py`

```python
def embed(texts: list[str]) -> list[list[float]]:
    """
    Convert text to embeddings using Sentence Transformers.
    
    MODEL: bge-base-en-v1.5
        - Optimized for retrieval tasks
        - 768-dimensional vectors
        - High semantic quality
    
    PARAMETERS:
        texts: List of text strings (chunks or queries)
        
    RETURNS:
        List of normalized embedding vectors (768-dim each)
        
    NORMALIZATION:
        - Divides each vector by its L2 norm
        - Makes cosine similarity more stable
        - Required for Milvus COSINE metric
    """
    global _model
    
    # Load model on first use (singleton pattern)
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        logger.info("Loaded embedding model")
    
    # Generate embeddings
    vectors = _model.encode(texts, normalize_embeddings=False)
    
    # Normalize for cosine similarity
    vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    
    return vectors.tolist()
```

---

### 2. RAG Query Flow (Synchronous)

**URL:** `POST /rag/ask?query=<question>&session_id=<uuid>`

**File:** `backend/app/rag/routes.py`

```python
@router.post("/ask")
def ask(query: str, session_id: str | None = None, db: Session = Depends(get_db)):
    """
    Answer question using RAG (synchronous - returns complete answer).
    
    PARAMETERS:
        query: User's question
        session_id: Optional UUID for chat history
        
    RETURNS:
        {"answer": "Generated answer from documents"}
        
    FLOW:
        1. Call ask_question() pipeline
        2. Optionally save to chat history
        3. Return complete answer
    """
    answer = ask_question(query)
    
    # Save to chat history if session provided
    if session_id:
        try:
            session_uuid = uuid.UUID(session_id)
            db.add(ChatMessage(
                id=uuid.uuid4(),
                session_id=session_uuid,
                sender="bot",
                message_text=answer,
                node_id=None
            ))
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to save to history: {e}")
    
    return {"answer": answer}
```

**File:** `backend/app/rag/pipeline.py`

```python
def ask_question(query: str) -> str:
    """
    Answer question using RAG pipeline (synchronous).
    
    PARAMETERS:
        query: User's question
        
    RETURNS:
        Complete answer from LLM
        
    PROCESS:
        1. Retrieve relevant chunks from Milvus
        2. Combine chunks into context
        3. Generate answer using Groq LLM
        4. Return complete answer
    """
    # STEP 1: Retrieve relevant chunks
    chunks = retrieve(query)
    
    if not chunks:
        return "I couldn't find relevant information in the documents."
    
    # STEP 2: Combine chunks
    context = "\n\n".join(chunks)
    
    # STEP 3: Generate answer
    try:
        from .ollama_client import generate_answer
        answer = generate_answer(context, query)
        return answer
    except Exception as e:
        logger.warning(f"Groq LLM failed: {e}")
        return f"Based on the documents:\n\n{context}\n\n(Groq LLM unavailable)"
```

**File:** `backend/app/rag/retriever.py`

```python
def retrieve(query: str, top_k: int = 5, threshold: float = 0.3) -> list[str]:
    """
    Retrieve relevant document chunks using similarity search.
    
    PARAMETERS:
        query: User's question
        top_k: Number of results to retrieve (default: 5)
        threshold: Minimum similarity score 0.0-1.0 (default: 0.3)
        
    RETURNS:
        List of text chunks (most relevant first)
        
    SIMILARITY METRIC:
        - Cosine similarity (measures angle between vectors)
        - Range: 0.0 (unrelated) to 1.0 (identical)
        - Threshold 0.3 = good balance (not too strict, not too loose)
        
    PROCESS:
        1. Convert query to embedding (768-dim)
        2. Search Milvus for similar embeddings
        3. Filter by threshold
        4. Return matching text chunks
    """
    col = get_collection()
    
    # STEP 1: Convert query to embedding
    q_emb = embed([query])[0]
    
    # STEP 2: Search Milvus
    results = col.search(
        [q_emb],                    # Query vector
        "embedding",                 # Field to search
        param={
            "metric_type": "COSINE", # Cosine similarity
            "params": {"nprobe": 10} # Search 10 partitions
        },
        limit=top_k,                 # Return top K results
        output_fields=["content"]    # Return text content
    )
    
    # STEP 3: Filter by threshold and extract content
    matches = []
    
    for hit in results[0]:
        score = hit.score
        content = hit.entity.get("content")
        
        if score >= threshold:
            matches.append(content)
            logger.debug(f"Match: score={score:.4f}, content={content[:100]}...")
        else:
            logger.debug(f"Rejected: score={score:.4f} < threshold")
    
    logger.info(f"Retrieved {len(matches)}/{top_k} chunks above threshold {threshold}")
    
    return matches
```

---

### 3. RAG Streaming Flow (Asynchronous with WebSocket)

This is the preferred method for RAG queries as it provides real-time streaming.

#### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│              RAG STREAMING FLOW (Asynchronous)                   │
└──────────────────────────────────────────────────────────────────┘

┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐
│  Frontend  │  │  Backend   │  │  RabbitMQ  │  │  Worker +      │
│            │  │  API       │  │  Queue     │  │  Redis Pub/Sub │
└────────────┘  └────────────┘  └────────────┘  └────────────────┘
      │               │               │                   │
      │ 1. POST /rag/ask-stream       │                   │
      │ {question, user_id}           │                   │
      │──────────────>│               │                   │
      │               │               │                   │
      │               │ Generate      │                   │
      │               │ request_id    │                   │
      │               │ (UUID)        │                   │
      │               │               │                   │
      │               │ Publish job   │                   │
      │               │ to RabbitMQ   │                   │
      │               │──────────────>│                   │
      │               │               │                   │
      │<──────────────│               │                   │
      │ 200 OK        │               │                   │
      │ {request_id}  │               │                   │
      │               │               │                   │
      │ 2. Connect WebSocket          │                   │
      │ ws://host/ws/chat/{request_id}│                   │
      │───────────────────────────────┼───────────────────│
      │               │               │                   │
      │               WebSocket       │                   │
      │               established     │                   │
      │               │               │                   │
      │               │               │ Worker pulls job  │
      │               │               │<──────────────────│
      │               │               │                   │
      │               │               │ Process RAG:      │
      │               │               │ • retrieve()      │
      │               │               │ • generate_answer_│
      │               │               │   streaming()     │
      │               │               │                   │
      │               │               │ For each token:   │
      │               │               │ Publish to Redis  │
      │               │               │ Pub/Sub           │
      │               │               │ ─────────────────>│
      │               │               │                   │
      │ 3. Receive tokens via WS      │                   │
      │ ◄─────────────────────────────────────────────────│
      │ {"type":"token","content":"The"}                  │
      │ {"type":"token","content":" answer"}              │
      │ {"type":"token","content":" is"}                  │
      │ ...                           │                   │
      │               │               │                   │
      │ 4. Stream complete            │                   │
      │ ◄─────────────────────────────────────────────────│
      │ {"type":"done"}               │                   │
      │               │               │                   │
      │ Close WebSocket               │                   │
      │               │               │                   │
```

#### Function Call Sequence

**Frontend** (`frontend/app/lib/api.js`):

```javascript
export async function askRAGQuestionStreaming(
    query,
    userId,
    sessionId,
    onToken,      // Callback: (token) => void
    onComplete,   // Callback: () => void
    onError       // Callback: (error) => void
) {
    /*
    PARAMETERS:
        query: User's question
        userId: User UUID (for tracking)
        sessionId: Chat session UUID
        onToken: Function called for each token
        onComplete: Function called when done
        onError: Function called on error
        
    FLOW:
        1. HTTP request to queue job
        2. Connect to WebSocket
        3. Receive tokens in real-time
        4. Call callbacks appropriately
    */
    
    try {
        // STEP 1: Queue the job
        const response = await fetch(`${API_BASE_URL}/rag/ask-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                question: query,
                user_id: userId,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`RAG Streaming API error: ${response.status}`);
        }
        
        const data = await response.json();
        const requestId = data.request_id;  // UUID
        
        // STEP 2: Connect to WebSocket
        const wsUrl = `${API_BASE_URL
            .replace('http:', 'ws:')
            .replace('https:', 'wss:')}/ws/chat/${requestId}`;
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('✓ WebSocket connected for streaming');
        };
        
        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                
                if (message.type === 'token') {
                    // Received a token - display it
                    onToken(message.content);
                    
                } else if (message.type === 'done') {
                    // Stream complete
                    ws.close();
                    onComplete();
                    
                } else if (message.type === 'error') {
                    // Error occurred
                    ws.close();
                    onError(new Error(message.message));
                }
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            onError(new Error('WebSocket connection failed'));
        };
        
        return data;
        
    } catch (err) {
        onError(err);
        throw err;
    }
}
```

**Backend - HTTP Endpoint** (`backend/app/rag/routes.py`):

```python
class StreamingRAGRequest(BaseModel):
    question: str
    user_id: str
    session_id: str | None = None


@router.post("/ask-stream")
async def ask_stream(
    payload: StreamingRAGRequest,
    rmq: RabbitMQClient = Depends(get_rabbitmq_client)
):
    """
    Queue RAG job for async processing with streaming.
    
    PARAMETERS:
        payload.question: User's question
        payload.user_id: User UUID
        payload.session_id: Chat session UUID (optional)
        
    RETURNS:
        {
            "request_id": "uuid-string",
            "message": "Job queued",
            "websocket_url": "ws://host/ws/chat/{request_id}"
        }
        
    FLOW:
        1. Generate unique request_id
        2. Publish job to RabbitMQ
        3. Return request_id to client
        4. Client connects to WebSocket with request_id
        5. Worker processes job and streams via Redis Pub/Sub
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Prepare job data
    job_data = {
        "request_id": request_id,
        "user_id": payload.user_id,
        "question": payload.question,
        "session_id": payload.session_id
    }
    
    # Publish to RabbitMQ queue
    success = rmq.publish_job(job_data)
    
    if not success:
        raise HTTPException(500, "Failed to queue job")
    
    # Return request_id for WebSocket connection
    websocket_url = f"{settings.WEBSOCKET_BASE_URL}/ws/chat/{request_id}"
    
    return {
        "request_id": request_id,
        "message": "Job queued for processing",
        "websocket_url": websocket_url
    }
```

**Backend - WebSocket Endpoint** (`backend/app/routes/websocket.py`):

```python
@router.websocket("/ws/chat/{request_id}")
async def websocket_chat_stream(websocket: WebSocket, request_id: str):
    """
    WebSocket endpoint for streaming chat responses.
    
    PARAMETERS:
        websocket: WebSocket connection object
        request_id: Unique request identifier (from HTTP response)
        
    MESSAGE FORMAT (sent to client):
        {"type": "token", "content": "Hello"}  # Each token
        {"type": "done"}                       # Stream complete
        {"type": "error", "message": "..."}    # Error occurred
        
    FLOW:
        1. Accept WebSocket connection
        2. Subscribe to Redis Pub/Sub channel: chat_stream:{request_id}
        3. Forward messages from Redis to WebSocket
        4. Close when "done" received
    """
    # STEP 1: Accept connection
    await websocket.accept()
    logger.info(f"✓ WebSocket connected: {request_id}")
    
    # Initialize Pub/Sub service
    pubsub = RedisPubSubService()
    
    try:
        # STEP 2: Connect to Redis Pub/Sub
        await pubsub.connect()
        
        # STEP 3: Subscribe to token stream
        async for message in pubsub.subscribe_stream(request_id):
            # STEP 4: Forward to client
            try:
                await websocket.send_json(message)
                
                msg_type = message.get("type")
                if msg_type == "done":
                    logger.info(f"✓ Stream completed: {request_id}")
                    break
                elif msg_type == "error":
                    logger.error(f"Stream error: {message.get('message')}")
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Client disconnected: {request_id}")
                break
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass
    
    finally:
        # STEP 5: Cleanup
        await pubsub.close()
        try:
            await websocket.close()
        except:
            pass
```

**Worker Service** (`backend/worker.py`):

```python
class RAGWorker:
    """
    Background worker that processes RAG jobs from RabbitMQ.
    
    RESPONSIBILITIES:
        1. Consume jobs from queue
        2. Execute RAG pipeline with streaming
        3. Publish tokens to Redis Pub/Sub
        4. ACK RabbitMQ message when done
    """
    
    def process_job(self, ch, method, properties, body):
        """
        Process a single RAG job (RabbitMQ callback).
        
        PARAMETERS:
            ch: RabbitMQ channel
            method: Delivery method (contains delivery_tag for ACK)
            properties: Message properties
            body: JSON message body
            
        FLOW:
            1. Parse job data
            2. Execute RAG streaming pipeline
            3. Publish each token to Redis Pub/Sub
            4. Publish "done" signal
            5. ACK RabbitMQ message
        """
        request_id = None
        
        try:
            # STEP 1: Parse job data
            job = json.loads(body)
            request_id = job.get("request_id")
            user_id = job.get("user_id")
            question = job.get("question")
            session_id = job.get("session_id")
            
            logger.info(f"📥 Job received: {request_id}")
            logger.info(f"   Question: {question}")
            
            # Validate
            if not request_id or not question:
                logger.error("Invalid job: missing data")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # STEP 2: Initialize Redis Pub/Sub (sync client for callback)
            import redis
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            
            channel = f"chat_stream:{request_id}"
            token_count = 0
            
            # STEP 3: Execute RAG pipeline with streaming
            logger.info("🔄 Starting RAG processing...")
            
            for token in ask_question_streaming(question):
                # STEP 4: Publish each token
                message = json.dumps({"type": "token", "content": token})
                redis_client.publish(channel, message)
                token_count += 1
            
            # STEP 5: Publish "done" signal
            done_message = json.dumps({"type": "done"})
            redis_client.publish(channel, done_message)
            
            logger.info(f"✓ Job completed: {request_id} ({token_count} tokens)")
            
            # STEP 6: Save to chat history (optional)
            if session_id:
                # Save complete answer to database
                # (implementation depends on requirements)
                pass
            
            # STEP 7: ACK RabbitMQ message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Job processing failed: {e}")
            
            # Publish error to client
            if request_id:
                try:
                    error_message = json.dumps({
                        "type": "error",
                        "message": str(e)
                    })
                    redis_client.publish(f"chat_stream:{request_id}", error_message)
                except:
                    pass
            
            # ACK message anyway (don't requeue failures)
            ch.basic_ack(delivery_tag=method.delivery_tag)
```

**RAG Streaming Pipeline** (`backend/app/rag/pipeline_streaming.py`):

```python
def ask_question_streaming(query: str) -> Generator[str, None, None]:
    """
    Answer question using RAG with token-by-token streaming.
    
    PARAMETERS:
        query: User's question
        
    YIELDS:
        Individual tokens from LLM response
        
    PROCESS:
        1. Retrieve relevant chunks
        2. If no chunks → yield error message
        3. If chunks found → stream LLM response
    """
    # STEP 1: Retrieve chunks
    chunks = retrieve(query)
    
    if not chunks:
        yield "I couldn't find relevant information in the documents."
        return
    
    # STEP 2: Combine chunks
    context = "\n\n".join(chunks)
    
    # STEP 3: Stream LLM response
    try:
        for token in generate_answer_streaming(context, query):
            yield token
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        yield f"\n\n[Error: {str(e)}]"
```

**Groq Streaming Client** (`backend/app/rag/ollama_client_streaming.py`):

```python
def generate_answer_streaming(context: str, query: str) -> Generator[str, None, None]:
    """
    Generate answer using Groq LLM with streaming.
    
    PARAMETERS:
        context: Retrieved text chunks (combined)
        query: User's original question
        
    YIELDS:
        Individual tokens from LLM
        
    GROQ API:
        Model: llama-3.1-70b-versatile
        Temperature: 0.7 (balanced creativity/accuracy)
        Max tokens: 1024
        Streaming: Enabled
    """
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not configured")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    # Create streaming request
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a factual assistant. Answer ONLY from the provided context. "
                    "Add your context in answer not just copy it from the document. "
                    "Use complete sentences and proper grammar. "
                    "If the question is not related to the context, respond with: "
                    "'The question is not related to the document.'"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\n"
                          f"Answer (use only information from the context):"
            }
        ],
        model=GROQ_MODEL,  # llama-3.1-70b-versatile
        temperature=0.7,
        max_tokens=1024,
        stream=True  # ENABLE STREAMING
    )
    
    # Yield tokens as they arrive
    token_count = 0
    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            token_count += 1
            yield token
    
    logger.info(f"✓ Streaming completed ({token_count} tokens)")
```

---

## 🛠️ Admin Panel Flow {#admin-panel-flow}

### Overview
Admin panel allows administrators to manage conversation flows, FAQs, and view chat history.

### Features
1. **Flow Management** - Visual node editor for conversation trees
2. **FAQ Management** - CRUD operations for FAQs
3. **RAG Management** - Upload/delete PDFs
4. **Chat History** - View all user conversations

---

### Admin Routes

**File:** `backend/app/routes/admin.py`

#### 1. Node Management

```python
# GET /admin/nodes - Get all nodes with edges
@router.get("/nodes", response_model=list[NodeWithEdges])
def get_all_nodes(db: Session = Depends(get_db)):
    """
    Retrieve all conversation nodes with their connections.
    
    RETURNS:
        List of NodeWithEdges objects:
        {
            id: UUID,
            message_text: "Bot's response",
            trigger_text: "User input trigger" (entry nodes only),
            is_entry: boolean,
            position_x: float (for graph editor),
            position_y: float,
            outgoing_edges: [Edge...],
            incoming_edges: [Edge...]
        }
    """
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
            outgoing_edges=[...],
            incoming_edges=[...]
        ))
    
    return result


# POST /admin/nodes - Create new node
@router.post("/nodes", response_model=NodeResponse)
def create_node(node_data: NodeCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation node.
    
    PARAMETERS:
        node_data:
            message_text: Bot's response text (required)
            trigger_text: User input to trigger (optional, for entry nodes)
            is_entry: Whether this is an entry point (default: false)
            position_x: X coordinate in graph editor
            position_y: Y coordinate
    """
    new_node = Node(
        id=uuid.uuid4(),
        message_text=node_data.message_text,
        trigger_text=node_data.trigger_text,
        is_entry=node_data.is_entry,
        position_x=node_data.position_x,
        position_y=node_data.position_y
    )
    
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    
    return new_node


# PUT /admin/nodes/{node_id} - Update node
@router.put("/nodes/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: str,
    node_data: NodeUpdate,
    db: Session = Depends(get_db)
):
    """Update existing node properties."""
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        raise HTTPException(404, "Node not found")
    
    # Update fields
    if node_data.message_text is not None:
        node.message_text = node_data.message_text
    if node_data.trigger_text is not None:
        node.trigger_text = node_data.trigger_text
    if node_data.is_entry is not None:
        node.is_entry = node_data.is_entry
    if node_data.position_x is not None:
        node.position_x = node_data.position_x
    if node_data.position_y is not None:
        node.position_y = node_data.position_y
    
    db.commit()
    db.refresh(node)
    
    return node


# DELETE /admin/nodes/{node_id} - Delete node
@router.delete("/nodes/{node_id}")
def delete_node(node_id: str, db: Session = Depends(get_db)):
    """
    Delete a conversation node.
    
    NOTE: Also deletes all connected edges (cascade).
    """
    node = db.query(Node).filter(Node.id == node_id).first()
    
    if not node:
        raise HTTPException(404, "Node not found")
    
    # Delete connected edges first
    db.query(Edge).filter(
        (Edge.from_node_id == node_id) | (Edge.to_node_id == node_id)
    ).delete()
    
    # Delete node
    db.delete(node)
    db.commit()
    
    return {"message": "Node deleted"}
```

#### 2. Edge Management

```python
# GET /admin/edges - Get all edges
@router.get("/edges", response_model=list[EdgeResponse])
def get_all_edges(db: Session = Depends(get_db)):
    """
    Retrieve all conversation edges (connections).
    
    RETURNS:
        List of Edge objects:
        {
            id: UUID,
            from_node_id: UUID,
            to_node_id: UUID,
            option_text: "Button label"
        }
    """
    edges = db.query(Edge).all()
    return edges


# POST /admin/edges - Create edge
@router.post("/edges", response_model=EdgeResponse)
def create_edge(edge_data: EdgeCreate, db: Session = Depends(get_db)):
    """
    Create connection between two nodes.
    
    PARAMETERS:
        edge_data:
            from_node_id: Source node UUID
            to_node_id: Destination node UUID
            option_text: Button label (what user clicks)
            
    VALIDATION:
        - Both nodes must exist
        - Creates directed edge (one-way connection)
    """
    # Verify nodes exist
    from_node = db.query(Node).filter(Node.id == edge_data.from_node_id).first()
    to_node = db.query(Node).filter(Node.id == edge_data.to_node_id).first()
    
    if not from_node or not to_node:
        raise HTTPException(400, "Invalid node IDs")
    
    new_edge = Edge(
        id=uuid.uuid4(),
        from_node_id=edge_data.from_node_id,
        to_node_id=edge_data.to_node_id,
        option_text=edge_data.option_text
    )
    
    db.add(new_edge)
    db.commit()
    db.refresh(new_edge)
    
    return new_edge


# DELETE /admin/edges/{edge_id} - Delete edge
@router.delete("/edges/{edge_id}")
def delete_edge(edge_id: str, db: Session = Depends(get_db)):
    """Delete connection between nodes."""
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    
    if not edge:
        raise HTTPException(404, "Edge not found")
    
    db.delete(edge)
    db.commit()
    
    return {"message": "Edge deleted"}
```

#### 3. FAQ Management

```python
# GET /admin/faqs - Get all FAQs (including inactive)
@router.get("/faqs", response_model=list[FAQResponse])
def get_all_faqs_admin(db: Session = Depends(get_db)):
    """
    Retrieve all FAQs (admin view includes inactive).
    
    DIFFERENCE from /faqs endpoint:
        - /faqs: Only active FAQs (user view)
        - /admin/faqs: All FAQs (admin view)
    """
    faqs = db.query(FAQ).order_by(FAQ.order).all()
    return faqs


# POST /admin/faqs - Create FAQ
@router.post("/faqs", response_model=FAQResponse)
def create_faq_admin(faq_data: FAQCreate, db: Session = Depends(get_db)):
    """
    Create new FAQ.
    
    PARAMETERS:
        faq_data:
            question: FAQ question text
            answer: FAQ answer text
            order: Display order (lower = higher priority)
            is_active: Whether to show in user interface
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
    
    return new_faq


# PUT /admin/faqs/{faq_id} - Update FAQ
@router.put("/faqs/{faq_id}", response_model=FAQResponse)
def update_faq_admin(
    faq_id: str,
    faq_data: FAQUpdate,
    db: Session = Depends(get_db)
):
    """Update existing FAQ."""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
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
    
    return faq


# DELETE /admin/faqs/{faq_id} - Delete FAQ
@router.delete("/faqs/{faq_id}")
def delete_faq_admin(faq_id: str, db: Session = Depends(get_db)):
    """Delete FAQ permanently."""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    if not faq:
        raise HTTPException(404, "FAQ not found")
    
    db.delete(faq)
    db.commit()
    
    return {"message": "FAQ deleted"}
```

#### 4. Chat History

```python
# GET /admin/chat/sessions - Get all chat sessions
@router.get("/chat/sessions", response_model=list[ChatSessionSummary])
def get_chat_sessions(db: Session = Depends(get_db)):
    """
    Retrieve all chat sessions with summary.
    
    RETURNS:
        List of sessions:
        {
            session_id: UUID,
            message_count: int,
            first_message_time: datetime,
            last_message_time: datetime
        }
    """
    # Group messages by session_id
    sessions = db.query(
        ChatMessage.session_id,
        func.count(ChatMessage.id).label('message_count'),
        func.min(ChatMessage.timestamp).label('first_message'),
        func.max(ChatMessage.timestamp).label('last_message')
    ).group_by(ChatMessage.session_id).all()
    
    return [
        ChatSessionSummary(
            session_id=str(s.session_id),
            message_count=s.message_count,
            first_message_time=s.first_message,
            last_message_time=s.last_message
        )
        for s in sessions
    ]


# GET /admin/chat/sessions/{session_id} - Get session messages
@router.get("/chat/sessions/{session_id}", response_model=list[ChatMessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all messages in a chat session.
    
    RETURNS:
        List of messages (ordered by timestamp):
        {
            id: UUID,
            session_id: UUID,
            sender: "user" | "bot",
            message_text: string,
            node_id: UUID (optional),
            timestamp: datetime
        }
    """
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()
    
    return messages
```

---

## 🗄️ Caching System {#caching-system}

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    REDIS CACHING SYSTEM                           │
└──────────────────────────────────────────────────────────────────┘

TWO SEPARATE REDIS USE CASES:
1. Caching (GET/SET with TTL) - Fast Q&A retrieval
2. Pub/Sub (Streaming) - Real-time token delivery

┌────────────────────────────────────────────────────────────────┐
│                    USE CASE 1: CACHING                          │
└────────────────────────────────────────────────────────────────┘

USER QUESTION
     │
     ▼
┌─────────────────────────────────┐
│ Generate Cache Key              │
│ SHA256(normalized_question)     │
│ → chatbot:qa:<hash>             │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Check Redis Cache               │
│ GET chatbot:qa:<hash>           │
└──────────┬──────────────────────┘
           │
     ┌─────┴─────┐
     │           │
  HIT (found)  MISS (not found)
     │           │
     ▼           ▼
┌────────┐  ┌──────────────────────┐
│ Return │  │ Process request      │
│ cached │  │ (chat/FAQ/RAG)       │
│ answer │  │                      │
│ (~2ms) │  │ Generate response    │
└────────┘  │                      │
            │ Cache response:      │
            │ SET chatbot:qa:<hash>│
            │ Value: JSON response │
            │ TTL: 600 seconds     │
            └──────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                 USE CASE 2: PUB/SUB (STREAMING)                 │
└────────────────────────────────────────────────────────────────┘

RAG WORKER (Publisher)
     │
     │ For each token from Groq:
     │
     ▼
┌─────────────────────────────────┐
│ PUBLISH to Redis Pub/Sub        │
│ Channel: chat_stream:{req_id}   │
│ Message: {"type":"token",...}   │
└──────────┬──────────────────────┘
           │
           │ Redis Pub/Sub
           │ (in-memory, ephemeral)
           │
           ▼
┌─────────────────────────────────┐
│ WebSocket Endpoint (Subscriber) │
│ SUBSCRIBE chat_stream:{req_id}  │
│                                 │
│ Forward to client's WebSocket   │
└──────────┬──────────────────────┘
           │
           ▼
CLIENT BROWSER
(displays token in real-time)
```

### Cache Configuration

**File:** `backend/app/core/config.py`

```python
# Redis connection
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

# Cache behavior
CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1")
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "600"))  # 10 minutes
CACHE_KEY_PREFIX: str = "chatbot:qa"
```

### Cache Key Structure

```
Format: chatbot:qa:<sha256_hash>

Examples:
Question: "What is AI?"
Normalized: "what is ai?"
Hash: sha256("what is ai?") = "a7b3c8d9e1f2..." (64 chars)
Final Key: "chatbot:qa:a7b3c8d9e1f2..."

Question: "What  is  AI?" (extra spaces)
Normalized: "what is ai?" (spaces collapsed)
Hash: Same as above
Final Key: Same (cache hit!)
```

### Performance Metrics

```
┌──────────────────────────────────────────────────────────────┐
│                   CACHE PERFORMANCE                           │
└──────────────────────────────────────────────────────────────┘

Without Cache:
  - Chat + DB query: ~50-100ms
  - RAG retrieval: ~500-2000ms
  - FAQ search: ~20-50ms

With Cache (HIT):
  - Redis retrieval: ~1-5ms
  - Total response: ~10-15ms
  - Speedup: 5-200x faster

Cache Hit Rate:
  - Typical: 30-60% (depends on question diversity)
  - Peak hours: 60-80% (common questions repeated)
```

---

## 📊 Module-by-Module Deep Dive {#module-deep-dive}

### Backend Modules

#### 1. Authentication Module (`backend/app/auth/`)

**Purpose:** Handle user authentication and JWT token management.

**Files:**
- `routes.py` - API endpoints (signup, login)
- `utils.py` - Password hashing, JWT creation
- `schemas.py` - Pydantic models for validation

**Key Functions:**
```python
# utils.py
hash_password(password: str) -> str
verify_password(plain: str, hashed: str) -> bool
create_access_token(data: dict) -> str
decode_access_token(token: str) -> dict
```

**Security Features:**
- bcrypt password hashing (cost factor 12)
- JWT tokens with 24-hour expiration
- Hasura claims for GraphQL authorization
- Role-based access control (USER/ADMIN)

---

#### 2. Cache Module (`backend/app/cache/`)

**Purpose:** Redis-based caching for Q&A responses.

**Files:**
- `redis_client.py` - Low-level Redis operations
- `cache_service.py` - High-level caching logic

**Key Functions:**
```python
# cache_service.py
_normalize_question(question: str) -> str
_generate_cache_key(question: str) -> str
get_cached_answer(question: str) -> Tuple[Optional[str], float]
cache_answer(question: str, answer: str) -> bool
```

**Cache Strategy:**
- Key: SHA256 hash of normalized question
- Value: JSON-serialized ChatResponse
- TTL: 600 seconds (configurable)
- Namespace: `chatbot:qa:*`

---

#### 3. Queue Module (`backend/app/queue/`)

**Purpose:** Async job processing for RAG streaming.

**Files:**
- `rabbitmq_client.py` - RabbitMQ operations
- `pubsub_service.py` - Redis Pub/Sub for streaming

**RabbitMQ Structure:**
```
Exchange: chat_exchange (direct)
Queue: chat_queue (durable)
Routing Key: chat.rag
```

**Pub/Sub Channels:**
```
Format: chat_stream:{request_id}
Messages: {"type": "token|done|error", ...}
```

---

#### 4. RAG Module (`backend/app/rag/`)

**Purpose:** Document processing and question answering.

**Files:**
- `pipeline.py` - Main ingestion and query logic
- `pipeline_streaming.py` - Streaming version for worker
- `pdf_loader.py` - PDF text extraction
- `chunker.py` - Text chunking (word-based)
- `embedder.py` - Convert text to vectors
- `retriever.py` - Similarity search
- `milvus_client.py` - Vector database client
- `minio_client.py` - Object storage client
- `ollama_client.py` - LLM integration (sync)
- `ollama_client_streaming.py` - LLM integration (streaming)
- `collection.py` - Milvus collection management
- `config.py` - RAG configuration
- `routes.py` - API endpoints

**RAG Configuration:**
```python
# Chunking
CHUNK_SIZE_WORDS = 300
CHUNK_OVERLAP_WORDS = 75

# Embedding
MODEL = "BAAI/bge-base-en-v1.5"
DIMENSIONS = 768

# Retrieval
TOP_K = 5
THRESHOLD = 0.3

# LLM
MODEL = "llama-3.1-70b-versatile"
TEMPERATURE = 0.7
MAX_TOKENS = 1024
```

---

#### 5. Routes Module (`backend/app/routes/`)

**Purpose:** API endpoint definitions.

**Files:**
- `chat.py` - Chat messaging endpoints
- `websocket.py` - WebSocket streaming endpoint
- `admin.py` - Admin management endpoints
- `faqs.py` - FAQ listing endpoint

---

#### 6. Services Module (`backend/app/services/`)

**Purpose:** Business logic layer.

**Files:**
- `chat_service.py` - Chat matching and navigation logic
- `faq_service.py` - FAQ CRUD operations

---

### Frontend Modules

#### 1. Pages (`frontend/app/`)

**Structure:**
```
app/
  page.js - Landing page (redirects based on auth)
  layout.js - Root layout
  auth/
    login/page.js - Login form
    signup/page.js - Signup form
  chatbot/page.js - Main chat interface
  admin/page.js - Admin panel
```

---

#### 2. Components (`frontend/app/components/`)

**Categories:**
- `auth/` - Login/signup forms
- `chat/` - Chat message components
- `admin/` - Admin panel components
- `common/` - Shared components (Header, Loading, etc.)

**Key Components:**
```javascript
// chat/
ChatMessage.js - Display single message with options
ChatInput.js - Message input field
TypingIndicator.js - Loading animation
FAQSection.js - FAQ quick links

// admin/
AdminTabs.js - Tab navigation
FAQTab.js - FAQ management
FlowTab.js - Conversation flow editor
RAGTab.js - Document management
HistoryTab.js - Chat history viewer
CustomNode.js - React Flow custom node
```

---

#### 3. Hooks (`frontend/app/hooks/`)

**Custom Hooks:**
```javascript
useChat.js - Chat state management
useAdminFAQ.js - FAQ admin operations
useAdminFlow.js - Flow editor state
useAdminRAG.js - RAG document management
useAdminHistory.js - Chat history fetching
```

---

#### 4. Library (`frontend/app/lib/`)

**Utilities:**
```javascript
api.js - API communication functions
auth.js - Auth token management
authGuard.js - Protected route guard
utils.js - UUID generation, etc.
```

---

## 🔄 Complete Function Call Sequences {#function-call-sequences}

### Sequence 1: User Signup

```
1. Frontend: app/auth/signup/page.js
   └─> handleSubmit()
       └─> fetch(POST /auth/signup)
           Body: {username, password}

2. Backend: app/auth/routes.py
   └─> signup(user_data)
       ├─> Check username exists
       │   └─> db.query(User).filter(username).first()
       ├─> hash_password(password)
       │   └─> bcrypt.hashpw(password, salt)
       ├─> Create User(username, hashed_password, role="USER")
       └─> db.add(), db.commit()

3. Response: {message: "User created", user: {username, role}}

4. Frontend: Redirect to /auth/login
```

---

### Sequence 2: User Login

```
1. Frontend: app/auth/login/page.js
   └─> handleSubmit()
       └─> fetch(POST /auth/login)
           Body: {username, password}

2. Backend: app/auth/routes.py
   └─> login(credentials)
       ├─> db.query(User).filter(username).first()
       ├─> verify_password(password, user.hashed_password)
       │   └─> bcrypt.checkpw(password, hashed)
       └─> create_access_token({sub, username, role, hasura_claims})
           └─> jwt.encode(payload, SECRET_KEY, algorithm="HS256")

3. Response: {access_token, token_type, user: {id, username, role}}

4. Frontend:
   ├─> localStorage.setItem('token', access_token)
   ├─> localStorage.setItem('user', JSON.stringify(user))
   └─> router.push('/chatbot')
```

---

### Sequence 3: Send Chat Message (Tree/FAQ)

```
1. Frontend: app/hooks/useChat.js
   └─> sendMessage(text, fromOption, nodeContext)
       ├─> setMessages([...prev, {sender: "user", text}])
       ├─> setIsTyping(true)
       └─> sendChatMessage(sessionId, text, nodeContext)
           └─> fetch(POST /chat/message)
               Headers: {Authorization: Bearer <token>}
               Body: {session_id, message, current_node_id}

2. Backend: app/routes/chat.py
   └─> send_chat_message(payload)
       │
       ├─> STEP 1: Check Redis Cache (if new question)
       │   └─> cache_service.get_cached_answer(payload.message)
       │       ├─> _generate_cache_key(question)
       │       │   ├─> _normalize_question(question)
       │       │   └─> sha256(normalized).hexdigest()
       │       └─> redis_client.get(cache_key)
       │   
       │   If CACHE HIT:
       │   ├─> save_chat_message(user message)
       │   ├─> save_chat_message(bot message)
       │   └─> return cached response
       │
       ├─> STEP 2: Determine Node
       │   │
       │   If current_node_id is null (new question):
       │   ├─> save_chat_message(user message)
       │   ├─> Try exact match:
       │   │   └─> db.query(Node).filter(trigger_text, is_entry=True)
       │   │
       │   ├─> If no exact match, try FAQ:
       │   │   └─> find_faq_answer(message, db)
       │   │       └─> db.query(FAQ).filter(question.ilike(%message%))
       │   │   
       │   │   If FAQ found:
       │   │   ├─> save_chat_message(bot message)
       │   │   ├─> cache_answer(question, response)
       │   │   └─> return FAQ response
       │   │
       │   └─> If no FAQ, try fuzzy match:
       │       └─> find_similar_node(message, db)
       │           ├─> Query all entry nodes
       │           ├─> For each node:
       │           │   └─> fuzz.ratio(user_message, trigger_text)
       │           └─> Return best match if score >= 80%
       │
       │   If current_node_id provided (navigating tree):
       │   ├─> save_chat_message(user message)
       │   └─> follow_edge_to_next_node(current_node_id, message)
       │       ├─> db.query(Edge).filter(from_node_id, option_text)
       │       └─> db.query(Node).filter(id = edge.to_node_id)
       │
       ├─> STEP 3: Build Response
       │   └─> get_node_with_edges(node.id)
       │       ├─> db.query(Node).filter(id)
       │       ├─> db.query(Edge).filter(from_node_id)
       │       └─> Build options from edges
       │
       ├─> STEP 4: Save Bot Message
       │   └─> save_chat_message(bot message, node_id)
       │
       ├─> STEP 5: Cache Response (if new question)
       │   └─> cache_service.cache_answer(question, response.json())
       │       └─> redis_client.set(cache_key, value, ex=TTL)
       │
       └─> Return ChatResponse{reply, options[], node_id}

3. Frontend: app/hooks/useChat.js
   ├─> Check if reply contains "don't understand"
   │   
   │   If YES and hasDocument:
   │   └─> Trigger RAG fallback (see Sequence 5)
   │
   │   If NO or no document:
   │   ├─> setIsTyping(false)
   │   ├─> setMessages([...prev, {sender: "bot", text, options, nodeId}])
   │   └─> setCurrentNodeId(nodeId)
```

---

### Sequence 4: Upload PDF

```
1. Frontend: app/admin/page.js (RAG Tab)
   └─> handlePDFUpload(file)
       ├─> Validate file (.pdf, size > 0)
       ├─> Create FormData
       └─> uploadPDF(file)
           └─> fetch(POST /rag/upload-pdf)
               Headers: {Authorization: Bearer <token>}
               Body: FormData(file)

2. Backend: app/rag/routes.py
   └─> upload_pdf(file)
       │
       ├─> STEP 1: Validate
       │   ├─> Check .pdf extension
       │   └─> Check file size > 0
       │
       ├─> STEP 2: Save temporarily
       │   └─> Save to temp_<filename>.pdf
       │
       ├─> STEP 3: Upload to MinIO
       │   └─> upload_pdf_to_minio(temp_path, filename)
       │       ├─> Connect to MinIO
       │       ├─> Generate object name: pdfs/<filename>_<timestamp>.pdf
       │       └─> minio_client.fput_object(bucket, object_name, file_path)
       │
       ├─> STEP 4: Process via RAG Pipeline
       │   └─> ingest_pdf(temp_path, minio_object, filename)
       │       │
       │       ├─> load_pdf(pdf_path)
       │       │   ├─> Try PyPDF2.PdfReader
       │       │   │   └─> Extract text from each page
       │       │   └─> Fallback to pdfplumber if PyPDF2 fails
       │       │
       │       ├─> chunk_text(text)
       │       │   ├─> Split text into words
       │       │   ├─> Create chunks of 300 words
       │       │   ├─> Overlap by 75 words
       │       │   └─> Return list of chunk strings
       │       │
       │       ├─> embed(chunks)
       │       │   ├─> Load SentenceTransformer model (if not loaded)
       │       │   ├─> Generate embeddings for all chunks
       │       │   │   └─> model.encode(texts)
       │       │   ├─> Normalize vectors (L2 norm)
       │       │   └─> Return 768-dim vectors
       │       │
       │       └─> Insert to Milvus
       │           └─> col.insert([chunks, embeddings, source_files, filenames])
       │               └─> col.flush()
       │
       ├─> STEP 5: Save Metadata to PostgreSQL
       │   └─> PDFDocument(id, filename, minio_object, chunk_count)
       │       └─> db.add(), db.commit()
       │
       ├─> STEP 6: Clean Up
       │   └─> os.remove(temp_path)
       │
       └─> Return {status, minio_object, filename, chunks}

3. Frontend:
   └─> Display success message
       └─> Refresh document list
```

---

### Sequence 5: RAG Query with Streaming

```
1. Frontend: app/hooks/useChat.js
   └─> sendMessage(text) → "don't understand" + hasDocument
       └─> askRAGQuestionStreaming(text, userId, sessionId, callbacks)
           │
           ├─> STEP 1: HTTP Request to Queue Job
           │   └─> fetch(POST /rag/ask-stream)
           │       Headers: {Authorization: Bearer <token>}
           │       Body: {question, user_id, session_id}
           │
           └─> STEP 2: Connect to WebSocket
               └─> new WebSocket(ws://host/ws/chat/${requestId})
                   ├─> ws.onopen → console.log("Connected")
                   ├─> ws.onmessage → Handle message
                   ├─> ws.onerror → Handle error
                   └─> ws.onclose → Cleanup

2. Backend: app/rag/routes.py
   └─> ask_stream(payload, rmq)
       ├─> Generate request_id (UUID)
       ├─> Build job_data {request_id, user_id, question, session_id}
       ├─> rmq.publish_job(job_data)
       │   └─> RabbitMQ: Publish to chat_queue
       └─> Return {request_id, message, websocket_url}

3. Worker: backend/worker.py
   └─> process_job(ch, method, properties, body)
       │
       ├─> Parse job: {request_id, user_id, question, session_id}
       │
       ├─> Initialize Redis Pub/Sub client
       │   └─> redis.Redis(host, port, decode_responses=True)
       │
       ├─> Execute RAG Pipeline with Streaming
       │   └─> ask_question_streaming(question)
       │       │
       │       ├─> retrieve(query)
       │       │   ├─> embed([query])
       │       │   │   └─> SentenceTransformer.encode([query])
       │       │   │       └─> Normalize vector
       │       │   │
       │       │   ├─> col.search([q_emb], "embedding", limit=5)
       │       │   │   └─> Milvus cosine similarity search
       │       │   │
       │       │   └─> Filter by threshold (0.3)
       │       │       └─> Return matching chunks
       │       │
       │       ├─> If no chunks:
       │       │   └─> yield "No relevant information found"
       │       │
       │       └─> If chunks found:
       │           ├─> Combine chunks into context
       │           └─> generate_answer_streaming(context, query)
       │               ├─> Initialize Groq client
       │               ├─> Create streaming request
       │               │   └─> client.chat.completions.create(
       │               │         messages=[system, user],
       │               │         model="llama-3.1-70b-versatile",
       │               │         temperature=0.7,
       │               │         stream=True
       │               │       )
       │               │
       │               └─> For each chunk in stream:
       │                   └─> yield chunk.choices[0].delta.content
       │
       ├─> For each token from pipeline:
       │   ├─> Build message: {"type": "token", "content": token}
       │   └─> redis_client.publish(f"chat_stream:{request_id}", message)
       │
       ├─> When done:
       │   ├─> Build message: {"type": "done"}
       │   └─> redis_client.publish(f"chat_stream:{request_id}", message)
       │
       └─> ACK RabbitMQ message
           └─> ch.basic_ack(delivery_tag)

4. Backend: app/routes/websocket.py
   └─> websocket_chat_stream(websocket, request_id)
       ├─> await websocket.accept()
       ├─> pubsub = RedisPubSubService()
       ├─> await pubsub.connect()
       │
       └─> async for message in pubsub.subscribe_stream(request_id):
           ├─> await websocket.send_json(message)
           │
           ├─> If type == "done":
           │   └─> break
           │
           └─> If type == "error":
               └─> break

5. Frontend: WebSocket onmessage handler
   └─> Parse JSON message
       │
       ├─> If type == "token":
       │   ├─> fullAnswer += token
       │   └─> Update streaming message in UI
       │
       ├─> If type == "done":
       │   ├─> ws.close()
       │   ├─> onComplete()
       │   └─> Mark message as complete
       │
       └─> If type == "error":
           ├─> ws.close()
           └─> onError(message.message)
```

---

## 🗃️ Data Models & Database Schema {#data-models}

### Database Tables

#### 1. users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT DEFAULT 'USER' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

Indexes:
    - PRIMARY KEY (id)
    - UNIQUE INDEX on username

Roles:
    - USER: Regular user (chatbot access)
    - ADMIN: Administrator (chatbot + admin panel)
```

#### 2. nodes
```sql
CREATE TABLE nodes (
    id UUID PRIMARY KEY,
    message_text TEXT NOT NULL,
    trigger_text TEXT,
    is_entry BOOLEAN DEFAULT FALSE,
    position_x FLOAT DEFAULT 0.0,
    position_y FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);

Purpose:
    - Stores conversation tree nodes
    - message_text: Bot's response
    - trigger_text: Keywords to trigger this node (entry nodes only)
    - is_entry: Can start conversation here
    - position_x/y: Visual position in admin graph editor
```

#### 3. edges
```sql
CREATE TABLE edges (
    id UUID PRIMARY KEY,
    from_node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    to_node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

Purpose:
    - Defines connections between nodes
    - option_text: Button label shown to user
    - Creates directed graph (one-way connections)
```

#### 4. faqs
```sql
CREATE TABLE faqs (
    id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

Purpose:
    - Stores frequently asked questions
    - order: Display priority (lower = higher)
    - is_active: Show/hide in user interface
```

#### 5. chat_messages
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    sender TEXT NOT NULL,  -- 'user' or 'bot'
    message_text TEXT NOT NULL,
    node_id UUID REFERENCES nodes(id),
    timestamp TIMESTAMP DEFAULT NOW()
);

Indexes:
    - INDEX on session_id (for history queries)
    - INDEX on timestamp (for chronological order)

Purpose:
    - Stores all chat messages for history tracking
    - session_id: Groups messages by conversation
    - sender: Identifies user vs bot messages
    - node_id: Links bot messages to conversation node
```

#### 6. pdf_documents
```sql
CREATE TABLE pdf_documents (
    id UUID PRIMARY KEY,
    original_filename TEXT NOT NULL,
    minio_object_name TEXT NOT NULL,
    chunk_count TEXT,
    upload_date TIMESTAMP DEFAULT NOW()
);

Purpose:
    - Tracks uploaded PDFs
    - minio_object_name: Object storage reference
    - chunk_count: Number of chunks created
```

---

### Milvus Collection Schema

```python
Collection Name: "chatbot_docs"

Fields:
    1. content (VARCHAR, primary key)
       - Text chunk content
       - Max length: 65535 characters
    
    2. embedding (FLOAT_VECTOR)
       - 768-dimensional vector
       - Normalized for cosine similarity
    
    3. source_file (VARCHAR)
       - MinIO object name
       - Tracks which PDF this chunk came from
    
    4. original_filename (VARCHAR)
       - Original user-provided filename
       - For display purposes

Index:
    - Type: IVF_FLAT
    - Metric: COSINE
    - Params: {nlist: 128}

Search Parameters:
    - metric_type: COSINE
    - params: {nprobe: 10}
    - limit: 5 (top-K results)
```

---

## 🎯 Key Takeaways

### System Strengths

1. **Modular Architecture** - Clear separation of concerns
2. **Multiple Response Strategies** - Tree → FAQ → RAG fallback
3. **Performance Optimization** - Redis caching for frequent questions
4. **Real-time Streaming** - WebSocket + Pub/Sub for low latency
5. **Scalable Design** - Worker-based async processing
6. **Rich Admin Tools** - Visual flow editor, FAQ management, history viewer

### Data Flow Summary

**Fast Path (Cached):**
```
User → HTTP Request → Redis Cache → Response (1-5ms)
```

**Normal Path (Tree/FAQ):**
```
User → HTTP Request → Database Query → Cache → Response (50-100ms)
```

**RAG Path (Streaming):**
```
User → HTTP Request → RabbitMQ → Worker → Milvus + Groq → Redis Pub/Sub → WebSocket → User (500-2000ms first token)
```

### Important Parameters Reference

**Authentication:**
- JWT expiration: 24 hours
- Password hash: bcrypt cost factor 12

**Chat:**
- Fuzzy match threshold: 80%
- Cache TTL: 600 seconds (10 minutes)

**RAG:**
- Chunk size: 300 words
- Chunk overlap: 75 words
- Embedding dimensions: 768
- Top-K retrieval: 5
- Similarity threshold: 0.3
- LLM model: llama-3.1-70b-versatile
- LLM temperature: 0.7
- Max tokens: 1024

**Performance:**
- Cache hit rate: 30-80%
- Cache retrieval: 1-5ms
- Database query: 50-100ms
- RAG retrieval: 500-2000ms
- Token streaming: Real-time (<100ms per token)

---

**End of Documentation**
