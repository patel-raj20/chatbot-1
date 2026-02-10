# RabbitMQ + Worker + Redis Pub/Sub + WebSocket Integration Guide

## 📋 Overview

This guide documents the complete integration of RabbitMQ, Worker, Redis Pub/Sub, and WebSockets for scalable, real-time streaming RAG responses in your FastAPI chatbot.

## 🏗️ Architecture

```
┌─────────────┐     HTTP POST      ┌─────────────┐
│   Client    │ ───────────────────>│  FastAPI    │
│  (Browser)  │                     │   Backend   │
└─────────────┘                     └─────────────┘
       │                                    │
       │                                    │ Publish Job
       │                                    ▼
       │                            ┌─────────────┐
       │                            │  RabbitMQ   │
       │                            │    Queue    │
       │                            └─────────────┘
       │                                    │
       │                                    │ Worker Pulls
       │                                    ▼
       │                            ┌─────────────┐
       │                            │  RAG Worker │
       │                            │   Service   │
       │                            └─────────────┘
       │                                    │
       │                                    │ Publish Tokens
       │                                    ▼
       │                            ┌─────────────┐
       │                            │   Redis     │
       │                            │   Pub/Sub   │
       │                            └─────────────┘
       │                                    │
       │     WebSocket                      │ Subscribe
       │    Connection                      │
       ▼                                    ▼
┌─────────────┐                     ┌─────────────┐
│  WebSocket  │<────────────────────│  WebSocket  │
│  Endpoint   │   Forward Tokens    │   Handler   │
└─────────────┘                     └─────────────┘
```

## 🔄 Request Flow

### Step-by-Step Process

1. **Client sends HTTP POST** to `/rag/ask-stream` with question
2. **Backend generates** unique `request_id`
3. **Backend pushes job** to RabbitMQ queue
4. **Backend returns** `request_id` and WebSocket URL to client
5. **Client connects** to WebSocket with `request_id`
6. **Worker pulls job** from RabbitMQ
7. **Worker executes RAG** (retrieve context + stream Groq LLM)
8. **Worker publishes tokens** to Redis Pub/Sub channel `chat_stream:{request_id}`
9. **WebSocket subscribes** to Redis Pub/Sub channel
10. **WebSocket forwards tokens** to client in real-time
11. **Worker publishes "done"** signal when complete
12. **WebSocket closes** connection

## 📁 Project Structure

```
backend/
├── app/
│   ├── queue/                    # NEW: RabbitMQ & Pub/Sub
│   │   ├── __init__.py
│   │   ├── rabbitmq_client.py   # RabbitMQ client for job queueing
│   │   └── pubsub_service.py    # Redis Pub/Sub for streaming
│   ├── rag/
│   │   ├── ollama_client_streaming.py  # NEW: Streaming Groq client
│   │   ├── pipeline_streaming.py       # NEW: Streaming RAG pipeline
│   │   └── routes.py            # MODIFIED: Added /ask-stream endpoint
│   ├── routes/
│   │   └── websocket.py         # NEW: WebSocket routes
│   ├── core/
│   │   └── config.py            # MODIFIED: Added RabbitMQ settings
│   └── main.py                  # MODIFIED: Added WebSocket routes
├── worker.py                     # NEW: Worker service
└── Dockerfile                    # Used by both API and Worker
```

## 🚀 Quick Start

### 1. Environment Variables

Add to your `.env` file:

```bash
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Existing settings (keep as is)
GROQ_API_KEY=your_groq_api_key
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. Start Services with Docker

```bash
# Start all services (including RabbitMQ and Worker)
docker-compose up -d

# Check service status
docker-compose ps

# View worker logs
docker-compose logs -f worker

# View backend logs
docker-compose logs -f backend
```

### 3. Test the Integration

#### A. Using curl (HTTP + WebSocket simulation)

```bash
# Step 1: Send question via HTTP
curl -X POST http://localhost:8000/rag/ask-stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "user_id": "test-user-123",
    "session_id": "test-session-456"
  }'

# Response:
# {
#   "request_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "queued",
#   "websocket_url": "/ws/chat/550e8400-e29b-41d4-a716-446655440000"
# }

# Step 2: Connect to WebSocket (use a WebSocket client)
# ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000
```

#### B. Using Python Client

```python
import requests
import asyncio
import websockets
import json

