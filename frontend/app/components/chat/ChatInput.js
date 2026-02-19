/**
 * Chat Input Component
 * ===================
 * Message input field with send button
 */

export default function ChatInput({ 
  input, 
  setInput, 
  onSend, 
  disabled = false,
  placeholder = "Type your message...",
  onSearchQueryChange = null
}) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        onSend();
      }
    }
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setInput(value);
    if (onSearchQueryChange) {
      onSearchQueryChange(value);
    }
  };

  return (
    <div className="relative bg-white border-t border-[#E5E7EB] px-6 py-4 shadow-lg">
      <div className="flex gap-3 items-center">
        <div className="flex-1 relative">
          <input
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full bg-[#F5F7FA] border border-[#E5E7EB] rounded-xl px-5 py-3 text-base text-[#1F2937] placeholder-[#9CA3AF] focus:outline-none focus:border-[#4F6BED] focus:ring-2 focus:ring-[#EEF2FF] transition-all duration-200"
            placeholder={disabled ? "Loading..." : placeholder}
            disabled={disabled}
          />
        </div>
        <button
          onClick={onSend}
          disabled={disabled || !input.trim()}
          className="bg-[#4F6BED] hover:bg-[#3D56D9] text-white p-3.5 rounded-xl font-semibold shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  );
}
