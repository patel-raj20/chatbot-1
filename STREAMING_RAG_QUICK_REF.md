# Quick Reference: Streaming RAG Integration

## 🚀 Quick Start Commands

```bash
# Start all services
docker-compose up -d

# View worker logs
docker-compose logs -f worker

# Check service health
docker-compose ps

# Restart services
docker-compose restart backend worker
```

## 📡 Key Endpoints

### 1. Streaming RAG (Async)
```http
POST /rag/ask-stream
Content-Type: application/json

{
  "question": "What is ML?",
  "user_id": "user-123",
  "session_id": "session-456"
}

Response:
{
  "request_id": "uuid",
  "status": "queued",
  "websocket_url": "/ws/chat/{request_id}"
}
```

### 2. WebSocket Connection
```javascript
ws://localhost:8000/ws/chat/{request_id}

// Messages received:
{"type": "token", "content": "Hello"}
{"type": "done"}
{"type": "error", "message": "..."}
```

### 3. Traditional RAG (Sync)
```http
POST /rag/ask?query=What is ML?&session_id=abc

Response:
{
  "answer": "Machine learning is..."
}
```

## 🔄 Data Flow

```
HTTP → Backend → RabbitMQ → Worker → Redis Pub/Sub → WebSocket → Client
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/worker.py` | Worker service (processes jobs) |
| `app/queue/rabbitmq_client.py` | RabbitMQ job queueing |
| `app/queue/pubsub_service.py` | Redis Pub/Sub streaming |
| `app/routes/websocket.py` | WebSocket endpoint |
| `app/rag/routes.py` | RAG endpoints (added /ask-stream) |
| `app/rag/pipeline_streaming.py` | Streaming RAG pipeline |
| `docker-compose.yml` | Services config (added RabbitMQ + Worker) |

## 🧪 Testing

### Python Client
```python
import requests, asyncio, websockets, json

# 1. Send question
r = requests.post('http://localhost:8000/rag/ask-stream', json={
    "question": "What is ML?",
    "user_id": "test-user",
    "session_id": "test-session"
})
request_id = r.json()['request_id']

# 2. Connect to WebSocket
async def stream():
    uri = f"ws://localhost:8000/ws/chat/{request_id}"
    async with websockets.connect(uri) as ws:
        async for msg in ws:
            data = json.loads(msg)
            if data['type'] == 'token':
                print(data['content'], end='', flush=True)
            elif data['type'] == 'done':
                break

asyncio.run(stream())
```

### JavaScript Client
```javascript
const res = await fetch('http://localhost:8000/rag/ask-stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: "What is ML?",
    user_id: "test-user"
  })
});

const {request_id} = await res.json();
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${request_id}`);

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === 'token') console.log(msg.content);
  if (msg.type === 'done') ws.close();
};
```

## 🐛 Debugging

### Check Queue Size
```bash
docker-compose exec backend python -c "
from app.queue.rabbitmq_client import RabbitMQClient
rmq = RabbitMQClient()
rmq.connect()
print(f'Queue size: {rmq.get_queue_size()}')
"
```

### Check Worker Status
```bash
# Is worker running?
docker-compose ps worker

# Worker logs
docker-compose logs -f worker | grep -E "(Job received|completed|ERROR)"
```

### Check Redis Pub/Sub
```bash
# Check active channels
docker-compose exec redis redis-cli pubsub channels "chat_stream:*"

# Monitor messages
docker-compose exec redis redis-cli --csv psubscribe "chat_stream:*"
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required for streaming
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Required for RAG
GROQ_API_KEY=your_key_here
REDIS_HOST=localhost
```

### Scaling Workers
```bash
# Scale to N workers
docker-compose up --scale worker=3 -d

# RabbitMQ auto-balances load
```

## 🎯 Architecture Components

### 1. RabbitMQ
- **Purpose**: Queue RAG jobs
- **Queue**: `chat_queue`
- **Exchange**: `chat_exchange` (direct)
- **UI**: http://localhost:15672 (guest/guest)

### 2. Worker
- **Purpose**: Process RAG jobs
- **Input**: RabbitMQ messages
- **Output**: Redis Pub/Sub tokens
- **Scaling**: Horizontal (add more workers)

### 3. Redis Pub/Sub
- **Purpose**: Real-time token streaming
- **Channel**: `chat_stream:{request_id}`
- **Messages**: `{"type": "token", "content": "..."}`, `{"type": "done"}`

### 4. WebSocket
- **Purpose**: Bridge Pub/Sub → Client
- **Endpoint**: `/ws/chat/{request_id}`
- **Protocol**: WebSocket (ws://)

## ⚠️ Important Notes

### Redis Cache vs Pub/Sub
- **Cache** (workflow Q&A): Persistent, TTL-based
- **Pub/Sub** (RAG streaming): Ephemeral, real-time
- **RAG answers**: NOT cached (as per requirements)

### Worker Isolation
- Worker does NOT know about WebSockets
- Worker does NOT cache RAG answers
- Worker ONLY: RabbitMQ → RAG → Pub/Sub

## 🔍 Monitoring URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| RabbitMQ UI | http://localhost:15672 | guest/guest |
| Redis Commander | http://localhost:8081 | - |
| Hasura | http://localhost:8080 | admin secret |
| Milvus Attu | http://localhost:3001 | - |

## 📊 Message Formats

### RabbitMQ Job
```json
{
  "request_id": "uuid",
  "user_id": "uuid",
  "question": "What is ML?",
  "session_id": "uuid"
}
```

### Redis Pub/Sub Token
```json
{"type": "token", "content": "Machine"}
```

### Redis Pub/Sub Done
```json
{"type": "done"}
```

### Redis Pub/Sub Error
```json
{"type": "error", "message": "Error details"}
```

## 🚨 Troubleshooting

### Worker not processing jobs
1. Check: `docker-compose ps worker` (should be "Up")
2. Check: `docker-compose logs worker` (look for errors)
3. Check: RabbitMQ UI → Queues → `chat_queue` (should have messages)

### WebSocket not receiving tokens
1. Check: Worker published to Pub/Sub (worker logs)
2. Check: Redis is running (`docker-compose ps redis`)
3. Check: Channel name matches (`chat_stream:{request_id}`)

### Connection refused
1. Check: `.env` has correct HOST values (use service names in Docker)
2. Check: All services are up (`docker-compose ps`)
3. Check: Networks are correct (all should be in `chatbot-network`)

---

**Need more details?** See [STREAMING_RAG_INTEGRATION_GUIDE.md](./STREAMING_RAG_INTEGRATION_GUIDE.md)
