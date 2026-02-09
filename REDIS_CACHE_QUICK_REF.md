# Redis Cache - Quick Reference

## 🚀 Quick Start

Redis caching is **already running** and working automatically!

## 📋 Quick Commands

### Check Redis Status
```bash
docker ps --filter name=chatbot-redis
docker exec chatbot-redis redis-cli ping
```

### View Backend Logs (Cache Activity)
```bash
docker logs chatbot-backend -f | grep CACHE
```

### Restart Services
```bash
docker-compose restart redis backend
```

### Access Redis CLI
```bash
docker exec -it chatbot-redis redis-cli

## Inside Redis CLI:
KEYS chatbot:qa:*        # List all cached questions
GET chatbot:qa:<hash>    # View a cached answer
TTL chatbot:qa:<hash>    # Check time-to-live
FLUSHDB                  # Clear all cache (use carefully!)
```

## ⚙️ Configuration (.env)

```bash
# Enable/Disable Cache
CACHE_ENABLED=true

# Cache Expiration (in seconds)
CACHE_TTL=600          # 10 minutes (default)
CACHE_TTL=1800         # 30 minutes
CACHE_TTL=3600         # 1 hour

# Redis Connection
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

## 📊 Log Examples

### Cache HIT (Fast Response)
```
✓ CACHE HIT | Question: 'What is AI?...' | Cache: 5.50ms | Total: 12.30ms
```
→ Answer served from Redis (very fast!)

### Cache MISS (First Request)
```
✗ CACHE MISS | Question: 'What is AI?...' | DB retrieval: 234.80ms
```
→ Answer fetched from database and cached for future requests

## 🔍 Testing Cache

### Test 1: Send same question twice
```bash
# First request (MISS)
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "What is AI?"
  }'

# Second request (HIT - much faster!)
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-456",
    "message": "What is AI?"
  }'
```

### Test 2: Check cache keys in Redis
```bash
docker exec chatbot-redis redis-cli KEYS "chatbot:qa:*"
```

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| All requests show CACHE MISS | Check `CACHE_ENABLED=true` in `.env` |
| Redis connection error | Run `docker-compose restart redis backend` |
| Cache not clearing | Check TTL setting or manually flush: `docker exec chatbot-redis redis-cli FLUSHDB` |

## 📈 Performance

| Metric | Value |
|--------|-------|
| Cache HIT response time | 5-20ms |
| Cache MISS (DB) response time | 200-500ms |
| Cache TTL (default) | 600 seconds (10 minutes) |
| Connection pool size | 50 connections |

## ✅ What's Cached

- ✅ FAQ answers
- ✅ Entry node responses
- ✅ Fuzzy-matched questions
- ✅ First-time questions (after initial query)

## ❌ What's NOT Cached

- ❌ Node navigation (button clicks)
- ❌ User credentials
- ❌ Session data
- ❌ JWT tokens

## 🎯 Key Points

1. **Automatic**: Works without any code changes
2. **Safe**: Falls back gracefully if Redis fails
3. **Global**: Same question → same cached answer (across all users)
4. **Smart**: Normalizes questions (case-insensitive, whitespace-trimmed)
5. **Fast**: 10-50x faster than database queries

## 📖 Full Documentation

See `REDIS_CACHE_IMPLEMENTATION.md` for complete details.
