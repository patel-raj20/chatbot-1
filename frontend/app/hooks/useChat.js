/**
 * Chat Hook
 * =========
 * Custom hook for managing chat functionality
 */

import { useState, useEffect, useRef } from 'react';
import { sendChatMessage, askRAGQuestionStreaming, fetchWorkflowQuestions, searchFAQs, API_BASE_URL, getAuthHeaders } from '../lib/api';
import { generateUUID } from '../lib/utils';

export function useChat(user) {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [currentNodeId, setCurrentNodeId] = useState(null);
  const [workflowQuestions, setWorkflowQuestions] = useState([]);
  const [faqSearchQuery, setFaqSearchQuery] = useState("");
  const [faqSuggestions, setFaqSuggestions] = useState([]);
  const [isSearchingFaqs, setIsSearchingFaqs] = useState(false);
  const [hasDocument, setHasDocument] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const listRef = useRef(null);

  // Initialize session and load workflow questions
  useEffect(() => {
    const id = generateUUID();
    setSessionId(id);

    // Load workflow questions
    console.log("Fetching workflow questions...");
    fetchWorkflowQuestions()
      .then(data => {
        console.log("Workflow questions received:", data);
        setWorkflowQuestions(data);
      })
      .catch(err => console.warn("Failed to load workflow questions:", err));

    // Check document status
    fetch(`${API_BASE_URL}/rag/documents`, {
      headers: getAuthHeaders()
    })
      .then(res => res.json())
      .then(docs => {
        const hasDoc = docs && docs.length > 0;
        setHasDocument(hasDoc);
        //console.log("Document status:", hasDoc ? `${docs.length} document(s) available` : "No documents");
      })
      .catch(err => {
        console.warn("Failed to check document status:", err);
        setHasDocument(false);
      });
  }, []);

  // Debounced FAQ search
  useEffect(() => {
    if (faqSearchQuery.length < 2) {
      setFaqSuggestions([]);
      return;
    }

    setIsSearchingFaqs(true);
    const timeoutId = setTimeout(() => {
      searchFAQs(faqSearchQuery)
        .then(results => {
          setFaqSuggestions(results);
          setIsSearchingFaqs(false);
        })
        .catch(err => {
          console.warn("FAQ search failed:", err);
          setFaqSuggestions([]);
          setIsSearchingFaqs(false);
        });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [faqSearchQuery]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  async function sendMessage(text, fromOption = false, nodeContext = null, isFaqClick = false) {
    if (!text || !sessionId) return;

    setMessages((prev) => [...prev, { sender: "user", text }]);
    setIsTyping(true);

    try {
      // STEP 1: Try FAQ/Conversation Tree
      const data = await sendChatMessage(sessionId, text, fromOption ? nodeContext : null);

      // Check if response indicates no match
      const replyLower = data.reply.toLowerCase();
      const didntMatch = replyLower.includes("don't understand") ||
        replyLower.includes("didn't understand") ||
        replyLower.includes("i'm not sure") ||
        replyLower.includes("i don't know");

      // STEP 2: Try RAG with STREAMING if no match and document available
      if (didntMatch && hasDocument && !isFaqClick) {
        try {
          setIsTyping(false);
          setIsStreaming(true);
          setStreamingText("");

          // Add placeholder message for streaming
          const streamingMessageIndex = messages.length + 1;
          setMessages((prev) => [
            ...prev,
            {
              sender: "bot",
              text: "",
              options: [],
              nodeId: null,
              isStreaming: true
            },
          ]);

          let fullAnswer = "";

          await askRAGQuestionStreaming(
            text,
            user?.id || 'anonymous',
            sessionId,
            // onToken callback
            (token) => {
              fullAnswer += token;
              setStreamingText(fullAnswer);
              // Update the streaming message
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[streamingMessageIndex] = {
                  sender: "bot",
                  text: fullAnswer,
                  options: [],
                  nodeId: null,
                  isStreaming: true
                };
                return newMessages;
              });
            },
            // onComplete callback
            () => {
              setIsStreaming(false);
              setStreamingText("");
              // Mark streaming as complete
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[streamingMessageIndex] = {
                  sender: "bot",
                  text: fullAnswer,
                  options: [],
                  nodeId: null,
                  isStreaming: false
                };
                return newMessages;
              });
            },
            // onError callback
            (error) => {
              console.error("Streaming RAG failed:", error);
              setIsStreaming(false);
              setStreamingText("");
              // Show error message
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[streamingMessageIndex] = {
                  sender: "bot",
                  text: `Sorry, there was an error: ${error.message}`,
                  options: [],
                  nodeId: null,
                  isStreaming: false
                };
                return newMessages;
              });
            }
          );

          return;
        } catch (err) {
          console.error("RAG fallback failed:", err);
          setIsStreaming(false);
          setStreamingText("");
          // Fall through to show tree response
        }
      }

      // STEP 3: Show FAQ/Tree response
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.reply,
          options: data.options || [],
          nodeId: data.node_id ?? null,
        },
      ]);

      setCurrentNodeId(data.node_id ?? null);
    } catch (err) {
      console.error("Chat error:", err);
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: `Sorry, something went wrong: ${err.message}`,
          options: [],
          nodeId: null,
        },
      ]);
    }
  }

  return {
    sessionId,
    messages,
    input,
    setInput,
    currentNodeId,
    workflowQuestions,
    faqSearchQuery,
    setFaqSearchQuery,
    faqSuggestions,
    isSearchingFaqs,
    hasDocument,
    isTyping,
    isStreaming,
    streamingText,
    listRef,
    sendMessage
  };
}
