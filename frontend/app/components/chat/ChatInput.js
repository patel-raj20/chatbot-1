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
    <div className="relative bg-white border-t border-purple-100 px-6 py-5 shadow-2xl">
      <div className="flex gap-3 items-center">
        <div className="flex-1 relative">
          <input
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="w-full bg-gradient-to-r from-purple-50 to-violet-50 border-2 border-purple-200 rounded-full px-6 py-4 text-base text-gray-800 placeholder-purple-400 focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-200 transition-all shadow-inner"
            placeholder={disabled ? "Loading..." : placeholder}
            disabled={disabled}
          />
        </div>
        <button
          onClick={onSend}
          disabled={disabled || !input.trim()}
          className="relative group bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 text-white p-4 rounded-full font-semibold shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-110 transition-all duration-300 disabled:hover:scale-100"
        >
          <svg className="w-6 h-6 transform group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <div className="absolute inset-0 rounded-full bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        </button>
      </div>
    </div>
  );
}
