/**
 * API Constants
 * =============
 * Centralized API configuration and endpoints
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  SIGNUP: '/auth/signup',
  
  // Chat
  CHAT_MESSAGE: '/chat/message',
  
  // FAQ
  FAQS: '/faqs',
  ADMIN_FAQS: '/admin/faqs',
  
  // RAG
  // RAG_ASK: '/rag/ask',  // Commented out - Using async streaming only
  RAG_ASK_STREAM: '/rag/ask-stream',
  RAG_UPLOAD: '/rag/upload-pdf',
  RAG_DOCUMENTS: '/rag/documents',
  
  // Admin
  ADMIN_NODES: '/admin/nodes',
  ADMIN_EDGES: '/admin/edges',
  ADMIN_SESSIONS: '/admin/chat/sessions',
  
  // WebSocket
  WS_CHAT: (requestId) => `/ws/chat/${requestId}`,
};

/**
 * Get WebSocket URL from HTTP URL
 */
export function getWebSocketUrl(httpUrl) {
  return httpUrl.replace('http:', 'ws:').replace('https:', 'wss:');
}
