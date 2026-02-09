# Authentication System Guide
## JWT-Based Authentication for Chatbot Application

---

## 🎯 Overview

This document explains the complete authentication system implemented in the chatbot application.

**Architecture:**
- **Backend**: FastAPI with JWT + bcrypt
- **Frontend**: Next.js with route guards
- **Authorization**: Hasura GraphQL Engine (see [HASURA_INTEGRATION_GUIDE.md](HASURA_INTEGRATION_GUIDE.md))

**Key Principle:**
- Backend handles **AUTHENTICATION** (who you are)
- Hasura handles **AUTHORIZATION** (what you can do)
- Frontend provides route protection for UX

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│                 │
│ - Login/Signup  │
│ - Route Guards  │
│ - JWT Storage   │
└────────┬────────┘
         │ JWT Token
         ▼
┌─────────────────┐      ┌──────────────┐
│   Backend       │      │   Hasura     │
│   (FastAPI)     │      │   GraphQL    │
│                 │      │              │
│ - Signup        │      │ - Permission │
│ - Login         │◄─────┤   Rules      │
│ - JWT Creation  │      │ - Row-level  │
└────────┬────────┘      │   Security   │
         │                └──────────────┘
         ▼
┌─────────────────┐
│   PostgreSQL    │
│                 │
│ - users table   │
│ - Other tables  │
└─────────────────┘
```

---

## 📁 File Structure

### Backend (`backend/app/`)

```
app/
├── auth/                          # 🆕 Authentication module
│   ├── __init__.py
│   ├── routes.py                  # POST /auth/signup, /auth/login
│   ├── schemas.py                 # Pydantic models
│   └── utils.py                   # JWT + password hashing
├── models.py                      # 🆕 Added User model
├── main.py                        # 🆕 Registered auth routes
└── ...                            # Existing files (unchanged)
```

### Frontend (`frontend/app/`)

```
app/
├── auth/                          # 🆕 Authentication pages
│   ├── login/
│   │   └── page.js                # Login page
│   └── signup/
│       └── page.js                # Signup page
├── chatbot/                       # 🆕 Protected chatbot
│   └── page.js                    # Moved from root (with guards)
├── admin/                         # 🆕 Protected admin panel
│   └── page.js                    # Updated with admin guard
├── lib/
│   ├── auth.js                    # 🆕 Auth utilities
│   ├── authGuard.js               # 🆕 Route protection hook
│   └── api.js                     # 🆕 Updated with JWT
└── page.js                        # 🆕 Landing/redirect page
```

---

## 🔐 Authentication Flow

### 1. User Signup

```
User                Frontend              Backend               Database
  │                    │                     │                     │
  │  Enter username    │                     │                     │
  │  + password        │                     │                     │
  │───────────────────>│                     │                     │
  │                    │                     │                     │
  │                    │ POST /auth/signup   │                     │
  │                    │ {username,password} │                     │
  │                    │────────────────────>│                     │
  │                    │                     │                     │
  │                    │                     │ Hash password       │
  │                    │                     │ (bcrypt)            │
  │                    │                     │                     │
  │                    │                     │ INSERT INTO users   │
  │                    │                     │ role='user'         │
  │                    │                     │────────────────────>│
  │                    │                     │                     │
  │                    │ Success message     │                     │
  │                    │<────────────────────│                     │
  │                    │                     │                     │
  │  Redirect to login │                     │                     │
  │<───────────────────│                     │                     │
```

**Key Points:**
- Password is hashed with bcrypt before storage
- All users default to `role='user'`
- Admin role must be manually assigned

---

### 2. User Login

```
User                Frontend              Backend               Database
  │                    │                     │                     │
  │  Enter credentials │                     │                     │
  │───────────────────>│                     │                     │
  │                    │                     │                     │
  │                    │ POST /auth/login    │                     │
  │                    │ {username,password} │                     │
  │                    │────────────────────>│                     │
  │                    │                     │                     │
  │                    │                     │ SELECT * FROM users │
  │                    │                     │ WHERE username=?    │
  │                    │                     │────────────────────>│
  │                    │                     │                     │
  │                    │                     │ Verify password     │
  │                    │                     │ (bcrypt.verify)     │
  │                    │                     │                     │
  │                    │                     │ Generate JWT        │
  │                    │                     │ + Hasura claims     │
  │                    │                     │                     │
  │                    │ JWT + user info     │                     │
  │                    │<────────────────────│                     │
  │                    │                     │                     │
  │  Store JWT in      │                     │                     │
  │  localStorage      │                     │                     │
  │                    │                     │                     │
  │  Redirect based    │                     │                     │
  │  on role           │                     │                     │
  │<───────────────────│                     │                     │
