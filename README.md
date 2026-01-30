# Intelligent Chat Bot with RAG (Retrieval-Augmented Generation)

A full-stack intelligent chatbot application powered by **RAG (Retrieval-Augmented Generation)** technology. The system features PDF document ingestion, semantic search using vector embeddings, conversational AI with Ollama LLM, FAQ management, and an admin panel for managing conversation flows.

> **📌 Code Quality**: This project follows professional software engineering practices with comprehensive documentation, structured logging, modular architecture, and detailed inline comments explaining WHY/WHERE/HOW for every component.

---

## 📖 Table of Contents

1. [Key Features](#-key-features)
2. [Tech Stack](#-tech-stack)
3. [Architecture](#️-architecture)
4. [Project Structure](#-project-structure)
5. [How It Works](#-how-it-works)
6. [Setup & Installation](#-setup--installation)
7. [Configuration](#️-configuration)
8. [API Documentation](#-api-documentation)
9. [Development Guide](#-development-guide)

---

## ✨ Key Features

- **🤖 RAG-Powered Chatbot** - Answer questions from uploaded PDF documents using semantic search
- **📄 PDF Document Ingestion** - Upload and process PDF files for knowledge extraction
- **🔍 Vector Similarity Search** - Semantic search using Sentence Transformers embeddings (all-MiniLM-L6-v2)
- **💬 LLM Integration** - Ollama integration for intelligent, context-aware responses
- **🗂️ FAQ Management** - Dynamic FAQ storage and retrieval system
- **🌲 Conversation Flow Builder** - Node-based conversation graph with fuzzy matching
- **👨‍💼 Admin Panel** - Manage FAQs, conversation nodes, and system configuration
- **📊 Persistent Storage** - MinIO for document storage, Milvus for vector database
- **🎨 Modern UI** - Responsive Next.js frontend with Tailwind CSS

## 🚀 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **SQLAlchemy** - SQL toolkit and ORM for database management
- **Milvus** - High-performance vector database for semantic search
- **MinIO** - S3-compatible object storage for PDF documents
- **Sentence Transformers** - State-of-the-art sentence embeddings (all-MiniLM-L6-v2 model)
- **Ollama** - Local LLM runtime (gemma3 model)
- **PyMuPDF** - PDF text extraction
- **RapidFuzz** - Fuzzy string matching for conversation flows

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - Modern JavaScript library for UI
- **Tailwind CSS** - Utility-first CSS framework
- **React Flow** - Interactive conversation graph visualization

### Infrastructure
- **Docker Compose** - Container orchestration
- **etcd** - Distributed configuration and service discovery
- **PostgreSQL** - (Optional) Relational database support

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                   (Next.js Frontend - Port 3000)                │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │  Chat Page  │  │ Admin Panel │  │  API Client (lib/)  │   │
│  │  (page.js)  │  │(admin/page) │  │  - api.js           │   │
│  │             │  │             │  │  - utils.js         │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Port 8000)                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Core Infrastructure (app/core/)                          │  │
│  │  ├── config.py    (Environment & Settings)              │  │
│  │  └── logger.py    (Structured Logging)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Routes (app/routes/)                                 │  │
│  │  ├── chat.py      (Conversation endpoint)               │  │
│  │  ├── faqs.py      (FAQ queries)                         │  │
│  │  └── admin.py     (CRUD for nodes/edges/FAQs/history)   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Business Logic (app/services/)                           │  │
│  │  ├── chat_service.py    (Fuzzy match, conversation)     │  │
│  │  └── faq_service.py     (FAQ management)                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ RAG Pipeline (app/rag/)                                  │  │
│  │  ├── pipeline.py        (Orchestration)                 │  │
│  │  ├── pdf_loader.py      (PDF → Text + OCR)              │  │
│  │  ├── chunker.py         (Text → Chunks)                 │  │
│  │  ├── embedder.py        (Chunks → Vectors)              │  │
│  │  ├── collection.py      (Milvus schema)                 │  │
│  │  ├── retriever.py       (Similarity search)             │  │
│  │  ├── ollama_client.py   (LLM generation)                │  │
│  │  ├── milvus_client.py   (Vector DB connection)          │  │
│  │  ├── minio_client.py    (Document storage)              │  │
│  │  └── routes.py          (Upload/Ask endpoints)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Data Layer (app/)                                        │  │
│  │  ├── database.py    (SQLAlchemy engine & sessions)      │  │
│  │  ├── models.py      (ORM models)                        │  │
│  │  └── schemas.py     (Pydantic validation)               │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────┬─────────────────┬──────────────────┬─────────────────┘
           │                 │                  │
           ▼                 ▼                  ▼
    ┌──────────┐      ┌─────────────┐    ┌────────────┐
    │SQLAlchemy│      │   Milvus    │    │   MinIO    │
    │   ORM    │      │   Vector    │    │  Document  │
    │ (SQLite/ │      │  Database   │    │  Storage   │
    │PostgreSQL)│      │  (19530)    │    │ (9000/9001)│
    └──────────┘      └─────────────┘    └────────────┘
                            │
                            ▼
                      ┌──────────┐
                      │  Ollama  │
                      │   LLM    │
                      │ (11434)  │
                      │ (gemma3) │
                      └──────────┘
```

### Data Flow

#### 1. Chat Flow (Hybrid: FAQ → Fuzzy Match → RAG Fallback)

```
User Message
    │
    ├─→ [FAQ Check] ──────────→ Match? ──→ Return FAQ Answer
    │                              ↓ No
    ├─→ [Fuzzy Match] ────────→ Match? ──→ Return Node + Options
    │   (RapidFuzz)                 ↓ No
    │                          
    └─→ [RAG Pipeline] ────────→ Has PDF? ──→ Vector Search → LLM → Answer
                                      ↓ No
                                 "I don't understand"
```

**Detailed Steps:**

1. **User sends message** → Frontend (`page.js`) → `POST /chat/message`
2. **Backend receives** → `routes/chat.py` → `chat_service.py`
3. **FAQ Check** → `find_faq_answer()` → Exact match in FAQ table
4. **Fuzzy Match** → `find_similar_node()` → RapidFuzz with 80% threshold
5. **RAG Fallback** → If no match + PDF uploaded → `POST /rag/ask`
6. **Save History** → `save_chat_message()` → ChatMessage table
7. **Return Response** → JSON with `{reply, options, node_id}`

#### 2. PDF Upload & Ingestion Flow

```
PDF File Upload
    │
    ├─→ [MinIO Storage] ──→ Save PDF to bucket "pdfs"
    │
    ├─→ [Text Extraction] ──→ PyPDF → Text
    │                             ↓ (If minimal text)
    │                          OCR (Tesseract)
    │
    ├─→ [Chunking] ──────────→ Split into 200-char chunks (50 overlap)
    │
    ├─→ [Embedding] ──────────→ SentenceTransformer → 384-dim vectors
    │
    └─→ [Milvus] ─────────────→ Store vectors + metadata in collection
```

**Detailed Steps:**

1. **User uploads PDF** → Frontend → `uploadPDF()` → `POST /rag/upload-pdf`
2. **Save to MinIO** → `minio_client.upload_pdf_to_minio()` → S3-compatible storage
3. **Extract Text** → `pdf_loader.load_pdf()` → PyPDF (+ OCR if scanned)
4. **Chunk Text** → `chunker.chunk_text()` → Overlapping chunks for context
5. **Generate Embeddings** → `embedder.embed()` → all-MiniLM-L6-v2 model
6. **Store Vectors** → `collection.get_collection().insert()` → Milvus DB
7. **Return Success** → Frontend sets `hasDocument = true`

#### 3. RAG Question Answering Flow

```
User Question
    │
    ├─→ [Embed Query] ──────────→ Convert question to 384-dim vector
    │
    ├─→ [Similarity Search] ─────→ Milvus top-k=5 search
    │                                   ↓
    ├─→ [Filter by Threshold] ───────→ Keep score > 0.0
    │                                   ↓
    ├─→ [Build Context] ─────────────→ Combine retrieved chunks
    │
    └─→ [LLM Generation] ────────────→ Ollama (gemma3) → Answer
```

**Detailed Steps:**

1. **User asks question** → Frontend → `askRAGQuestion()` → `POST /rag/ask`
2. **Embed Query** → `embedder.embed([query])` → Vector representation
3. **Search Vectors** → `retriever.retrieve()` → Milvus similarity search
4. **Build Context** → Concatenate top-5 chunks
5. **Generate Answer** → `ollama_client.generate_answer()` → LLM prompt
6. **Return Answer** → JSON `{answer, sources}`

---

## 📁 Project Structure

```
Chat_bot/
├── backend/
│   ├── app/
│   │   ├── core/                    # Core infrastructure
│   │   │   ├── config.py            # Centralized configuration management
│   │   │   └── logger.py            # Structured logging system
│   │   │
│   │   ├── routes/                  # API endpoints
│   │   │   ├── chat.py              # Chat conversation endpoint
│   │   │   ├── faqs.py              # FAQ queries (user-facing)
│   │   │   └── admin.py             # Admin CRUD operations
│   │   │
│   │   ├── services/                # Business logic layer
│   │   │   ├── chat_service.py      # Chat logic (fuzzy match, conversation)
│   │   │   └── faq_service.py       # FAQ management operations
│   │   │
│   │   ├── rag/                     # RAG Pipeline Module
│   │   │   ├── __init__.py          # Module initialization
│   │   │   ├── config.py            # RAG-specific configuration
│   │   │   ├── pipeline.py          # Main RAG orchestration
│   │   │   ├── pdf_loader.py        # PDF text extraction (+ OCR)
│   │   │   ├── chunker.py           # Text chunking strategy
│   │   │   ├── embedder.py          # Sentence Transformer embeddings
│   │   │   ├── collection.py        # Milvus collection schema
│   │   │   ├── retriever.py         # Vector similarity search
│   │   │   ├── ollama_client.py     # Ollama LLM integration
│   │   │   ├── milvus_client.py     # Milvus connection utilities
│   │   │   ├── minio_client.py      # MinIO storage client
│   │   │   └── routes.py            # RAG API endpoints
│   │   │
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── database.py              # Database connection & session management
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   └── schemas.py               # Pydantic validation schemas
│   │
│   ├── create_faqs.py               # FAQ initialization script
│   ├── migrate_postgres.py          # PostgreSQL migration utility
│   ├── Dockerfile                   # Backend container definition
│   └── requirements.txt             # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── lib/                     # Utility functions
│   │   │   ├── api.js               # Centralized API client
│   │   │   └── utils.js             # Helper functions (UUID, etc.)
│   │   │
│   │   ├── layout.js                # Root layout component
│   │   ├── page.js                  # Chat interface (main page)
│   │   └── admin/
│   │       └── page.js              # Admin panel (FAQ/Node management)
│   │
│   ├── styles/
│   │   └── globals.css              # Global Tailwind styles
│   │
│   ├── package.json                 # Node dependencies
│   ├── postcss.config.js            # PostCSS configuration
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   ├── next.config.js               # Next.js configuration
│   └── Dockerfile                   # Frontend container definition
│
├── docker-compose.yml               # Docker services orchestration
├── requirements.txt                 # Root-level Python dependencies
├── ADMIN_GUIDE.md                   # Administrator documentation
├── DOCKER_GUIDE.md                  # Docker setup instructions
└── README.md                        # This file
```

### Key Components Explained

#### Backend Core (`app/core/`)

**config.py** - Centralized Configuration
- **WHY**: Single source of truth for all environment variables
- **WHAT**: Pydantic Settings class with validation
- **WHERE USED**: Imported by main.py, logger.py, all RAG modules
- **KEY SETTINGS**: DATABASE_URL, CORS origins, Milvus/MinIO/Ollama hosts, log level

**logger.py** - Structured Logging
- **WHY**: Replace scattered print() with organized logging
- **WHAT**: Python logging module with formatters and handlers
- **WHERE USED**: Every module uses `logger = get_logger(__name__)`
- **LOG LEVELS**: DEBUG (verbose), INFO (normal), WARNING, ERROR

#### Backend Routes (`app/routes/`)

**chat.py** - Chat Endpoint
- **ROUTE**: `POST /chat/message`
- **WHAT**: Main conversation endpoint with FAQ → Fuzzy Match → RAG fallback
- **FLOW**: Check FAQ table → Fuzzy match nodes → Return response + options
- **RETURNS**: `{reply: str, options: list, node_id: str}`

**faqs.py** - FAQ Query Endpoint
- **ROUTE**: `GET /faqs`
- **WHAT**: Returns active FAQs for display
- **USED BY**: Frontend chat page to show FAQ suggestions

**admin.py** - Admin CRUD Endpoints
- **ROUTES**: 
  - `GET/POST/PUT/DELETE /admin/nodes` - Conversation nodes
  - `GET/POST/DELETE /admin/edges` - Node connections
  - `GET/POST/PUT/DELETE /admin/faqs` - FAQ management
  - `GET /admin/chat-sessions` - Chat history
  - `GET /admin/chat-sessions/{id}/messages` - Session messages
- **WHAT**: Complete admin panel backend
- **USED BY**: Admin panel frontend (`admin/page.js`)

#### Backend Services (`app/services/`)

**chat_service.py** - Chat Business Logic
- **WHY**: Separate business logic from API routes
- **FUNCTIONS**:
  - `find_similar_node()` - RapidFuzz with 80% threshold
  - `find_faq_answer()` - Exact FAQ matching
  - `save_chat_message()` - Persist conversation history
  - `get_node_with_edges()` - Fetch node + edges for options
  - `follow_edge_to_next_node()` - Navigate conversation tree

**faq_service.py** - FAQ Management
- **WHY**: Reusable FAQ operations for routes
- **FUNCTIONS**: `get_active_faqs()`, `get_all_faqs()`, `create_faq()`, `update_faq()`, `delete_faq()`

#### Backend RAG Pipeline (`app/rag/`)

**pipeline.py** - RAG Orchestration
- **FUNCTIONS**:
  - `ingest_pdf()` - PDF → Text → Chunks → Embeddings → Milvus
  - `ask_question()` - Query → Retrieve → Generate Answer
- **WHY**: Main entry point coordinating all RAG operations
- **WHERE USED**: Called by `routes.py` endpoints

**pdf_loader.py** - PDF Text Extraction
- **FEATURES**:
  - Standard extraction with PyPDF
  - OCR fallback for scanned documents (Tesseract + pdf2image)
  - Image preprocessing (grayscale, threshold, denoise)
- **WHY**: Handle both digital and scanned PDFs
- **DEPENDENCIES**: PyPDF, pytesseract, pdf2image, Pillow, OpenCV

**chunker.py** - Text Chunking
- **STRATEGY**: Fixed-size chunks (200 chars) with overlap (50 chars)
- **WHY**: Embeddings work better on smaller, focused text segments
- **OVERLAP**: Maintains context across chunk boundaries

**embedder.py** - Text Embeddings
- **MODEL**: all-MiniLM-L6-v2 (SentenceTransformers)
- **OUTPUT**: 384-dimensional vectors
- **WHY**: Convert text to numerical representation for similarity search
- **WHERE USED**: PDF ingestion + query embedding

**collection.py** - Milvus Schema Management
- **SCHEMA**:
  - `id` (VARCHAR) - Unique chunk identifier
  - `content` (VARCHAR) - Original text
  - `embedding` (FLOAT_VECTOR, dim=384) - Vector representation
  - `source_file` (VARCHAR) - MinIO object key
  - `original_filename` (VARCHAR) - User-uploaded filename
- **INDEX**: IVF_FLAT for fast approximate nearest neighbor search
- **WHY**: Define structure for vector storage

**retriever.py** - Similarity Search
- **FUNCTION**: `retrieve(query, top_k=5, threshold=0.0)`
- **HOW**: Embed query → Milvus search → Filter by score → Return chunks
- **OUTPUT**: List of (text, score, source) tuples
- **WHERE USED**: RAG question answering

**ollama_client.py** - LLM Integration
- **FUNCTION**: `generate_answer(context, query)`
- **MODEL**: gemma3 (running on Ollama)
- **PROMPT**: "Answer the question using ONLY the provided context..."
- **ERROR HANDLING**: Connection errors, timeouts, HTTP failures
- **WHY**: Generate natural language answers from retrieved chunks

**milvus_client.py** - Vector Database Connection
- **FUNCTION**: `connect_milvus()`
- **HOST**: Configured via MILVUS_HOST/MILVUS_PORT (default 19530)
- **WHERE USED**: Application startup in main.py

**minio_client.py** - Document Storage
- **FUNCTIONS**:
  - `get_minio_client()` - Connection to MinIO
  - `ensure_bucket_exists()` - Auto-create "pdfs" bucket
  - `upload_pdf_to_minio()` - Save PDF with sanitized filename
  - `sanitize_filename()` - Remove special characters
- **WHY**: Durable storage for uploaded PDFs
- **ACCESS**: S3-compatible API (can swap for AWS S3)

**routes.py** - RAG API Endpoints
- **ROUTES**:
  - `POST /rag/upload-pdf` - Upload PDF for ingestion
  - `POST /rag/ask` - Ask question with RAG
  - `GET /rag/debug` - View all stored chunks
  - `DELETE /rag/clear` - Clear all vectors
  - `GET /rag/documents` - List uploaded PDFs
  - `DELETE /rag/documents/{id}` - Delete PDF + vectors
- **WHERE USED**: Frontend API calls

#### Frontend (`frontend/app/`)

**lib/api.js** - Centralized API Client
- **WHY**: Avoid duplicate fetch() calls, centralize error handling
- **FUNCTIONS**:
  - `sendChatMessage(sessionId, message, nodeId)` - Chat API
  - `askRAGQuestion(query, sessionId)` - RAG query
  - `fetchFAQs()` - Get FAQ list
  - `uploadPDF(file)` - Upload PDF
- **EXPORTS**: API_BASE_URL for custom calls

**lib/utils.js** - Helper Functions
- **FUNCTIONS**:
  - `generateUUID()` - Session ID generation with crypto API fallback
- **WHY**: Reusable utilities across components

**page.js** - Main Chat Interface
- **FEATURES**:
  - Session-based chat history
  - FAQ suggestions
  - Hybrid response (FAQ → Tree → RAG)
  - Typing indicator
  - Option buttons for conversation flow
- **STATE MANAGEMENT**: React hooks (useState, useEffect)
- **API USAGE**: Imports from `lib/api.js`

**admin/page.js** - Admin Panel
- **FEATURES**:
  - Conversation graph visualization (React Flow)
  - Node CRUD operations
  - Edge creation/deletion
  - FAQ management
  - Chat history viewer
- **WHY**: Visual management of conversation flows

#### Database Models (`app/models.py`)

**Node** - Conversation Tree Nodes
- **FIELDS**: id, text, response
- **PURPOSE**: Store conversation prompts and bot responses
- **RELATIONSHIPS**: One-to-many with Edge (outgoing options)

**Edge** - Conversation Connections
- **FIELDS**: id, from_node_id, to_node_id, option_text
- **PURPOSE**: Link nodes to create conversation flow
- **EXAMPLE**: "Yes" option from "Want help?" → "How can I assist?"

**ChatMessage** - Conversation History
- **FIELDS**: id, session_id, message, response, timestamp
- **PURPOSE**: Persist user conversations for analytics
- **USED BY**: Admin panel chat history viewer

**FAQ** - Frequently Asked Questions
- **FIELDS**: id, question, answer, is_active
- **PURPOSE**: Quick answers without tree navigation
- **PRIORITY**: Checked before conversation tree

**PDFDocument** - Uploaded Documents
- **FIELDS**: id, filename, original_filename, file_path, upload_time
- **PURPOSE**: Track PDFs for deletion and management
- **RELATIONSHIPS**: Linked to Milvus vectors by source_file

---

---

## 🔍 How It Works

### Understanding the Hybrid Chat System

This chatbot uses a **three-tier fallback mechanism** to provide answers:

```
1. FAQ (Fastest)        → Exact match from FAQ table
        ↓ No match
2. Fuzzy Match          → RapidFuzz similarity (80% threshold)
        ↓ No match
3. RAG (Most Powerful)  → Vector search + LLM generation
```

**WHY THREE TIERS?**
- **FAQ**: Instant answers for common questions (no computation)
- **Fuzzy Match**: Handles typos and variations ("hi" → "hello", "thx" → "thanks")
- **RAG**: Answers any question from uploaded documents (most flexible)

### Detailed Component Explanations

#### 1. Configuration System (`app/core/config.py`)

**PURPOSE**: Single source of truth for all settings

**WHY**: Avoid hardcoded values scattered across codebase

**HOW**: Pydantic Settings class reads from `.env` file or environment variables

**KEY SETTINGS**:
```python
DATABASE_URL           # SQLite or PostgreSQL connection
CORS_ORIGINS           # Allowed frontend origins
MILVUS_HOST/PORT       # Vector database connection
MINIO_ENDPOINT         # Document storage
OLLAMA_BASE_URL        # LLM service
LOG_LEVEL              # DEBUG, INFO, WARNING, ERROR
FUZZY_MATCH_THRESHOLD  # Similarity percentage (default 80)
```

**WHERE USED**: Imported at top of every module that needs config

#### 2. Logging System (`app/core/logger.py`)

**PURPOSE**: Replace scattered `print()` with structured logging

**WHY**: 
- Enable/disable debug output via LOG_LEVEL
- Add timestamps and severity levels
- Separate logs by module (easier debugging)

**HOW**: Python logging module with custom formatter

**USAGE PATTERN**:
```python
from app.core.logger import get_logger
logger = get_logger(__name__)

logger.debug("Detailed info for debugging")
logger.info("Normal operation messages")
logger.warning("Something unusual happened")
logger.error("An error occurred")
```

**LOG LEVELS**:
- `DEBUG`: Verbose (every operation, variable values)
- `INFO`: Normal operation (started, completed, results)
- `WARNING`: Unexpected but handled situations
- `ERROR`: Failures requiring attention

#### 3. Database Layer

**database.py** - Connection Management
- **WHY**: Centralize database connection logic
- **WHAT**: SQLAlchemy engine, SessionLocal factory, Base class
- **DEPENDENCY INJECTION**: `get_db()` yields sessions for FastAPI routes

**models.py** - ORM Models
- **WHY**: Object-oriented database access (no raw SQL)
- **MODELS**: Node, Edge, ChatMessage, FAQ, PDFDocument
- **RELATIONSHIPS**: Node ↔ Edge (one-to-many), automatic joins

**schemas.py** - API Validation
- **WHY**: Validate request/response data structure
- **WHAT**: Pydantic models with type checking
- **BENEFIT**: Automatic API documentation, prevents bad data

#### 4. Chat Service (`app/services/chat_service.py`)

**find_similar_node()**
- **ALGORITHM**: RapidFuzz token_set_ratio
- **THRESHOLD**: 80% similarity required
- **WHY**: Handle typos ("Hw r u?" → "How are you?")
- **HOW**: Compares input to all node texts, returns best match

**find_faq_answer()**
- **ALGORITHM**: Case-insensitive substring match
- **EXAMPLE**: "pricing" matches FAQ "What is your pricing?"
- **PRIORITY**: Checked before fuzzy match (faster)

**save_chat_message()**
- **PURPOSE**: Persist conversation history
- **USED FOR**: Analytics, chat history viewer in admin panel
- **STORED**: session_id, message, response, timestamp

**get_node_with_edges()**
- **PURPOSE**: Fetch node + outgoing edges in one query
- **RETURNS**: Node data + list of option buttons
- **WHERE**: Used by chat endpoint to build response

**follow_edge_to_next_node()**
- **PURPOSE**: Navigate conversation tree based on selected option
- **HOW**: Find edge with matching option_text → Return target node
- **USED**: When user clicks option button

#### 5. FAQ Service (`app/services/faq_service.py`)

**get_active_faqs()**
- **PURPOSE**: Return only active FAQs (is_active=True)
- **USED BY**: Chat page FAQ suggestions

**get_all_faqs()**
- **PURPOSE**: Return all FAQs including inactive
- **USED BY**: Admin panel

**create_faq() / update_faq() / delete_faq()**
- **PURPOSE**: CRUD operations for admin panel
- **VALIDATION**: Uses Pydantic schemas

#### 6. RAG Pipeline Deep Dive

**WHAT IS RAG?**
Retrieval-Augmented Generation combines:
1. **Retrieval**: Find relevant document chunks (semantic search)
2. **Augmentation**: Add retrieved context to LLM prompt
3. **Generation**: LLM creates answer using context

**WHY RAG?**
- LLMs have knowledge cutoff dates
- Can't answer questions about private documents
- RAG grounds answers in actual document content (reduces hallucination)

**PDF INGESTION PIPELINE** (`ingest_pdf()`):

```
1. UPLOAD → MinIO Storage
   - Save original PDF for download/deletion
   - Generate unique object key

2. EXTRACT → Text Extraction
   - PyPDF for digital PDFs
   - OCR (Tesseract) for scanned PDFs
   - Preprocessing: grayscale, threshold, denoise

3. CHUNK → Text Splitting
   - Split into 200-character chunks
   - 50-character overlap (maintains context)
   - Example: "...end of chunk A [overlap] start of chunk B..."

4. EMBED → Vector Conversion
   - SentenceTransformer (all-MiniLM-L6-v2)
   - Convert text → 384-dim numerical vector
   - Similar text → similar vectors

5. STORE → Milvus Database
   - Insert vectors with metadata
   - Create IVF_FLAT index for fast search
   - Store: id, content, embedding, source_file, original_filename
```

**QUESTION ANSWERING PIPELINE** (`ask_question()`):

```
1. EMBED QUERY
   - User question → 384-dim vector
   - Same model as document embedding

2. SIMILARITY SEARCH
   - Milvus finds top-k=5 nearest vectors
   - Uses cosine similarity (dot product)
   - Returns chunks with score

3. FILTER BY THRESHOLD
   - Keep only chunks with score > threshold
   - Discard irrelevant results

4. BUILD CONTEXT
   - Concatenate retrieved chunks
   - Add source information

5. LLM GENERATION
   - Send context + question to Ollama
   - Prompt: "Answer ONLY using provided context"
   - Model: gemma3 (or configured model)

6. RETURN ANSWER
   - Formatted response with sources
   - JSON: {answer, sources}
```

**WHY CHUNKING?**
- Embeddings work better on focused text segments
- 200 chars ≈ 1-2 sentences (optimal granularity)
- Overlap prevents context loss at boundaries

**WHY IVF_FLAT INDEX?**
- IVF = Inverted File (clusters vectors)
- Faster than brute-force search
- Good balance: speed vs accuracy

**OCR SUPPORT** (`pdf_loader.py`):
- **WHEN**: If standard extraction yields < 100 characters
- **HOW**: Convert PDF pages → images → Tesseract OCR → text
- **PREPROCESSING**:
  - Grayscale: Remove color noise
  - OTSU threshold: Optimize contrast automatically
  - Median blur: Remove noise while preserving edges
- **WHY**: Many documents are scanned (no embedded text)

#### 7. Vector Search (`retriever.py`)

**retrieve() Function**:
```python
def retrieve(query, top_k=5, threshold=0.0):
    # 1. Convert query to vector
    query_embedding = embedder.embed([query])[0]
    
    # 2. Search Milvus
    results = collection.search(
        data=[query_embedding],
        limit=top_k,
        output_fields=["content", "source_file", "original_filename"]
    )
    
    # 3. Filter by score
    filtered = [r for r in results if r.score > threshold]
    
    return filtered
```

**HOW SIMILARITY WORKS**:
- Cosine similarity: angle between vectors
- Range: -1 (opposite) to 1 (identical)
- 0 = perpendicular (unrelated)
- Typically use threshold 0.3-0.7

#### 8. Ollama Integration (`ollama_client.py`)

**generate_answer() Function**:
```python
def generate_answer(context, query):
    prompt = f"""
    Answer the question using ONLY the provided context.
    If the context doesn't contain the answer, say "I don't know".
    
    Context:
    {context}
    
    Question: {query}
    
    Answer:
    """
    
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": "gemma3", "prompt": prompt}
    )
    
    return response.json()["response"]
```

**WHY THIS PROMPT?**
- "ONLY provided context": Prevents hallucination
- "Say I don't know": Handles incomplete information
- Structured format: Improves answer quality

**ERROR HANDLING**:
- Connection errors → "Ollama not available"
- Timeouts → "Request timed out"
- HTTP errors → Log status code and message

#### 9. Frontend Architecture

**lib/api.js** - API Client
- **WHY**: Centralize all fetch() calls
- **BENEFITS**:
  - Single place to update API_BASE_URL
  - Consistent error handling
  - Reusable across components
- **PATTERN**:
```javascript
export async function sendChatMessage(sessionId, message, nodeId) {
  const response = await fetch(`${API_BASE_URL}/chat/message`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id: sessionId, message, current_node_id: nodeId})
  });
  if (!response.ok) throw new Error("Chat request failed");
  return response.json();
}
```

**lib/utils.js** - Helper Functions
- **generateUUID()**: Session IDs with crypto.randomUUID() + fallback
- **WHY**: Unique session tracking for conversation history

**page.js** - Chat Interface
- **STATE MANAGEMENT**:
  - `messages`: Chat history array
  - `sessionId`: Unique conversation ID
  - `hasDocument`: PDF uploaded flag
  - `isTyping`: Loading indicator
  - `faqs`: FAQ list for suggestions

- **CHAT FLOW**:
```javascript
async function sendMessage(text, fromOption, nodeContext, isFaqClick) {
  // 1. Try FAQ/Tree
  const data = await sendChatMessage(sessionId, text, nodeContext);
  
  // 2. Check if no match
  const noMatch = data.reply.includes("don't understand");
  
  // 3. Try RAG if no match + PDF uploaded
  if (noMatch && hasDocument && !isFaqClick) {
    const ragData = await askRAGQuestion(text, sessionId);
    // Show RAG answer
  } else {
    // Show tree answer + options
  }
}
```

**admin/page.js** - Admin Panel
- **React Flow**: Visual conversation graph
- **NODE DRAGGING**: Update positions via PATCH request
- **EDGE CREATION**: Click node → select target → create connection
- **FAQ MANAGEMENT**: CRUD table with inline editing
- **CHAT HISTORY**: Session list → Message viewer

---

## 🛠️ Setup Instructions

### Prerequisites
- **Python 3.8+** - Required for backend
- **Node.js 16+** - Required for frontend
- **Docker & Docker Compose** - Required for Milvus, MinIO, and etcd
- **Ollama** (Optional) - For LLM-powered responses ([Install Ollama](https://ollama.ai))

### Step 1: Start Docker Services

The application requires Milvus (vector database), MinIO (document storage), and etcd (configuration) services:

```bash
# Navigate to project root
cd Chat_bot

# Start all Docker services
docker compose up -d
```

This will start:
- **Milvus** - Vector database (Port 19530)
- **MinIO** - Object storage (Ports 9000, 9001)
- **etcd** - Configuration store (Port 2379)
- **Attu** - Milvus admin UI (Port 3001)

Verify services are running:
```bash
docker ps
```

### Step 2: Install Ollama (Optional but Recommended)

For intelligent LLM responses:

1. Download and install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the gemma3 model:
   ```bash
   ollama pull gemma3
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

**Note:** Without Ollama, the chatbot will return raw document chunks instead of generated answers.

### Step 3: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

4. (Optional) Initialize sample FAQs:
   ```bash
   python create_faqs.py
   ```

5. Start the FastAPI backend:
   ```bash
   cd app
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Or from the backend directory:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend API will be available at **`http://localhost:8000`**

### Step 4: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

The frontend will be available at **`http://localhost:3000`**

## 🎯 Quick Start

Once everything is running:

1. **Access the Chat Interface** → [http://localhost:3000](http://localhost:3000)
2. **Upload a PDF document** using the upload button
3. **Ask questions** about the uploaded document
4. **Access Admin Panel** → [http://localhost:3000/admin](http://localhost:3000/admin)
5. **View Milvus Collections** → [http://localhost:3001](http://localhost:3001) (Attu UI)

## 📚 Core Features Explained

### 1. RAG (Retrieval-Augmented Generation)

The RAG pipeline enables the chatbot to answer questions based on uploaded PDF documents:

**How it works:**
1. **Document Upload** → User uploads a PDF via `/rag/upload-pdf`
2. **Text Extraction** → PyMuPDF extracts text from the PDF
3. **Chunking** → Text is split into manageable chunks (configurable size)
4. **Embedding** → Each chunk is converted to a 384-dimensional vector using `all-MiniLM-L6-v2`
5. **Storage** → Vectors stored in Milvus, original PDFs in MinIO
6. **Query** → User asks a question via `/rag/ask`
7. **Query Embedding** → Question is embedded using the same model
8. **Retrieval** → Milvus finds the top-k most similar chunks (vector search)
9. **Generation** → Ollama LLM generates a natural answer from retrieved context

**Key Benefits:**
- ✅ Answers questions from your own documents
- ✅ Semantic search (understands meaning, not just keywords)
- ✅ Contextual responses from LLM
- ✅ Scalable vector search with Milvus

### 2. Conversation Flow System

Node-based conversation graph with fuzzy matching:

- **Nodes** - Conversation states with trigger text and responses
- **Edges** - Transitions between nodes based on user choices
- **Fuzzy Matching** - Uses RapidFuzz to match similar user inputs (80% threshold)
- **Entry Nodes** - Starting points for conversation flows

### 3. FAQ Management

Dynamic FAQ system with CRUD operations:
- Create, Read, Update, Delete FAQs
- Category-based organization
- Integration with admin panel

## 🔌 API Endpoints

### RAG Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rag/upload-pdf` | Upload and process a PDF document |
| `POST` | `/rag/ask` | Ask a question about uploaded documents |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/message` | Send a message and get chatbot response |
| `GET` | `/` | Health check |

### FAQ Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/faqs` | Get all FAQs |
| `POST` | `/faqs` | Create a new FAQ |
| `PUT` | `/faqs/{id}` | Update an existing FAQ |
| `DELETE` | `/faqs/{id}` | Delete a FAQ |

### Node/Edge Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/nodes` | Get all conversation nodes |
| `POST` | `/nodes` | Create a new node |
| `PUT` | `/nodes/{id}` | Update a node |
| `DELETE` | `/nodes/{id}` | Delete a node |
| `POST` | `/edges` | Create a new edge |
| `DELETE` | `/edges/{id}` | Delete an edge |

## 🔧 API Documentation

Once the backend is running, FastAPI provides interactive API documentation:

- **Swagger UI** → [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** → [http://localhost:8000/redoc](http://localhost:8000/redoc)

## ⚙️ Configuration

### RAG Configuration (`backend/app/rag/config.py`)

```python
# Milvus Collection
COLLECTION_NAME = "rag_documents"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

# MinIO Configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET_NAME = "pdf-documents"
```

### Environment Variables

You can override default configurations using environment variables:

- `DATABASE_URL` - SQLAlchemy database connection string
- `MILVUS_HOST` - Milvus server host (default: localhost)
- `MILVUS_PORT` - Milvus server port (default: 19530)

## 🐳 Docker Services

The `docker-compose.yml` file manages the following services:

| Service | Port(s) | Description |
|---------|---------|-------------|
| **Milvus** | 19530, 9091 | Vector database for embeddings |
| **MinIO** | 9000, 9001 | S3-compatible object storage |
| **etcd** | 2379 | Distributed key-value store for Milvus |
| **Attu** | 3001 | Milvus admin UI |

**Useful Commands:**
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Remove volumes (reset data)
docker compose down -v
```

## 📖 Additional Documentation

- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Detailed administrator guide for managing the system

## 🧪 Development

### Backend Development

**Structure:**
- The FastAPI server supports hot reloading with `--reload` flag
- API documentation is auto-generated from Pydantic schemas
- Database models defined in `models.py` (SQLAlchemy ORM)
- Request/response validation in `schemas.py` (Pydantic)
- RAG pipeline is modular and extensible

**Adding New Features:**
1. Define models in `models.py`
2. Create schemas in `schemas.py`
3. Implement endpoints in `main.py` or create new routers
4. RAG extensions go in `backend/app/rag/`

**Testing:**
```bash
# Run backend with auto-reload
uvicorn app.main:app --reload

# Access interactive API docs
http://localhost:8000/docs
```

### Frontend Development

**Structure:**
- Next.js 16 with App Router (app directory)
- Tailwind CSS for styling with utility-first approach
- React 19 with modern hooks and components
- React Flow for conversation graph visualization

**Development Features:**
- Hot reloading enabled by default
- Global styles in `styles/globals.css`
- Tailwind configuration in `tailwind.config.js`
- API calls to FastAPI backend via fetch

**Adding New Pages:**
```bash
# Create a new route
frontend/app/your-route/page.js
```

## 🚀 Production Deployment

### Backend Deployment

1. **Disable reload mode:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Use Gunicorn with Uvicorn workers:**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Environment variables:**
   - Set `DATABASE_URL` for production database
   - Configure `OLLAMA_URL` for remote Ollama instance
   - Update CORS origins in `main.py`

### Frontend Deployment

1. **Build for production:**
   ```bash
   npm run build
   ```

2. **Start production server:**
   ```bash
   npm start
   ```

3. **Deploy to Vercel/Netlify:**
   - Connect your Git repository
   - Set build command: `npm run build`
   - Set output directory: `.next`

## 🔍 Troubleshooting

### Common Issues

**1. Milvus Connection Error**
```
[WARNING] Could not connect to Milvus
```
**Solution:** Ensure Docker services are running:
```bash
docker compose up -d
docker ps  # Verify milvus container is running
```

**2. Ollama Not Found**
```
Cannot connect to Ollama at http://localhost:11434
```
**Solution:** 
- Install Ollama from https://ollama.ai
- Run `ollama serve`
- Pull the model: `ollama pull gemma3`

**3. Frontend Can't Connect to Backend**
```
Failed to fetch from http://localhost:8000
```
**Solution:**
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Ensure ports 8000 and 3000 are not blocked

**4. PDF Upload Fails**
```
MinIO upload failed
```
**Solution:**
- Check MinIO is running: `docker ps | grep minio`
- Verify MinIO credentials in `config.py`
- Check MinIO logs: `docker logs milvus-minio`

**5. Empty Responses from RAG**
```
I couldn't find relevant information
```
**Solution:**
- Upload a PDF document first
- Check Milvus has data: Access Attu UI at http://localhost:3001
- Verify embedding model downloaded correctly

## 📊 Performance Tuning

### Vector Search Optimization

In `retriever.py`, adjust these parameters:

```python
def retrieve(query: str, top_k=5, threshold=0.2):
    # top_k: Number of results to retrieve (higher = more context, slower)
    # threshold: Minimum similarity score (0.0-1.0, higher = stricter)
```

### Chunking Strategy

In `chunker.py`, optimize chunk size:
- Smaller chunks = more precise retrieval
- Larger chunks = more context per result

### Embedding Model

To use a different model, update `embedder.py`:
```python
_model = SentenceTransformer("all-mpnet-base-v2")  # Larger, more accurate
# Or
_model = SentenceTransformer("all-MiniLM-L6-v2")   # Faster, smaller
```

## � Dependencies

### Backend (Python)

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for building APIs |
| `uvicorn[standard]` | ASGI server for FastAPI |
| `sqlalchemy` | SQL toolkit and ORM |
| `psycopg2-binary` | PostgreSQL adapter |
| `python-dotenv` | Environment variable management |
| `rapidfuzz` | Fuzzy string matching |
| `pymilvus` | Milvus vector database client |
| `sentence-transformers` | Embedding model (all-MiniLM-L6-v2) |
| `pypdf` | PDF text extraction |
| `python-multipart` | File upload support |
| `requests` | HTTP client for Ollama |
| `minio` | MinIO Python SDK |

### Frontend (Node.js)

| Package | Purpose |
|---------|---------|
| `next@16` | React framework |
| `react@19` | UI library |
| `react-dom@19` | React DOM renderer |
| `reactflow` | Conversation graph visualization |
| `tailwindcss` | Utility-first CSS framework |
| `autoprefixer` | PostCSS plugin for vendor prefixes |
| `postcss` | CSS transformation tool |

## 🎓 Learning Resources

### RAG & Vector Search
- [Milvus Documentation](https://milvus.io/docs)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Explained](https://huggingface.co/docs/transformers/model_doc/rag)

### Frameworks
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)

### LLM Integration
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Gemma Model](https://ollama.ai/library/gemma3)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes:**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React code
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the **MIT License**.

## 📧 Support

For support, questions, or feedback:

- 📖 Check the [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for detailed usage instructions
- 🐛 Open an issue on GitHub for bug reports
- 💡 Submit feature requests via GitHub Issues
- 📚 Review API documentation at http://localhost:8000/docs

## 🙏 Acknowledgments

- **Milvus** - For the powerful vector database
- **Sentence Transformers** - For state-of-the-art embeddings
- **Ollama** - For easy local LLM deployment
- **FastAPI** - For the excellent web framework
- **Next.js Team** - For the amazing React framework

---

**Built with ❤️ using RAG technology**
