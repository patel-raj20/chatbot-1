# 🌐 Redis Web UI - Access Guide

## ✅ Redis Commander is Now Running!

### 📍 Access URL

**Open in your browser:**
```
http://localhost:8081
```

Or click here: **[http://localhost:8081](http://localhost:8081)**

---

## 🎯 What You'll See

Redis Commander provides a web-based interface where you can:

### 1. **Browse Cache Keys**
- See all cached chatbot questions
- Keys are stored as: `chatbot:qa:<hash>`

### 2. **View Cached Values**
- Click any key to see the cached response
- JSON-formatted chatbot answers

### 3. **Monitor TTL (Time-To-Live)**
- See how long until cache expires
- Default: 600 seconds (10 minutes)

### 4. **Delete Keys**
- Manually remove cached entries
- Useful for testing or clearing stale data

### 5. **Database Info**
- View Redis memory usage
- See total number of keys
- Monitor Redis statistics

---

## 🔍 Finding Your Cached Data

### Step 1: Open Redis Commander
Go to: **http://localhost:8081**

### Step 2: Select Database
- Click on `local (redis:6379)` in the left sidebar
- Select database `0` (default)

### Step 3: Browse Keys
- Look for keys starting with `chatbot:qa:`
- These are your cached questions/answers

### Step 4: View Details
- Click any key to see:
  - Full JSON response
  - TTL (time remaining)
  - Key size

---

## 📊 Example Cache Entry

**Key:**
```
chatbot:qa:a7b3c8d9e1f2g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h0
```

**Value:**
```json
{
  "reply": "AI is artificial intelligence...",
  "node_id": "123e4567-e89b-12d3-a456-426614174000",
  "options": null
}
```

**TTL:** `573` (seconds remaining before expiration)

---

## 🛠️ Common Actions

### Clear All Cache
1. Click on database `0`
2. Click `Delete` button at top
3. Confirm deletion
4. All cache cleared!

### Delete Single Entry
1. Find the key you want to delete
2. Click the key
3. Click `Delete Key` button
4. Confirm

### Refresh View
- Click `Refresh` button to see latest data
- Auto-refresh available in settings

---

## 🔧 Troubleshooting

### Can't Access http://localhost:8081?

**Solution 1**: Check if Redis Commander is running
```bash
docker ps --filter name=redis-commander
```

**Solution 2**: Restart Redis Commander
```bash
docker-compose restart redis-commander
```

**Solution 3**: Check logs
```bash
docker logs chatbot-redis-commander
```

### No Keys Showing?

**Possible Reasons:**
1. **No questions asked yet** - Send a test question to the chatbot first
2. **Cache expired** - TTL might have expired (default 10 minutes)
3. **Wrong database** - Make sure you're viewing database `0`

**Test by sending a question:**
```bash
# Send a test question via API
curl -X POST http://localhost:8000/chat/message -H "Content-Type: application/json" -d "{\"session_id\":\"test-123\",\"message\":\"What is AI?\"}"

# Then refresh Redis Commander to see the cached entry
```

---

## 📱 Interface Overview

### Left Sidebar
- **Servers**: List of Redis connections
- **local (redis:6379)**: Your Redis instance
- **DB 0**: Your cache database

### Main Panel
- **Key List**: All keys in the database
- **Search Bar**: Find specific keys
- **Actions**: Add/Delete/Refresh

### Right Panel (when key selected)
- **Value**: Key content (JSON)
- **TTL**: Time until expiration
- **Type**: Data type (string)
- **Size**: Key size in bytes

---

## 🎨 Tips & Tricks

### 1. Search for Cache Keys
In the search box, type:
```
chatbot:qa:*
```

### 2. Monitor Cache Growth
- Refresh periodically to see new entries
- Watch TTL countdown

### 3. Test Cache Behavior
1. Ask a question in chatbot
2. Check Redis Commander - should see new key
3. Wait 10+ minutes
4. Refresh - key should disappear (expired)

### 4. Debug Cache Issues
- If cache not working, check if keys appear here
- If keys appear but chatbot shows MISS, check key format
- Compare cached value with expected response

---

## 🔗 Quick Links

- **Redis Commander**: http://localhost:8081
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Hasura Console**: http://localhost:8080

---

## 📝 Additional Commands (PowerShell)

### View Backend Logs (Cache Activity)
```powershell
docker logs chatbot-backend --tail 100 | Select-String "CACHE"
```

### Check Redis Connection
```powershell
docker exec chatbot-redis redis-cli ping
```

### Count Cache Keys
```powershell
docker exec chatbot-redis redis-cli DBSIZE
```

### View All Cache Keys
```powershell
docker exec chatbot-redis redis-cli KEYS "chatbot:qa:*"
```

---

## 🎉 You're All Set!

**Open Redis Commander now:**
👉 **[http://localhost:8081](http://localhost:8081)**

You'll be able to see all your cached chatbot responses in real-time!
