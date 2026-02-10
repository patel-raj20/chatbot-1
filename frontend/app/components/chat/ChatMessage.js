/**
 * Chat Message Component
 * =====================
 * Displays individual chat messages (user or bot)
 */

import { ANIMATIONS } from '../../constants/styles';

export default function ChatMessage({ message, onOptionClick }) {
  const isUser = message.sender === "user";

  if (isUser) {
    return (
      <div className={`flex justify-end items-start gap-3 ${ANIMATIONS.slideInRight} pr-4`}>
        <div className="flex flex-col gap-2 max-w-[75%]">
          <div className="group relative">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-300"></div>
            <div className="relative bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-2xl rounded-tr-md px-5 py-4 shadow-xl">
              <p className="text-white text-base leading-relaxed font-medium">{message.text}</p>
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

  // Bot message
  return (
    <div className={`flex justify-start items-start gap-3 ${ANIMATIONS.slideInLeft} pl-4`}>
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
            <p className="text-gray-800 text-base leading-relaxed">
              {message.text}
              {message.isStreaming && (
                <span className="inline-block w-2 h-5 bg-purple-500 ml-1 animate-pulse"></span>
              )}
            </p>
          </div>
        </div>
        {message.options?.length > 0 && (
          <div className="flex flex-wrap gap-2.5">
            {message.options.map((option, index) => (
              <button
                key={index}
                onClick={() => onOptionClick(option.text, message.nodeId)}
                className="relative group overflow-hidden bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 text-white px-5 py-2.5 rounded-full text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 hover:-translate-y-0.5"
              >
                <span className="relative z-10">{option.text}</span>
                <div className="absolute inset-0 bg-gradient-to-r from-fuchsia-600 to-violet-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
