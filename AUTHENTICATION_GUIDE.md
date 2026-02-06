# JWT Authentication Integration Guide

## Overview
This project now includes JWT-based authentication with role-based access control (RBAC). Users can register accounts and login to access the chat interface. Admins have additional access to the admin panel.

---

## 🎯 Features Implemented

### Backend (FastAPI)
- ✅ User registration and login endpoints
- ✅ JWT token generation with Hasura claims
- ✅ Password hashing using bcrypt
- ✅ Role-based access control (user/admin)
- ✅ Protected routes with authentication middleware
- ✅ User-specific chat history

### Frontend (Next.js)
- ✅ Login and registration pages
- ✅ Auth context for global state management
- ✅ Protected routes (chat page, admin panel)
- ✅ Navigation bar with user info
- ✅ Token storage in localStorage
- ✅ Automatic token inclusion in API requests

---

## 📁 New Files Created

### Backend Files
```
backend/
├── app/
│   ├── core/
│   │   ├── security.py          # Password hashing & JWT token management
│   │   ├── auth.py               # Authentication dependencies
│   │   └── hasura.py             # Hasura GraphQL integration helpers
│   ├── routes/
│   │   └── auth.py               # Authentication endpoints (register, login, me)
│   └── services/
│       └── auth_service.py       # Authentication business logic
└── create_admin.py               # Script to create admin users
```

### Frontend Files
```
frontend/app/
├── context/
│   └── AuthContext.js            # Global auth state management
├── components/
│   ├── Navbar.js                 # Navigation with user info
│   └── ProtectedRoute.js         # Route protection wrapper
├── login/
│   └── page.js                   # Login page
└── register/
    └── page.js                   # Registration page
```

---

## 🔧 Updated Files

### Backend
- `requirements.txt` - Added: `python-jose[cryptography]`, `passlib[bcrypt]`, `pyjwt`
- `app/core/config.py` - Added JWT and Hasura configuration
- `app/models.py` - Added `User` model and updated `ChatMessage` with `user_id`
- `app/schemas.py` - Added auth-related schemas
- `app/main.py` - Added auth router
- `app/routes/admin.py` - Added admin-only middleware
- `app/routes/chat.py` - Added authentication requirement
- `app/services/chat_service.py` - Added `user_id` parameter

### Frontend
- `app/layout.js` - Added AuthProvider and Navbar
- `app/page.js` - Wrapped with ProtectedRoute
- `app/admin/page.js` - Wrapped with ProtectedRoute (admin only)
- `app/lib/api.js` - Added JWT token to API requests

---

## 🚀 Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create/update `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Hasura Configuration (if using Hasura)
HASURA_GRAPHQL_URL=http://localhost:8080/v1/graphql
HASURA_GRAPHQL_ADMIN_SECRET=your-hasura-admin-secret
HASURA_JWT_SECRET_KEY=your-super-secret-key-change-in-production
```

⚠️ **Important**: Change `SECRET_KEY` to a strong random string in production!

### 3. Run Database Migrations

The User table will be created automatically on first run. If using existing database:

```bash
# Start backend (it will create tables automatically)
cd backend
python -m uvicorn app.main:app --reload
```

### 4. Create First Admin User

```bash
cd backend
python create_admin.py
```

Follow the prompts to create your admin account:
- Enter email address
- Enter username
- Enter password (min 6 characters)

### 5. Start Services

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 👤 User Roles

### Regular User (role='user')
- ✅ Can register via public registration page
- ✅ Can login and access chat page
- ✅ Can see only their own chat history
- ❌ Cannot access admin panel

### Admin (role='admin')
- ✅ Can access chat page
- ✅ Can access admin panel
- ✅ Can see all users' chat histories
- ✅ Can manage nodes, edges, FAQs

---

## 🔐 Authentication Flow

### Registration
```
1. User visits /register
2. Fills form (email, username, password)
3. Backend creates user with role='user'
4. Auto-login after successful registration
5. Redirect to chat page
```

### Login
```
1. User visits /login
2. Enters email and password
3. Backend verifies credentials
4. Returns JWT token with user data
5. Frontend stores token in localStorage
6. Redirect to chat page
```

### Protected Routes
```
1. User navigates to protected page (/ or /admin)
2. ProtectedRoute component checks authentication
3. If not authenticated → redirect to /login
4. If authenticated but not admin (for /admin) → redirect to / with error
5. If authorized → render page content
```

---

## 🔑 API Authentication

### Making Authenticated Requests

All protected endpoints require JWT token in Authorization header:

```javascript
const response = await fetch('http://localhost:8000/chat/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`  // JWT token
  },
  body: JSON.stringify({...})
});
```

### Frontend API Integration

The `api.js` file automatically includes tokens:

```javascript
import { sendChatMessage } from './lib/api';