# Step 1: Send question
response = requests.post('http://localhost:8000/rag/ask-stream', json={
    "question": "What is machine learning?",
    "user_id": "test-user-123",
    "session_id": "test-session-456"
})
data = response.json()
request_id = data['request_id']

print(f"Request ID: {request_id}")
print("Connecting to WebSocket...")

# Step 2: Connect to WebSocket and receive streaming response
async def receive_stream():
    uri = f"ws://localhost:8000/ws/chat/{request_id}"
    async with websockets.connect(uri) as websocket:
        print("Connected! Receiving tokens...\n")
        full_answer = ""
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'token':
                token = data['content']
                print(token, end='', flush=True)
                full_answer += token
            elif data['type'] == 'done':
                print("\n\nStream complete!")
                break
            elif data['type'] == 'error':
                print(f"\nError: {data['message']}")
                break
        
        print(f"\n\nFull answer: {full_answer}")

# Run the async function
asyncio.run(receive_stream())
```

#### C. Using JavaScript/Frontend

```javascript
// Step 1: Send question via HTTP
const response = await fetch('http://localhost:8000/rag/ask-stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What is machine learning?",
    user_id: "test-user-123",
    session_id: "test-session-456"
  })
});

const data = await response.json();
const requestId = data.request_id;

console.log('Request ID:', requestId);

// Step 2: Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${requestId}`);

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'token') {
    // Display token in real-time
    document.getElementById('answer').textContent += message.content;
  } else if (message.type === 'done') {
    console.log('Stream complete');
    ws.close();
  } else if (message.type === 'error') {
    console.error('Error:', message.message);
    ws.close();
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

## 🔧 Component Details

### 1. RabbitMQ Client (`app/queue/rabbitmq_client.py`)

**Purpose**: Queue management for async job processing

**Key Methods**:
- `connect()`: Establish connection to RabbitMQ
- `publish_job(job_data)`: Enqueue a RAG job
- `consume(callback)`: Start consuming jobs (worker side)
- `close()`: Cleanup connection

**Queue Configuration**:
- Exchange: `chat_exchange` (direct)
- Queue: `chat_queue`
- Routing Key: `chat.rag`

### 2. Redis Pub/Sub Service (`app/queue/pubsub_service.py`)

**Purpose**: Real-time token streaming between Worker and WebSocket

**Key Methods**:
- `publish_token(request_id, token)`: Publish a single token
- `publish_done(request_id)`: Signal completion
- `publish_error(request_id, error)`: Signal error
- `subscribe_stream(request_id)`: Subscribe to token stream (async generator)

**Channel Format**: `chat_stream:{request_id}`

### 3. RAG Worker (`backend/worker.py`)

**Purpose**: Background service that processes RAG jobs

**Workflow**:
1. Connect to RabbitMQ and Redis Pub/Sub
2. Pull jobs from RabbitMQ queue
3. Execute RAG pipeline with streaming
4. Publish each token to Redis Pub/Sub
5. Publish "done" signal
6. ACK RabbitMQ message

**Running the Worker**:
```bash
# Directly
python backend/worker.py

# With Docker
docker-compose up worker

# Scale workers (future)
docker-compose up --scale worker=3
```

### 4. WebSocket Endpoint (`app/routes/websocket.py`)

**Purpose**: Bridge between Redis Pub/Sub and client WebSocket

**Endpoint**: `WS /ws/chat/{request_id}`

**Message Types Sent to Client**:
```json
{"type": "token", "content": "Hello"}
{"type": "done"}
{"type": "error", "message": "Error details"}
```

### 5. Streaming RAG Endpoint (`app/rag/routes.py`)

**Endpoint**: `POST /rag/ask-stream`

**Request**:
```json
{
  "question": "What is machine learning?",
  "user_id": "user-uuid",
  "session_id": "session-uuid"  // optional
}
```

**Response**:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "websocket_url": "/ws/chat/550e8400-e29b-41d4-a716-446655440000",
  "message": "Job queued. Connect to WebSocket to receive streaming response."
}
```

## 📊 Monitoring & Debugging

### RabbitMQ Management UI

Access: http://localhost:15672
- Username: `guest`
- Password: `guest`

**Features**:
- View queue size
- Monitor message rates
- Check connections
- View exchanges and bindings

### Redis Commander

Access: http://localhost:8081

**Usage**:
- Monitor Pub/Sub channels
- View cache keys
- Debug Redis operations

### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f worker
docker-compose logs -f backend
docker-compose logs -f rabbitmq

# Check for errors
docker-compose logs worker | grep ERROR
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/

# Check RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview

# Check Redis
redis-cli ping

# Check queue size
docker-compose exec backend python -c "
from app.queue.rabbitmq_client import RabbitMQClient
rmq = RabbitMQClient()
rmq.connect()
print(f'Queue size: {rmq.get_queue_size()}')
rmq.close()
"
```

