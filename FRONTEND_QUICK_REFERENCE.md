# Frontend Quick Reference Guide

## 📁 File Organization

### Where to Find Things

**Need to modify the chat UI?**
→ `frontend/app/components/chat/`

**Need to change admin panel?**
→ `frontend/app/components/admin/`

**Need to update API calls?**
→ `frontend/app/lib/api.js` and `frontend/app/hooks/`

**Need to change styles?**
→ `frontend/app/constants/styles.js`

**Need to update endpoints?**
→ `frontend/app/constants/api.js`

## 🔧 Common Tasks

### Adding a New Feature to Chat

1. Create component in `components/chat/NewFeature.js`
2. Add logic to `hooks/useChat.js` (if needed)
3. Import and use in `chatbot/page.js`

```javascript
// Example: Adding a new chat feature
// 1. Create component
// components/chat/VoiceInput.js
export default function VoiceInput({ onVoiceInput }) {
  // ... component code
}

// 2. Add to useChat hook
// hooks/useChat.js
export function useChat(user) {
  const handleVoiceInput = (text) => {
    // ... voice logic
  };
  return { ...existing, handleVoiceInput };
}

// 3. Use in page
// chatbot/page.js
import VoiceInput from '../components/chat/VoiceInput';

export default function ChatPage() {
  const chatState = useChat(user);
  return (
    <>
      {/* ... existing components */}
      <VoiceInput onVoiceInput={chatState.handleVoiceInput} />
    </>
  );
}
```

### Adding a New Admin Tab

1. Create tab component in `components/admin/NewTab.js`
2. Create hook in `hooks/useAdminNew.js`
3. Add tab to `components/admin/AdminTabs.js`
4. Add tab content to `admin/page.js`

### Modifying Styles

**Global Colors/Gradients:**
```javascript
// constants/styles.js
export const GRADIENTS = {
  primary: 'bg-gradient-to-br from-violet-600...',
  newGradient: 'bg-gradient-to-br from-pink-500...',
};
```

**Component-Specific:**
```javascript
// Directly in component
<div className="bg-blue-500 hover:bg-blue-600">...</div>
```

## 📦 Component Catalog

### Common Components

| Component | Purpose | Usage |
|-----------|---------|-------|
| `Loading` | Loading spinner | `<Loading message="Loading..." />` |
| `ErrorMessage` | Error display | `<ErrorMessage error={error} onClose={...} />` |
| `Header` | App header | `<Header user={user} hasDocument={...} />` |

### Chat Components

| Component | Purpose | Usage |
|-----------|---------|-------|
| `ChatMessage` | Message bubble | `<ChatMessage message={msg} onOptionClick={...} />` |
| `TypingIndicator` | Bot typing | `{isTyping && <TypingIndicator />}` |
| `EmptyChatState` | Empty state | `{messages.length === 0 && <EmptyChatState />}` |
| `FAQSection` | FAQ buttons | `<FAQSection faqs={faqs} onFaqClick={...} />` |
| `ChatInput` | Input field | `<ChatInput input={input} onSend={...} />` |

### Admin Components

| Component | Purpose | Usage |
|-----------|---------|-------|
| `AdminHeader` | Admin header | `<AdminHeader user={user} onLogout={...} />` |
| `AdminTabs` | Tab navigation | `<AdminTabs activeTab={tab} setActiveTab={...} />` |
| `FlowTab` | Flow editor | `<FlowTab nodes={...} edges={...} />` |
| `FAQTab` | FAQ manager | `<FAQTab faqs={...} onSubmit={...} />` |
| `HistoryTab` | Chat history | `<HistoryTab sessions={...} />` |
| `RAGTab` | Document upload | `<RAGTab uploadStatus={...} />` |

## 🎣 Hooks Reference

### useChat

```javascript
const {
  sessionId,        // Current session ID
  messages,         // Array of messages
  input,            // Input field value
  setInput,         // Update input
  faqs,             // Available FAQs
  hasDocument,      // Document uploaded?
  isTyping,         // Bot typing?
  listRef,          // Scroll container ref
  sendMessage,      // Send message function
} = useChat(user);
```

### useAdminFlow

```javascript
const {
  nodes,            // ReactFlow nodes
  edges,            // ReactFlow edges
  nodeForm,         // Node form data
  setNodeForm,      // Update node form
  fetchNodes,       // Reload nodes
  handleAddNode,    // Open create form
  handleSubmitForm, // Save node
  deleteEdge,       // Delete connection
} = useAdminFlow();
```

### useAdminFAQ

```javascript
const {
  faqs,             // FAQ list
  faqForm,          // FAQ form data
  setFaqForm,       // Update FAQ form
  fetchFaqs,        // Reload FAQs
  handleAddFaq,     // Open create form
  handleSubmitForm, // Save FAQ
  deleteFaq,        // Delete FAQ
  startEditFaq,     // Start editing
} = useAdminFAQ();
```

### useAdminHistory

```javascript
const {
  sessions,          // Session list
  expandedSessions,  // Which sessions are expanded
  messagesBySession, // Messages per session
  fetchSessions,     // Reload sessions
  toggleSession,     // Expand/collapse session
} = useAdminHistory();
```

### useAdminRAG

```javascript
const {
  uploadStatus,      // Upload status message
  isUploading,       // Currently uploading?
  handleFileUpload,  // File upload handler
} = useAdminRAG();
```

## 🎨 Style Constants

```javascript
import { GRADIENTS, BUTTON_STYLES, ANIMATIONS } from '../constants/styles';

// Use gradients
<div className={GRADIENTS.primary}>...</div>

// Use button styles
<button className={BUTTON_STYLES.primary}>Click</button>

// Use animations
<div className={ANIMATIONS.fadeIn}>...</div>
```

## 🔌 API Constants

```javascript
import { API_BASE_URL, ENDPOINTS } from '../constants/api';

// Make API calls
fetch(`${API_BASE_URL}${ENDPOINTS.LOGIN}`, { ... });
```

## 🐛 Debugging Tips

### Chat Not Working?
1. Check console for errors
2. Verify `sessionId` is set in useChat
3. Check API_BASE_URL in .env

### Admin Panel Issues?
1. Verify user has ADMIN role
2. Check useAuthGuard in page
3. Check tab is fetching data in useEffect

### Component Not Displaying?
1. Check import path is correct
2. Verify component is exported as default
3. Check props are passed correctly

## 📝 Code Patterns

### Creating a New Component

```javascript
/**
 * Component Name
 * ==============
 * Brief description
 */

export default function ComponentName({ prop1, prop2, onAction }) {
  // Component logic
  
  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  );
}
```

### Creating a New Hook

```javascript
/**
 * Hook Name
 * =========
 * Brief description
 */

import { useState, useEffect } from 'react';

export function useFeature() {
  const [state, setState] = useState(null);
  
  // Hook logic
  
  return {
    state,
    setState,
    // ... other exports
  };
}
```

## 🚀 Getting Started

1. **Read the structure**: Check FRONTEND_REFACTORING_SUMMARY.md
2. **Explore components**: Browse `components/` folder
3. **Understand hooks**: Check `hooks/` folder
4. **Modify existing**: Start with small changes
5. **Build new**: Follow the patterns established

## 📚 Learn More

- **React Hooks**: https://react.dev/reference/react
- **Next.js**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **ReactFlow**: https://reactflow.dev/

---

**Remember**: The code is now organized, but the functionality is unchanged. Everything works exactly as it did before, just in a cleaner structure!
