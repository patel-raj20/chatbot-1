/**
 * Chat Interface
 * ==============
 * Main chat page with RAG fallback mechanism.
 * 
 * CHAT FLOW:
 *   1. User sends message
 *   2. Try FAQ/Conversation Tree match
 *   3. If no match + PDF uploaded → Try RAG
 *   4. Display response with options (if any)
 * 
 * FEATURES:
 *   - Session-based chat history
 *   - FAQ quick answers
 *   - Conversation tree navigation
 *   - RAG-powered document search
 *   - PDF upload support
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { sendChatMessage, askRAGQuestion, fetchFAQs, uploadPDF } from "./lib/api";
import { generateUUID } from "./lib/utils";

export default function ChatTestUI() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [currentNodeId, setCurrentNodeId] = useState(null);
  const [faqs, setFaqs] = useState([]);
  const [hasDocument, setHasDocument] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const listRef = useRef(null);

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

      // STEP 2: Try RAG if no match and document available
      if (didntMatch && hasDocument && !isFaqClick) {
        try {
          const ragData = await askRAGQuestion(text, sessionId);
          
          setIsTyping(false);
          setMessages((prev) => [
            ...prev,
            {
              sender: "bot",
              text: ragData.answer,
              options: [],
              nodeId: null,
            },
          ]);
          return;
        } catch (err) {
          // RAG failed, fall through to show tree response
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
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Sorry, something went wrong. Please try again.",
          options: [],
          nodeId: null,
        },
      ]);
    }
  }

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  /**
   * Initialize session and load FAQs on mount
   */
  useEffect(() => {
    const id = generateUUID();
    setSessionId(id);
    
    // Load FAQs
    fetchFAQs()
      .then(data => setFaqs(data))
      .catch(err => {
        // Silently fail - FAQs not critical
      });
    
    // Check if document is uploaded
    const docUploaded = localStorage.getItem("rag_document_uploaded");
    setHasDocument(docUploaded === "true");
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 flex items-center justify-center p-6">
      <div className="w-full max-w-6xl h-[95vh] flex flex-col rounded-3xl overflow-hidden shadow-2xl bg-white mx-auto">
        
        {/* Header - Vibrant Gradient */}
        <div className="relative bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 px-6 py-5 shadow-xl">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-white/30 rounded-full blur-md animate-pulse"></div>
              <div className="relative w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-lg ring-4 ring-white/30">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full border-2 border-white shadow-md"></div>
            </div>
            <div>
              <h1 className="text-white text-xl font-bold tracking-wide">AI Assistant</h1>
              <p className="text-purple-100 text-sm flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                Always here to help
              </p>
            </div>
            {hasDocument && (
              <div className="ml-4 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-full border border-white/30 flex items-center gap-2">
                <span className="text-sm">📄</span>
                <span className="text-white text-xs font-medium">Document loaded</span>
              </div>
            )}
            <div className="ml-auto">
              <a
                href="/admin"
                className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg text-sm font-medium transition-all duration-200 backdrop-blur-sm border border-white/30"
              >
                ⚙️ Admin
              </a>
            </div>
          </div>
        </div>

        {/* Messages Area - Elegant Gradient Background */}
        <div
          ref={listRef}
          className="flex-1 overflow-y-auto px-8 py-6 space-y-6 bg-gradient-to-b from-slate-50 to-purple-50"
        >
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-4 animate-fade-in">
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-gradient-to-r from-violet-400 to-fuchsia-400 rounded-full blur-2xl opacity-50 animate-pulse"></div>
                  <div className="relative w-24 h-24 mx-auto bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 rounded-full flex items-center justify-center shadow-2xl">
                    <span className="text-5xl">💬</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-gray-700 text-lg font-semibold">Welcome to AI Chat</p>
                  <p className="text-gray-500 text-sm">Start a conversation and let's explore together!</p>
                </div>
              </div>
            </div>
          )}

          {messages.map((m, i) => {
            const isUser = m.sender === "user";

            if (!isUser) {
              // Bot message - LEFT side with stunning effects
              return (
                <div key={i} className="flex justify-start items-start gap-3 animate-slide-in-left pl-4">
                  <div className="relative flex-shrink-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-violet-400 to-purple-400 rounded-full blur-sm opacity-50"></div>
                    <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                      <span className="text-lg">🤖</span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-3 max-w-[75%]">
                    <div className="group relative">
                      <div className="absolute -inset-1 bg-gradient-to-r from-violet-200 to-purple-200 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
                      <div className="relative bg-white rounded-2xl rounded-tl-md px-5 py-4 shadow-lg border border-purple-100">
                        <p className="text-gray-800 text-base leading-relaxed">{m.text}</p>
                      </div>
                    </div>
                    {m.options?.length > 0 && (
                      <div className="flex flex-wrap gap-2.5">
                        {m.options.map((o, j) => (
                          <button
                            key={j}
                            onClick={() =>
                              sendMessage(o.text, true, m.nodeId ?? currentNodeId)
                            }
                            className="relative group overflow-hidden bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 text-white px-5 py-2.5 rounded-full text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 hover:-translate-y-0.5"
                          >
                            <span className="relative z-10">{o.text}</span>
                            <div className="absolute inset-0 bg-gradient-to-r from-fuchsia-600 to-violet-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            } else {
              // User message - RIGHT side with eye-catching gradient
              return (
                <div key={i} className="flex justify-end items-start gap-3 animate-slide-in-right pr-4">
                  <div className="flex flex-col gap-2 max-w-[75%]">
                    <div className="group relative">
                      <div className="absolute -inset-1 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-300"></div>
                      <div className="relative bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-2xl rounded-tr-md px-5 py-4 shadow-xl">
                        <p className="text-white text-base leading-relaxed font-medium">{m.text}</p>
                      </div>
                    </div>
                  </div>
                  <div className="relative flex-shrink-0">
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-indigo-400 rounded-full blur-sm opacity-50"></div>
                    <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
                      <span className="text-lg">👤</span>
                    </div>
                  </div>
                </div>
              );
            }
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start items-start gap-3 animate-slide-in-left pl-4">
              <div className="relative flex-shrink-0">
                <div className="absolute inset-0 bg-gradient-to-br from-violet-400 to-purple-400 rounded-full blur-sm opacity-50"></div>
                <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                  <span className="text-lg">🤖</span>
                </div>
              </div>
              <div className="flex flex-col gap-3 max-w-[75%]">
                <div className="group relative">
                  <div className="absolute -inset-1 bg-gradient-to-r from-violet-200 to-purple-200 rounded-2xl blur opacity-25 transition duration-300"></div>
                  <div className="relative bg-white rounded-2xl rounded-tl-md px-5 py-4 shadow-lg border border-purple-100">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* FAQ Section - Fixed position above input */}
        {faqs.length > 0 && (
          <div className="bg-gradient-to-r from-purple-50 to-violet-50 border-t border-purple-100 px-6 py-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm font-semibold text-purple-700">Quick Questions</span>
              <span className="text-xs text-purple-500">Click to ask</span>
            </div>
            <div className="flex flex-wrap gap-2 max-h-24 overflow-y-auto">
              {faqs.map((faq) => (
                <button
                  key={faq.id}
                  onClick={() => {
                    sendMessage(faq.question, false, null, true);
                  }}
                  className="group relative overflow-hidden bg-white hover:bg-gradient-to-r hover:from-violet-500 hover:to-purple-500 text-purple-700 hover:text-white px-4 py-2 rounded-full text-sm font-medium border-2 border-purple-200 hover:border-transparent shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-300"
                >
                  <span className="relative z-10">{faq.question}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area - Premium Design */}
        <div className="relative bg-white border-t border-purple-100 px-6 py-5 shadow-2xl">
          <div className="flex gap-3 items-center">
            <div className="flex-1 relative">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(input);
                    setInput("");
                  }
                }}
                className="w-full bg-gradient-to-r from-purple-50 to-violet-50 border-2 border-purple-200 rounded-full px-6 py-4 text-base text-gray-800 placeholder-purple-400 focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-200 transition-all shadow-inner"
                placeholder={sessionId ? "Type your message..." : "Loading..."}
                disabled={!sessionId}
              />
            </div>
            <button
              onClick={() => {
                sendMessage(input);
                setInput("");
              }}
              disabled={!sessionId || !input.trim()}
              className="relative group bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 text-white p-4 rounded-full font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-110 transition-all duration-300 disabled:hover:scale-100"
            >
              <svg className="w-6 h-6 transform group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <div className="absolute inset-0 rounded-full bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
            </button>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes slide-in-left {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes slide-in-right {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        .animate-slide-in-left {
          animation: slide-in-left 0.4s ease-out;
        }
        .animate-slide-in-right {
          animation: slide-in-right 0.4s ease-out;
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
