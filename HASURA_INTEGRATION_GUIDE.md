# Hasura Integration Guide
## JWT-Based Authorization for Chatbot Application

---

## 📋 Overview

This guide explains how to integrate Hasura GraphQL Engine with your chatbot application to enforce role-based authorization using JWT tokens.

**Architecture:**
- **Authentication**: Handled by FastAPI (signup/login endpoints)
- **Authorization**: Enforced by Hasura GraphQL Engine
- **Backend**: Does NOT check authorization (only authenticates users)
- **JWT Claims**: Include Hasura-compatible claims for permission enforcement

---

## 🎯 Why Hasura?

Hasura provides:
1. **Automatic GraphQL API** generation from your PostgreSQL database
2. **Row-level security** based on JWT claims
3. **Role-based permissions** without custom backend code
4. **Real-time subscriptions** (if needed in future)

---

## 🔧 Step 1: Install Hasura

### Using Docker (Recommended)

Add Hasura service to your `docker-compose.yml`:

```yaml
services:
  # ... existing services (postgres, backend, frontend)
  
  hasura:
    image: hasura/graphql-engine:latest
    ports:
      - "8080:8080"
    environment:
      # Connect to existing PostgreSQL database
      HASURA_GRAPHQL_DATABASE_URL: postgresql://user:password@postgres:5432/chatbot
      
      # Enable console for development
      HASURA_GRAPHQL_ENABLE_CONSOLE: "true"
      
      # Admin secret (change in production!)
      HASURA_GRAPHQL_ADMIN_SECRET: "your-hasura-admin-secret"
      
      # JWT Configuration
      HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"your-secret-key-change-this-in-production-use-minimum-32-characters"}'
      
      # Enable unauthorized role for public access (optional)
      # HASURA_GRAPHQL_UNAUTHORIZED_ROLE: "anonymous"
      
    depends_on:
      - postgres
```

**IMPORTANT:** The `HASURA_GRAPHQL_JWT_SECRET` key MUST match the `JWT_SECRET_KEY` in your FastAPI auth utils!

### Start Hasura

```bash
docker-compose up -d hasura
```

Access Hasura Console at: **http://localhost:8080/console**

---

## 🔌 Step 2: Connect Hasura to PostgreSQL

Hasura should automatically connect using `HASURA_GRAPHQL_DATABASE_URL`.

### Verify Connection:

1. Open Hasura Console: http://localhost:8080/console
2. Go to **Data** tab
3. You should see your existing tables:
   - `users`
   - `nodes`
   - `edges`
   - `chat_messages`
   - `faqs`
   - `pdf_documents`

If tables aren't visible, click **Track All** to expose them via GraphQL.

---

## 🔐 Step 3: Configure JWT Mode

### Understanding JWT Claims

Your FastAPI auth system generates JWT tokens with this structure:

```json
{
  "sub": "user-uuid-123",
  "username": "john_doe",
  "role": "user",
  "exp": 1707500000,
  "https://hasura.io/jwt/claims": {
    "x-hasura-user-id": "user-uuid-123",
    "x-hasura-default-role": "user",
    "x-hasura-allowed-roles": ["user", "admin"]
  }
}
```

**Key Claims:**
- `x-hasura-user-id`: User's database ID (used in permission rules)
- `x-hasura-default-role`: Role to use for this request
- `x-hasura-allowed-roles`: All roles user can assume

### JWT Secret Configuration

In your `docker-compose.yml`:

```yaml
HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"your-secret-key-here"}'
```

**Match this key with FastAPI's `JWT_SECRET_KEY`!**

---

## 🛡️ Step 4: Define Roles

Hasura supports two custom roles in this application:

### 1. **user** Role
- Can access chatbot functionality
- Can view/create own chat messages
- Can view FAQs
- **Cannot** access admin features

### 2. **admin** Role
- Full access to all tables
- Can create/edit/delete nodes, edges, FAQs
- Can view all chat messages (all sessions)
- Can upload/manage documents

---

## 📊 Step 5: Configure Table Permissions

### Example: `chat_messages` Table

#### **user** Role Permissions

**Select (Read):**
- ✅ Allow users to see their own messages
- **Custom Check:**
  ```json
  {
    "session_id": {
      "_eq": "X-Hasura-User-Id"
    }
  }
  ```
  *(Optional: adjust based on how you want to scope sessions)*

- **Columns Allowed:**
  - `id`, `session_id`, `sender`, `message_text`, `created_at`

**Insert (Create):**
- ✅ Allow users to create chat messages
- **Custom Check:**
  ```json
  {
    "session_id": {
      "_eq": "X-Hasura-User-Id"
    }
  }
  ```
- **Columns Allowed:**
  - `session_id`, `sender`, `message_text`, `node_id`

**Update/Delete:**
- ❌ Users cannot update or delete messages

---

#### **admin** Role Permissions

**Select (Read):**
- ✅ Allow without any checks (admin sees everything)
- **Custom Check:** `{}`

**Insert/Update/Delete:**
- ✅ Full access for admin

---

### Example: `nodes` Table

#### **user** Role
- **Select:** ✅ (users can see conversation nodes)
- **Insert/Update/Delete:** ❌ (only admins can modify workflow)

#### **admin** Role
- **Select/Insert/Update/Delete:** ✅ (full control)

---

### Example: `faqs` Table

#### **user** Role
- **Select:** ✅ (where `is_active = true`)
  ```json
  {
    "is_active": {
      "_eq": true
    }
  }
  ```

#### **admin** Role
- **Select/Insert/Update/Delete:** ✅ (full control)

---

### Example: `users` Table

#### **user** Role
- **Select:** ✅ (only own user record)
  ```json
  {
    "id": {
      "_eq": "X-Hasura-User-Id"
    }
  }
  ```
