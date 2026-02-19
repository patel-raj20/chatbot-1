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
            <div className="relative bg-[#E6F7F5] rounded-2xl rounded-tr-md px-5 py-3.5 shadow-md">
              <p className="text-[#0F3D3A] text-base leading-relaxed">{message.text}</p>
            </div>
          </div>
        </div>
        <div className="relative flex-shrink-0">
          <div className="relative w-10 h-10 rounded-full bg-[#2CB1A6] flex items-center justify-center shadow-md">
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
        <div className="relative w-10 h-10 rounded-full bg-[#4F6BED] flex items-center justify-center shadow-md">
          <span className="text-lg">🤖</span>
        </div>
      </div>
      <div className="flex flex-col gap-3 max-w-[75%]">
        <div className="group relative">
          <div className="relative bg-[#EEF2FF] rounded-2xl rounded-tl-md px-5 py-3.5 shadow-md border border-[#E5E7EB]">
            <p className="text-[#1F2937] text-base leading-relaxed">
              {message.text}
              {message.isStreaming && (
                <span className="inline-block w-2 h-5 bg-[#4F6BED] ml-1 animate-pulse"></span>
              )}
            </p>
          </div>
        </div>
        {message.options?.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {message.options.map((option, index) => (
              <button
                key={index}
                onClick={() => onOptionClick(option.text, message.nodeId)}
                className="bg-[#4F6BED] hover:bg-[#3D56D9] text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-md hover:shadow-lg transition-all duration-200"
              >
                {option.text}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