```

**JWT Token Structure:**
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

---

### 3. Authenticated Requests

```
User                Frontend              Backend/Hasura
  │                    │                     │
  │  Visit /chatbot    │                     │
  │───────────────────>│                     │
  │                    │                     │
  │                    │ Check JWT           │
  │                    │ (authGuard)         │
  │                    │                     │
  │                    │ Valid? Continue     │
  │                    │ Invalid? → /login   │
  │                    │                     │
  │  API Call          │                     │
  │───────────────────>│                     │
  │                    │                     │
  │                    │ Add Authorization:  │
  │                    │ Bearer <token>      │
  │                    │────────────────────>│
  │                    │                     │
  │                    │                     │ Verify JWT
  │                    │                     │ Check permissions
  │                    │                     │ (if Hasura)
  │                    │                     │
  │                    │ Response            │
  │                    │<────────────────────│
  │                    │                     │
  │  Display data      │                     │
  │<───────────────────│                     │
```

---

## 👥 User Roles

### 1. **user** (Default)

**Access:**
- ✅ Chatbot page (`/chatbot`)
- ❌ Admin page (`/admin`)

**Permissions (via Hasura):**
- Read FAQs
- Create own chat messages
- View own chat history
- Read conversation nodes

**Frontend Behavior:**
- Shows chatbot interface
- No admin menu visible

---

### 2. **admin** (Manually Assigned)

**Access:**
- ✅ Chatbot page (`/chatbot`)
- ✅ Admin page (`/admin`)

**Permissions (via Hasura):**
- Full access to all tables
- Create/edit conversation flows
- Manage FAQs
- View all chat sessions
- Upload documents

**Frontend Behavior:**
- Shows chatbot interface
- Admin button visible in header
- Can access admin panel

---

## 🛡️ Route Protection

### Frontend Route Guards

**Implementation:** `useAuthGuard()` hook

**Usage:**

```javascript
// Protect for any authenticated user
function ChatbotPage() {
  const { loading, user } = useAuthGuard();
  
  if (loading) return <div>Loading...</div>;
  
  return <div>Chatbot content</div>;
}

// Protect for admin only
function AdminPage() {
  const { loading, user } = useAuthGuard('admin');
  
  if (loading) return <div>Loading...</div>;
  
  return <div>Admin panel</div>;
}
```

**Behavior:**
- Not authenticated → Redirect to `/auth/login`
- Authenticated but insufficient role → Redirect to `/chatbot`
- Authorized → Render page

---

## 🔑 Admin User Management

### Creating First Admin

Since all signups default to `user` role, you must manually promote users to admin.

#### Method 1: Using Promotion Script (Recommended)

```bash
# List all users
python backend/promote_admin.py --list

# Promote specific user
python backend/promote_admin.py john_doe
```

#### Method 2: Direct Database Update

```sql
-- Connect to PostgreSQL
docker exec -it chatbot_postgres psql -U user -d chatbot

-- Promote user
UPDATE users SET role = 'admin' WHERE username = 'john_doe';

-- Verify
SELECT username, role, created_at FROM users;
```

#### After Promotion

User must:
1. **Log out** from frontend
2. **Log in again** to get new JWT with admin role
3. Can now access `/admin` route

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

```bash
# JWT Configuration
JWT_SECRET_KEY="your-secret-key-change-this-in-production-use-minimum-32-characters"
ACCESS_TOKEN_EXPIRE_DAYS=7

