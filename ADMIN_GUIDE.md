# Chatbot Admin Panel - User Guide

## 🎯 Overview
You now have a complete visual admin panel to manage your chatbot's conversation flow without manually editing the database!

## 🚀 How to Access
1. **From Chat Interface**: Click the "⚙️ Admin" button in the top-right header
2. **Direct URL**: http://localhost:3000/admin

## 📋 Features

### 1. **Create Nodes**
- Click "+ Add New Node" button
- Fill in:
  - **Message Text**: What the bot will say (required)
  - **Trigger Text**: User keyword to start this conversation (optional, for entry nodes)
  - **Is Entry Node**: Check if this is a starting point
- Click "Create Node"

### 2. **Edit Nodes**
- Click "Edit" button on any node card
- Modify the fields
- Click "Update Node"

### 3. **Delete Nodes**
- Click "Delete" button on any node card
- Confirms before deleting
- **Automatically deletes all connections** to/from that node

### 4. **Create Connections (Edges)**
- Click "+ Add Connection" on the source node
- Select the target node from dropdown
- Enter **Option Text** (what user clicks) or leave empty for auto-transition
- Click "Add Connection"

### 5. **Delete Connections**
- In the "Options" section of each node
- Click "Delete" next to any connection

## 🌳 Node Types

### Entry Nodes
- **Purpose**: Starting points of conversations
- **How**: Check "Is Entry Node" and set "Trigger Text"
- **Example**: Trigger text "hello" → Bot says "Hi! How can I help?"

### Regular Nodes
- **Purpose**: Follow-up messages in the conversation
- **Connected via**: Edges with option text

## 🔗 Connection Types

### 1. **User Choice (Option Text)**
```
Node A: "Choose a topic"
  ├─ Option: "Pricing" → Node B
  └─ Option: "Features" → Node C
```

### 2. **Auto-Transition (No Option Text)**
```
Node A: "Please wait..."
  └─ (auto) → Node B: "Here's your info!"
```

## 📊 Visual Structure
Each node card shows:
- 🟢 **ENTRY NODE** badge (if applicable)
- Trigger keyword (in monospace box)
- Bot's message
- List of outgoing options/connections
- Action buttons (Edit, Add Connection, Delete)

## 💡 Best Practices

1. **Start Simple**
   - Create 1-2 entry nodes first
   - Build the conversation tree gradually

2. **Entry Nodes**
   - Use clear trigger words: "hello", "help", "start"
   - Keep trigger text lowercase
   - Mark as "Is Entry Node"

3. **Connections**
   - Use descriptive option text: "Learn more", "Get pricing", "Contact us"
   - Leave option text empty for automatic flow

4. **Testing**
   - After creating/editing, go back to main chat
   - Try the conversation flow
   - Return to admin to adjust

## 🎨 Example Flow

### Simple Greeting Flow
```
1. Entry Node:
   - Trigger: "hello"
   - Message: "Hi! What would you like to know?"
   - Entry: ✓

2. Option Nodes:
   Node A: "Tell me about your services"
   Node B: "Contact information"
   
3. Connections from Node 1:
   - Option: "Services" → Node A
   - Option: "Contact" → Node B
```

## 🔧 Backend API Endpoints Created

All endpoints are at `http://127.0.0.1:8000/admin/`

- **GET /admin/nodes** - List all nodes
- **GET /admin/nodes/{id}** - Get specific node
- **POST /admin/nodes** - Create node
- **PUT /admin/nodes/{id}** - Update node
- **DELETE /admin/nodes/{id}** - Delete node
- **GET /admin/edges** - List all edges
- **POST /admin/edges** - Create edge
- **DELETE /admin/edges/{id}** - Delete edge

## ✨ What's Preserved
All your existing functionality still works:
- ✅ Chat interface
- ✅ FAQs
- ✅ Beautiful UI
- ✅ Message history
- ✅ Auto-scrolling

## 🎉 You're Ready!
No more manual database editing! Just use the admin panel to build your conversation tree visually.