## ⚠️ Important Notes

### What Gets Cached (Redis Cache)

✅ **ONLY workflow-based Q&A** (traditional chatbot responses)
❌ **NEVER RAG-based answers** (as per requirements)

### Worker Responsibilities

✅ Worker DOES:
- Pull jobs from RabbitMQ
- Execute RAG pipeline
- Stream tokens via Redis Pub/Sub
- ACK messages when done

❌ Worker DOES NOT:
- Know about WebSockets
- Store RAG answers in Redis cache
- Talk to HTTP clients directly

### WebSocket Responsibilities

✅ WebSocket DOES:
- Accept client connections
- Subscribe to Redis Pub/Sub
- Forward tokens to client

❌ WebSocket DOES NOT:
- Perform RAG
- Talk to RabbitMQ
- Execute business logic

## 🔐 Security Considerations

1. **Production RabbitMQ Credentials**
   ```bash
   RABBITMQ_USER=production_user
   RABBITMQ_PASS=strong_random_password_here
   ```

2. **WebSocket Authentication** (TODO)
   - Add JWT token validation to WebSocket endpoint
   - Verify user ownership of request_id

3. **Rate Limiting** (TODO)
   - Limit requests per user
   - Prevent queue flooding

## 🚦 Scaling

### Horizontal Scaling the Worker

```bash
# Scale to 3 workers
docker-compose up --scale worker=3 -d

# RabbitMQ automatically load-balances jobs across workers
```

**Benefits**:
- Increased throughput
- Better fault tolerance
- No code changes needed

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
# Then run:
locust -f locustfile.py --host http://localhost:8000
```

## 🐛 Troubleshooting

### Issue: Worker not processing jobs

**Check**:
1. Is worker running? `docker-compose ps worker`
2. Is RabbitMQ healthy? `docker-compose ps rabbitmq`
3. Check worker logs: `docker-compose logs worker`
4. Check queue size in RabbitMQ UI

### Issue: WebSocket not receiving tokens

**Check**:
1. Is Redis running? `docker-compose ps redis`
2. Is worker publishing to Pub/Sub? (check worker logs)
3. Is WebSocket subscribed to correct channel?
4. Check Redis Pub/Sub channels: `redis-cli pubsub channels "chat_stream:*"`

### Issue: Connection timeouts

**Check**:
1. Firewall settings
2. Docker network configuration
3. Environment variables (HOST settings)

### Issue: Tokens arriving out of order

**Solution**: This shouldn't happen with Redis Pub/Sub (ordered delivery guaranteed). If it does:
1. Check Redis version (should be 7+)
2. Check network latency
3. Review client-side message handling

## 📝 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/rag/ask` | Synchronous RAG (returns complete answer) |
| POST | `/rag/ask-stream` | Async RAG (returns request_id) |
| WS | `/ws/chat/{request_id}` | Stream tokens to client |
| POST | `/rag/upload-pdf` | Upload PDF for RAG |
| GET | `/rag/debug` | RAG system statistics |

## 🎯 Future Enhancements

1. **Authentication**
   - Add JWT validation to WebSocket
   - User-specific rate limiting

2. **Persistence**
   - Save streaming answers to database
   - Replay capability for disconnected clients

3. **Advanced Features**
   - Pause/resume streaming
   - Priority queues for premium users
   - Multi-model support

4. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert on queue size thresholds

## 📚 Additional Resources

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Pub/Sub Guide](https://redis.io/docs/manual/pubsub/)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Groq API](https://console.groq.com/docs)

## ✅ Checklist for Deployment

- [ ] Update `.env` with production credentials
- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Configure CORS allowed origins
- [ ] Set up monitoring/logging
- [ ] Test WebSocket connections
- [ ] Test worker scaling
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS for WebSocket
- [ ] Enable RabbitMQ clustering (optional)
- [ ] Set up Redis persistence (optional)

---

**Integration Complete!** 🎉

Your chatbot now supports scalable, real-time streaming RAG responses with minimal changes to existing structure.
