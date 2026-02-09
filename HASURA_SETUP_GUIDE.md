# Hasura Setup Guide

## ✅ Step 1: Access Hasura Console

Hasura is now running at: **http://localhost:8080**

1. Open http://localhost:8080 in your browser
2. Enter admin secret: `myadminsecretkey`
3. Click "Enter"

---

## ✅ Step 2: Track Database Tables

1. In Hasura Console, click **"DATA"** tab
2. Click **"public"** schema
3. Click **"Track All"** button to track all tables:
   - `users`
   - `nodes`
   - `edges`
   - `faqs`
   - `chat_messages`
   - `pdf_documents`

---

## ✅ Step 3: Set Up Permissions

### For USERS Table

#### USER Role Permissions:
1. Click on `users` table
2. Go to **"Permissions"** tab
3. For **USER** role:
   - **select**: 
     - Custom check: `{"id": {"_eq": "X-Hasura-User-Id"}}`
     - Allow columns: `id`, `username`, `role`, `created_at`
   - **update**:
     - Row check: `{"id": {"_eq": "X-Hasura-User-Id"}}`
     - Allow columns: `username` (only their own profile)
   - **NO insert** or **delete** permissions

#### ADMIN Role Permissions:
1. For **ADMIN** role:
   - **select**: Without any checks (can see all users)
   - **insert**: Allow all columns except `id`
   - **update**: Without any checks (can update any user)
   - **delete**:  Without any checks (can delete any user)

---

### For NODES Table

#### USER Role:
- **select**: Allow all columns (read-only for chatbot)
- **NO insert/update/delete**

#### ADMIN Role:
- **select**: Allow all columns
- **insert**: Allow all columns
- **update**: Allow all columns
- **delete**: Allow without checks

---

### For EDGES Table

#### USER Role:
- **select**: Allow all columns (read-only for chatbot)
- **NO insert/update/delete**

#### ADMIN Role:
- **select**: Allow all columns
- **insert**: Allow all columns
- **update**: Allow all columns
- **delete**: Allow without checks

---

### For FAQS Table

#### USER Role:
- **select**: Custom check: `{"is_active": {"_eq": true}}`
- **NO insert/update/delete**

#### ADMIN Role:
- **select**: Allow all columns (including inactive FAQs)
- **insert**: Allow all columns
- **update**: Allow all columns
- **delete**: Allow without checks

---

### For CHAT_MESSAGES Table

#### USER Role:
- **select**: Custom check: `{"session_id": {"_eq": "X-Hasura-User-Id"}}`
  (Users can only see their own messages)
- **insert**: Allow all columns (users can create messages)
- **NO update/delete**

#### ADMIN Role:
- **select**: Allow all columns (can see all messages)
- **NO insert/update/delete** (admins view only)

---

### For PDF_DOCUMENTS Table

#### USER Role:
- **select**: Allow all columns
- **NO insert/update/delete**

#### ADMIN Role:
- **select**: Allow all columns
- **insert**: Allow all columns
- **update**: Allow all columns
- **delete**: Allow without checks

---

## ✅ Step 4: Test Authorization

### Test as Regular User:
1. In Hasura Console, click "GraphiQL" tab
2. Add request headers:
   ```json
   {
     "Authorization": "Bearer <your-jwt-token-here>"
   }
   ```
3. Try querying nodes:
   ```graphql
   query {
     nodes {
       id
       message_text
       trigger_text
     }
   }
   ```

### Test as Admin:
1. Use admin JWT token in Authorization header
2. Try admin operations:
   ```graphql
   mutation {
     insert_nodes_one(object: {
       message_text: "Test message",
       trigger_text: "test",
       is_entry: false
     }) {
       id
     }
   }
   ```

---

## ✅ Step 5: Update Frontend to Use Hasura

The frontend environment variable is already configured:
```
NEXT_PUBLIC_HASURA_URL: http://localhost:8080/v1/graphql
```

To use Hasura in frontend, install Apollo Client or urql:

```bash
cd frontend
npm install @apollo/client graphql
```

---

## 🔑 Important Notes

1. **JWT Secret**: Backend (`JWT_SECRET_KEY`) and Hasura (`HASURA_GRAPHQL_JWT_SECRET`) use the same key:
   ```
   your-secret-key-change-this-in-production-use-minimum-32-characters
   ```

2. **Admin Secret**: Use `myadminsecretkey` to access Hasura console

3. **Role-Based Access**:
   - JWT token contains role claim: `"role": "USER"` or `"role": "ADMIN"`
   - Hasura reads this from: `"x-hasura-default-role": "USER"`

4. **Production**:
   - Change `HASURA_GRAPHQL_DEV_MODE` to `false`
   - Change `HASURA_GRAPHQL_ENABLE_CONSOLE` to `false`
   - Use environment variables for secrets

---

## 🎯 Next Steps

1. **Access Hasura Console**: http://localhost:8080
2. **Track all tables** in the public schema
3. **Configure permissions** for USER and ADMIN roles (follow step 3 above)
4. **Test with JWT tokens** from your login
5. **Update frontend** to use GraphQL instead of REST API (optional)

--- 

## 🔧 Troubleshooting

**Hasura not starting?**
```bash
docker-compose logs hasura
```

**Database connection error?**
- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify DATABASE_URL in docker-compose.yml

**JWT tokens not working?**
- Verify JWT secret matches in both backend and Hasura
- Check token format in browser console
- Ensure role claim is present in token

---

## 📚 Resources

- [Hasura Docs](https://hasura.io/docs/latest/graphql/core/index.html)
- [JWT Authentication](https://hasura.io/docs/latest/graphql/core/auth/authentication/jwt.html)
- [Role-Based Permissions](https://hasura.io/docs/latest/graphql/core/auth/authorization/index.html)