- **Update:** ✅ (only own profile, exclude `role` column)
- **Columns:** `id`, `username`, `created_at` (NOT `hashed_password` or `role`)

#### **admin** Role
- **Select/Update:** ✅ (can view/edit all users)
- **Special:** Can update `role` column to promote users to admin

---

## 🚀 Step 6: Frontend Integration

Update your frontend to send JWT tokens in GraphQL requests:

### Using Apollo Client (if adding GraphQL):

```javascript
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { getToken } from './auth';

const httpLink = createHttpLink({
  uri: 'http://localhost:8080/v1/graphql',
});

const authLink = setContext((_, { headers }) => {
  const token = getToken();
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  }
});

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache()
});
```

### Using Fetch API:

```javascript
import { getAuthHeaders } from './auth';

const response = await fetch('http://localhost:8080/v1/graphql', {
  method: 'POST',
  headers: getAuthHeaders(),
  body: JSON.stringify({
    query: `
      query GetChatMessages($sessionId: uuid!) {
        chat_messages(where: {session_id: {_eq: $sessionId}}) {
          id
          sender
          message_text
          created_at
        }
      }
    `,
    variables: { sessionId: '...' }
  })
});
```

---

## 🔄 Step 7: Testing Authorization

### Test as User:

1. **Signup** via `/auth/signup`
2. **Login** via `/auth/login` → receive JWT token
3. Use token in Hasura Console:
   - Go to **GraphiQL** tab
   - Click **Request Headers**
   - Add:
     ```json
     {
       "Authorization": "Bearer <your-jwt-token>"
     }
     ```
4. Try queries:
   ```graphql
   query {
     chat_messages {
       id
       message_text
     }
   }
   ```
   ✅ Should only see own messages

### Test as Admin:

1. **Manually promote user to admin**:
   ```sql
   -- Connect to PostgreSQL
   docker exec -it <postgres-container> psql -U user -d chatbot
   
   -- Update user role
   UPDATE users SET role = 'admin' WHERE username = 'your_username';
   ```

2. **Login again** to get new JWT with admin role
3. Try admin query in Hasura:
   ```graphql
   query {
     users {
       id
       username
       role
     }
   }
   ```
   ✅ Admin should see all users

---

## 🛠️ Step 8: Manual Admin Role Assignment

Since there's no admin promotion UI, use one of these methods:

### Method 1: Direct Database Update

```sql
-- SSH/Connect to PostgreSQL container
docker exec -it chatbot_postgres psql -U chatbot_user -d chatbot

-- Promote user to admin
UPDATE users 
SET role = 'admin' 
WHERE username = 'admin_username';
```

### Method 2: Create Admin Script

**`backend/create_admin.py`:**
```python
"""
Script to promote a user to admin role
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User

def promote_to_admin(username: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        user.role = 'admin'
        db.commit()
        
        print(f"✅ User '{username}' promoted to admin")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_admin.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    promote_to_admin(username)
```

**Run:**
```bash
python backend/create_admin.py john_doe
```

---

## 📝 Permission Rules Summary

| Table          | user Role                     | admin Role         |
|----------------|-------------------------------|--------------------|
| `users`        | Read/Update own record        | Full access        |
| `nodes`        | Read only                     | Full access        |
| `edges`        | Read only                     | Full access        |
| `chat_messages`| Read/Create own messages      | Full access        |
| `faqs`         | Read active FAQs              | Full access        |
| `pdf_documents`| Read only                     | Full access        |

---

## 🔍 Debugging Tips

### JWT Not Working?

1. **Check secret key matches:**
   - FastAPI: `backend/app/auth/utils.py` → `SECRET_KEY`
   - Hasura: `docker-compose.yml` → `HASURA_GRAPHQL_JWT_SECRET`

2. **Verify JWT structure:**
   - Use https://jwt.io to decode your token
   - Ensure `https://hasura.io/jwt/claims` namespace exists

3. **Check Hasura logs:**
   ```bash
   docker logs chatbot_hasura
   ```

### Permissions Not Working?

1. **Verify role in JWT:**
   - Decode token, check `x-hasura-default-role`

2. **Check permission rules:**
   - Go to Hasura Console → Data → [table] → Permissions
   - Ensure role is configured

3. **Test with admin secret:**
   - Add `x-hasura-admin-secret` header with your admin secret
   - If it works, issue is with JWT/permissions

---

## 🎓 Key Concepts Recap

### What Backend Does:
✅ **Authentication** (signup, login, JWT generation)
❌ **Authorization** (no role checks in FastAPI)

### What Hasura Does:
✅ **Authorization** (enforces permissions based on JWT)
✅ **GraphQL API** (auto-generated from database)
✅ **Row-level security** (users see only their data)

### JWT Flow:
1. User logs in → FastAPI generates JWT
2. Frontend stores JWT → sends with requests
3. Hasura validates JWT → enforces permissions
4. Database returns only authorized data

---

## 🚀 Next Steps

1. ✅ Verify Hasura is running: http://localhost:8080/console
2. ✅ Configure permissions for each role
3. ✅ Test with real JWT tokens
4. ✅ Create first admin user using script
5. ✅ Document permission rules for your team
6. 🔄 (Optional) Migrate REST endpoints to GraphQL

---

## 📚 Additional Resources

- **Hasura JWT Guide:** https://hasura.io/docs/latest/auth/authentication/jwt/
- **Permission Rules:** https://hasura.io/docs/latest/auth/authorization/permissions/
- **Best Practices:** https://hasura.io/docs/latest/security/best-practices/

---

**Need Help?**  
Refer to Hasura documentation or check FastAPI logs for authentication issues.
