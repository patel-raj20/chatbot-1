# Frontend Architecture Diagram

## 📊 Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION ROOT                          │
│                         (app/layout.js)                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
          ┌─────────▼─────────┐    ┌─────────▼─────────┐
          │   Landing Page    │    │    Auth Pages     │
          │   (page.js)       │    │  (login/signup)   │
          └─────────┬─────────┘    └─────────┬─────────┘
                    │                         │
                    │                         ▼
                    │              ┌─────────────────────┐
                    │              │    AuthForm         │
                    │              │  (components/auth)  │
                    │              └─────────────────────┘
                    │
          ┌─────────┴──────────────────────┐
          │                                │
┌─────────▼─────────┐          ┌──────────▼──────────┐
│   Chat Page       │          │   Admin Page        │
│ (chatbot/page.js) │          │  (admin/page.js)    │
└─────────┬─────────┘          └──────────┬──────────┘
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌─────────────────────┐
│   useChat Hook   │          │  Admin Hooks        │
│  (hooks/useChat) │          │  - useAdminFlow     │
└────────┬─────────┘          │  - useAdminFAQ      │
         │                    │  - useAdminHistory  │
         │                    │  - useAdminRAG      │
         ▼                    └──────────┬──────────┘
┌──────────────────┐                    │
│ Chat Components  │                    ▼
│  - ChatMessage   │          ┌─────────────────────┐
│  - ChatInput     │          │  Admin Components   │
│  - FAQSection    │          │  - FlowTab          │
│  - TypingInd...  │          │  - FAQTab           │
│  - EmptyState    │          │  - HistoryTab       │
└──────────────────┘          │  - RAGTab           │
                              │  - AdminHeader      │
                              │  - AdminTabs        │
                              │  - NodeForm         │
                              │  - FAQForm          │
                              │  - CustomNode       │
                              └─────────────────────┘
```

## 🔄 Data Flow

### Chat Flow
```
User Input (ChatInput)
        │
        ▼
useChat Hook
        │
        ├──► API Call (lib/api.js)
        │         │
        │         ▼
        │    Backend API
        │         │
        │         ▼
        └──► Update State
                  │
                  ▼
            ChatMessage Component
                  │
                  ▼
            User sees response
```

### Admin Flow
```
User Action (Click/Form Submit)
        │
        ▼
Admin Hook (useAdminFlow/FAQ/etc)
        │
        ├──► API Call (constants/api.js)
        │         │
        │         ▼
        │    Backend API
        │         │
        │         ▼
        └──► Update State
                  │
                  ▼
            Tab Component
                  │
                  ▼
            UI Updates
```

## 📦 Module Dependencies

```
Pages
  │
  ├─► Hooks ────┐
  │             │
  ├─► Components │
  │      │      │
  │      └──────┤
  │             │
  └─> Constants │
        │       │
        └───────┤
                │
                ▼
            lib/api.js
                │
                ▼
          Backend API
```

## 🎯 Component Reusability

### Shared Across App
```
┌──────────────────────────────────┐
│       Common Components          │
│  ┌────────────────────────────┐  │
│  │  Loading                   │  │
│  │  ErrorMessage              │  │
│  │  Header                    │  │
│  └────────────────────────────┘  │
└──────────┬───────────────────────┘
           │
     ┌─────┴─────┬─────────┬────────┐
     ▼           ▼         ▼        ▼
   Chat        Admin     Auth    Landing
  Pages       Pages     Pages     Page
```

### Feature-Specific
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  Chat Components │  │ Admin Components │  │Auth Component│
│  Used in:        │  │ Used in:         │  │Used in:      │
│  - chatbot/page  │  │ - admin/page     │  │- login/page  │
│                  │  │                  │  │- signup/page │
└──────────────────┘  └──────────────────┘  └──────────────┘
```

## 🔌 API Integration

```
Component/Hook
      │
      ▼
lib/api.js Functions
      │
      ├─► sendChatMessage()
      ├─► fetchFAQs()
      ├─► askRAGQuestionStreaming()
      ├─► uploadPDF()
      └─► [other API calls]
      │
      ▼
constants/api.js
      │
      ├─► ENDPOINTS.CHAT_MESSAGE
      ├─► ENDPOINTS.FAQS
      ├─► ENDPOINTS.RAG_ASK_STREAM
      └─► [other endpoints]
      │
      ▼
Backend API
      │
      ▼
Response
      │
      ▼
Update Hook State
      │
      ▼
Re-render Components
      │
      ▼
User sees updated UI
```

## 🎨 Style System

```
constants/styles.js
      │
      ├─► GRADIENTS
      ├─► BUTTON_STYLES
      ├─► ANIMATIONS
      └─► KEYFRAMES
      │
      ▼
Imported by Components
      │
      ├─► Chat Components
      ├─► Admin Components
      ├─► Common Components
      └─► Page Components
      │
      ▼
Applied via className
      │
      ▼
Tailwind CSS Processing
      │
      ▼
Final Rendered Styles
```

## 🔐 Authentication Flow

```
User visits protected page
      │
      ▼
useAuthGuard() hook
      │
      ├─► Check localStorage
      │   for auth token
      │
      ├─ No token? ──► Redirect to /auth/login
      │
      └─ Has token? ──┐
                      │
                      ▼
              Verify role (if required)
                      │
              ┌───────┴────────┐
              │                │
         Admin role?      User role?
              │                │
              ▼                ▼
        Admin Panel      Chat Interface
```

## 📱 Responsive Architecture

```
Mobile/Tablet/Desktop
        │
        ▼
Tailwind Responsive Classes
        │
        ├─► sm: (640px+)
        ├─► md: (768px+)
        ├─► lg: (1024px+)
        └─► xl: (1280px+)
        │
        ▼
Same Components
Different Layout
        │
        ▼
Optimized User Experience
```

## 🚀 Performance Optimization

```
Page Load
    │
    ▼
Next.js Code Splitting
    │
    ├─► Load only required components
    ├─► Lazy load heavy dependencies (ReactFlow)
    └─► Server-side rendering for initial page
    │
    ▼
Client-side Hydration
    │
    ▼
Interactive Application
    │
    ├─► Efficient re-renders (React)
    ├─► WebSocket for streaming (RAG)
    └─► Optimistic UI updates
```

## 📊 State Management

```
Page Component
      │
      ▼
Custom Hook (useState, useEffect)
      │
      ├─► Local State
      │   (messages, input, etc.)
      │
      ├─► Side Effects
      │   (API calls, subscriptions)
      │
      └─► Derived State
          (computed values)
      │
      ▼
Props to Child Components
      │
      ▼
Component Re-renders
      │
      ▼
Updated UI
```

---

## Summary

The new architecture follows these principles:

1. **Separation of Concerns**: UI, Logic, and Data are separated
2. **Single Responsibility**: Each component/hook has one job
3. **DRY (Don't Repeat Yourself)**: Reusable components and hooks
4. **Clear Dependencies**: Easy to trace data flow
5. **Maintainable**: Easy to find and fix issues
6. **Scalable**: Easy to add new features

This diagram serves as a visual guide to understanding how all the pieces fit together in the refactored frontend.
