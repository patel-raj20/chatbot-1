/**
 * Chat Interface (Protected)
 * ===========================
 * Main chat page with RAG fallback mechanism.
 * 
 * AUTHENTICATION:
 *   - Requires user OR admin role
 *   - Redirects to /auth/login if not authenticated
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

import { useRouter } from "next/navigation";
import { useAuthGuard } from "../lib/authGuard";
import { logout } from "../lib/auth";
import { useChat } from "../hooks/useChat";
import { GRADIENTS, KEYFRAMES } from "../constants/styles";
import Loading from "../components/common/Loading";
import Header from "../components/common/Header";
import ChatMessage from "../components/chat/ChatMessage";
import TypingIndicator from "../components/chat/TypingIndicator";
import EmptyChatState from "../components/chat/EmptyChatState";
import WorkflowQuestionsSection from "../components/chat/WorkflowQuestionsSection";
import FAQSuggestionsDropdown from "../components/chat/FAQSuggestionsDropdown";
import ChatInput from "../components/chat/ChatInput";

export default function ChatTestUI() {
  const router = useRouter();
  const { loading: authLoading, user } = useAuthGuard();
  const {
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
    isTyping,
    listRef,
    sendMessage
  } = useChat(user);

  // Show loading while auth check is in progress
  if (authLoading) {
    return <Loading />;
  }

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  const handleSendMessage = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput("");
      setFaqSearchQuery(""); // Clear search when message is sent
    }
  };

  const handleOptionClick = (optionText, nodeId) => {
    sendMessage(optionText, true, nodeId || currentNodeId);
  };

  const handleWorkflowClick = (triggerText) => {
    sendMessage(triggerText, false, null, false);
  };

  const handleFaqSuggestionClick = (question) => {
    sendMessage(question, false, null, true);
    setInput("");
    setFaqSearchQuery("");
  };

  return (
    <div className={`min-h-screen ${GRADIENTS.primary} flex items-center justify-center p-6`}>
      <div className="w-full max-w-6xl h-[95vh] flex flex-col rounded-xl overflow-hidden shadow-xl bg-white mx-auto border border-[#E5E7EB]">

        {/* Header */}
        <Header
          user={user}
          onAdminClick={() => router.push('/admin')}
          onLogout={handleLogout}
          showAdminButton={true}
        />

        {/* Messages Area */}
        <div
          ref={listRef}
          className={`flex-1 overflow-y-auto px-8 py-6 space-y-6 ${GRADIENTS.messagesBg}`}
        >
          {/* Workflow Questions Section */}
          <WorkflowQuestionsSection 
            workflowQuestions={workflowQuestions}
            onQuestionClick={handleWorkflowClick}
            isDisabled={isTyping}
          />

          {messages.length === 0 && <EmptyChatState />}

          {messages.map((message, index) => (
            <ChatMessage
              key={index}
              message={message}
              onOptionClick={handleOptionClick}
            />
          ))}

          {isTyping && <TypingIndicator />}
        </div>

        {/* Input Area with FAQ Dropdown */}
        <div className="relative">
          <FAQSuggestionsDropdown
            suggestions={faqSuggestions}
            onSuggestionClick={handleFaqSuggestionClick}
            isLoading={isSearchingFaqs}
            isVisible={faqSearchQuery.length >= 2}
          />
          <ChatInput
            input={input}
            setInput={setInput}
            onSend={handleSendMessage}
            disabled={!sessionId}
            onSearchQueryChange={setFaqSearchQuery}
          />
        </div>
      </div>

      <style jsx global>{KEYFRAMES}</style>
    </div>
  );
}
