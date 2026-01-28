# Intelligent Chat Bot with RAG (Retrieval-Augmented Generation)

A full-stack intelligent chatbot application powered by **RAG (Retrieval-Augmented Generation)** technology. The system features PDF document ingestion, semantic search using vector embeddings, conversational AI with Ollama LLM, FAQ management, and an admin panel for managing conversation flows.

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

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                   (Next.js Frontend - Port 3000)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (Port 8000)                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Chat Engine   │  │   RAG Pipeline │  │  FAQ Management  │  │
│  │  (Fuzzy Match) │  │   (Semantic)   │  │   (CRUD API)     │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└──────────┬─────────────────┬──────────────────┬─────────────────┘
           │                 │                  │
           ▼                 ▼                  ▼
    ┌──────────┐      ┌─────────────┐    ┌────────────┐
    │SQLAlchemy│      │   Milvus    │    │   MinIO    │
    │   ORM    │      │   Vector    │    │  Document  │
    │          │      │  Database   │    │  Storage   │
    └──────────┘      └─────────────┘    └────────────┘
                            │
                            ▼
                      ┌──────────┐
                      │  Ollama  │
                      │   LLM    │
                      │ (gemma3) │
                      └──────────┘
```

## 📁 Project Structure

```
Chat_bot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & chat logic
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models (Node, Edge, FAQ, ChatMessage)
│   │   ├── schemas.py           # Pydantic schemas for API validation
│   │   └── rag/                 # RAG Pipeline Module
│   │       ├── __init__.py
│   │       ├── config.py        # RAG configuration (Milvus, MinIO, Ollama)
│   │       ├── rag_pipeline.py  # Main pipeline (ingest_pdf, ask_question)
│   │       ├── pdf_loader.py    # PDF text extraction
│   │       ├── chunker.py       # Text chunking strategy
│   │       ├── embedder.py      # Sentence Transformer embeddings
│   │       ├── collection.py    # Milvus collection management
│   │       ├── retriever.py     # Vector similarity search
│   │       ├── ollama_client.py # Ollama LLM integration
│   │       ├── milvus_client.py # Milvus connection utilities
│   │       ├── minio_client.py  # MinIO storage client
│   │       └── routes.py        # RAG API endpoints (/rag/upload-pdf, /rag/ask)
│   ├── create_faqs.py           # FAQ initialization script
│   ├── migrate_db.py            # Database migration utilities
│   └── migrate_postgres.py      # PostgreSQL migration
├── frontend/
│   ├── app/
│   │   ├── layout.js            # Root layout component
│   │   ├── page.js              # Chat interface (main page)
│   │   └── admin/
│   │       └── page.js          # Admin panel for FAQ/Node management
│   ├── styles/
│   │   └── globals.css          # Global Tailwind styles
│   ├── package.json             # Node dependencies
│   ├── postcss.config.js        # PostCSS configuration
│   └── tailwind.config.js       # Tailwind CSS configuration
├── docker-compose.yml           # Docker services (Milvus, MinIO, etcd, Attu)
├── requirements.txt             # Python dependencies
├── ADMIN_GUIDE.md              # Administrator documentation
└── README.md                   # This file
```

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