# Database (existing)
DATABASE_URL="postgresql://user:password@localhost:5432/chatbot"
```

**⚠️ IMPORTANT:**
- Use a strong, random secret key in production
- Never commit `.env` to version control
- `JWT_SECRET_KEY` must match Hasura's `HASURA_GRAPHQL_JWT_SECRET`

---

## 🧪 Testing the System

### 1. Test Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "username": "testuser",
    "role": "user"
  }
}
```

---

### 2. Test Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "testuser",
  "role": "user"
}
```

---

### 3. Test Frontend Flow

1. **Visit:** http://localhost:3000
   - Should redirect to `/auth/login`

2. **Signup:**
   - Go to `/auth/signup`
   - Create account
   - Redirected to login

3. **Login:**
   - Enter credentials
   - Redirected to `/chatbot` (for user)
   - Redirected to `/admin` (for admin)

4. **Protected Routes:**
   - Try accessing `/admin` as user → Redirected to `/chatbot`
   - Try accessing `/chatbot` without login → Redirected to `/auth/login`

---

## 🐛 Troubleshooting

### Issue: "Invalid username or password"

**Cause:** Incorrect credentials or user doesn't exist

**Solution:**
- Verify username is correct (case-sensitive)
- Ensure user completed signup
- Check database: `SELECT * FROM users;`

---

### Issue: "Token expired"

**Cause:** JWT token has expired (default: 7 days)

**Solution:**
- Log out and log in again
- Adjust `ACCESS_TOKEN_EXPIRE_DAYS` if needed

---

### Issue: Admin can't access `/admin`

**Cause:** User role not updated or needs new JWT

**Solution:**
1. Verify role in database:
   ```sql
   SELECT username, role FROM users WHERE username = 'admin_user';
   ```
2. If role is correct, user must **log out and log in again**
3. Decode JWT at https://jwt.io to verify role claim

---

### Issue: "Authorization header missing"

**Cause:** Token not being sent with requests

**Solution:**
- Check `localStorage` has `auth_token`
- Verify `getAuthHeaders()` in `api.js` is used
- Check browser console for errors

---

## 🚀 Deployment Considerations

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to strong random value (min 32 chars)
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS for token transmission
- [ ] Set appropriate CORS origins
- [ ] Consider httpOnly cookies instead of localStorage
- [ ] Implement refresh tokens for long sessions
- [ ] Add rate limiting on auth endpoints
- [ ] Log all authentication attempts
- [ ] Regular security audits

---

## 📚 API Reference

### POST `/auth/signup`

**Request:**
```json
{
  "username": "string (3-50 chars)",
  "password": "string (min 6 chars)"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "username": "string",
    "role": "user"
  }
}
```

**Errors:**
- `400`: Username already exists
- `422`: Validation error

---

### POST `/auth/login`

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "jwt-token-string",
  "token_type": "bearer",
  "user_id": "uuid",
  "username": "string",
  "role": "user|admin"
}
```

**Errors:**
- `401`: Invalid credentials
- `403`: Account inactive

---

## 🎓 Security Best Practices

1. **Password Security:**
   - ✅ Hashed with bcrypt (slow by design)
   - ✅ Never logged or exposed in responses
   - ✅ Minimum 6 characters enforced

2. **JWT Security:**
   - ✅ Short expiration (7 days default)
   - ✅ Signed with secret key
   - ✅ Includes minimal necessary claims

3. **Frontend Security:**
   - ⚠️ localStorage (consider httpOnly cookies in production)
   - ✅ Route guards prevent unauthorized access
   - ✅ Tokens not logged to console

4. **Database Security:**
   - ✅ Passwords never stored in plain text
   - ✅ Role changes require direct database access
   - ✅ Admin promotion is manual process

---

## 📖 Related Documentation

- [HASURA_INTEGRATION_GUIDE.md](HASURA_INTEGRATION_GUIDE.md) - Full Hasura setup
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - Admin panel usage
- [README.md](README.md) - Project overview

---

**Questions?** Check the troubleshooting section or review the code comments in:
- `backend/app/auth/routes.py`
- `frontend/app/lib/authGuard.js`