// Token is automatically included from localStorage
const response = await sendChatMessage(sessionId, message);
```

---

## 🛡️ Security Features

### Password Security
- ✅ Passwords hashed with bcrypt before storage
- ✅ Salted hashes (prevents rainbow table attacks)
- ✅ Minimum password length: 6 characters
- ✅ Never stored as plain text

### Token Security
- ✅ JWT tokens signed with SECRET_KEY
- ✅ Tokens include expiration timestamp
- ✅ Tokens validated on every request
- ✅ Expired tokens automatically rejected
- ✅ Includes Hasura claims for GraphQL authorization

### API Security
- ✅ All admin endpoints require admin role
- ✅ Chat endpoints require authentication
- ✅ Users can only see their own chat history
- ✅ Admins can see all chat histories

---

## 📝 API Endpoints

### Authentication Endpoints

#### POST `/auth/register`
Create new user account (public)

**Request:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "secure123"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "john_doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-29T10:30:00"
}
```

#### POST `/auth/login`
Login and receive JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET `/auth/me`
Get current user info (requires authentication)

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "john_doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-29T10:30:00"
}
```

---

## 🔨 Managing Users

### Create Admin User (Option 1: Script)

```bash
cd backend
python create_admin.py
```

Select option 1 to create new admin user. Follow the prompts.

### Create Admin User (Option 2: SQL)

If you already have a user and want to promote them:

```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'user@example.com';
```

### List All Users (via Script)

```bash
cd backend
python create_admin.py
```

Select option 2 to list all users.

### Promote User to Admin (via Script)

```bash
cd backend
python create_admin.py
```

Select option 3, then enter the user's email.

---

## 🧪 Testing Authentication

### Test User Registration

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123"
  }'
```

### Test Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

Copy the `access_token` from response.

### Test Protected Endpoint

```bash
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token_here>" \
  -d '{
    "session_id": "uuid",
    "message": "hello"
  }'
```

---

## 🔗 Hasura Integration

### JWT Token Structure

Tokens include Hasura-specific claims for GraphQL authorization:

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "https://hasura.io/jwt/claims": {
    "x-hasura-allowed-roles": ["user"],
    "x-hasura-default-role": "user",
    "x-hasura-user-id": "user_id"
  }
}
```

### Hasura Configuration

In your Hasura `docker-compose.yml`:

```yaml
HASURA_GRAPHQL_JWT_SECRET: '{"type":"HS256","key":"your-secret-key"}'
HASURA_GRAPHQL_UNAUTHORIZED_ROLE: anonymous
```

### Using Tokens with Hasura

```javascript
const response = await fetch(hasuraURL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: `query { users { id email } }`
  })
});
```

---

## ❓ Troubleshooting

### "Authentication required" error

**Problem**: API returns 401 Unauthorized

**Solutions**:
1. Check if token exists in localStorage
2. Verify token hasn't expired
3. Confirm Authorization header is set correctly
4. Try logging out and logging in again

### "Admin access required" error

**Problem**: User can't access admin panel

**Solutions**:
1. Check user's role in database: `SELECT role FROM users WHERE email = 'your@email.com';`
2. If role is 'user', promote to admin: `UPDATE users SET role = 'admin' WHERE email = 'your@email.com';`
3. Restart backend after database changes
4. Logout and login again to get fresh token

### Database errors on startup

**Problem**: User table doesn't exist

**Solution**:
1. Ensure backend is running
2. Tables are created automatically on startup
3. Check DATABASE_URL in .env is correct
4. Verify database permissions

### Frontend shows "Redirecting to login..."

**Problem**: Token invalid or expired

**Solutions**:
1. Clear localStorage: `localStorage.clear()` in browser console
2. Logout and login again
3. Check backend is running
4. Verify SECRET_KEY hasn't changed

---

## 📊 Database Schema

### users table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  role VARCHAR NOT NULL DEFAULT 'user',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### chat_messages table (updated)
```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL,
  user_id UUID REFERENCES users(id),  -- NEW COLUMN
  sender VARCHAR NOT NULL,
  message_text TEXT NOT NULL,
  node_id UUID REFERENCES nodes(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 Customization

### Change Token Expiration

In `backend/app/core/config.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Change to desired minutes
```

### Customize User Roles

To add more roles, update `backend/app/models.py`:

```python
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"  # New role
```

Then update authorization logic in `backend/app/core/auth.py`.

### Change Password Requirements

In `backend/app/routes/auth.py` and frontend registration:

```python
# Backend validation
if len(password) < 8:  # Change minimum length
    raise HTTPException(400, "Password must be at least 8 characters")
```

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can register new user
- [ ] Can login with created user
- [ ] Chat page requires authentication
- [ ] Admin panel requires admin role
- [ ] Regular users cannot access admin panel
- [ ] Admins can access admin panel
- [ ] Logout works correctly
- [ ] Token persists after page reload
- [ ] Invalid tokens are rejected
- [ ] Users see only their own chat history
- [ ] Admins see all chat histories

---

## 📚 Next Steps

1. **Production Deployment**:
   - Change `SECRET_KEY` to strong random value
   - Use HTTPS for all endpoints
   - Configure CORS for production domain
   - Set secure cookie options

2. **Additional Features**:
   - Password reset functionality
   - Email verification
   - Remember me checkbox
   - Session management
   - User profile editing

3. **Security Enhancements**:
   - Rate limiting on auth endpoints
   - Account lockout after failed attempts
   - Two-factor authentication
   - Refresh tokens with rotation

---

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs for error messages
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

---

## 📄 License

This authentication system is part of the Chat Bot project.
