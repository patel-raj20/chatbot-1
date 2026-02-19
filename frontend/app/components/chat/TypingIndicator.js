/**
 * Typing Indicator Component
 * =========================
 * Displays animated typing indicator for bot
 */

import { ANIMATIONS } from '../../constants/styles';

export default function TypingIndicator() {
  return (
    <div className={`flex justify-start items-start gap-3 ${ANIMATIONS.slideInLeft} pl-4`}>
      <div className="relative flex-shrink-0">
        <div className="relative w-10 h-10 rounded-full bg-[#4F6BED] flex items-center justify-center shadow-md">
          <span className="text-lg">🤖</span>
        </div>
      </div>
      <div className="flex flex-col gap-3 max-w-[75%]">
        <div className="group relative">
          <div className="relative bg-[#EEF2FF] rounded-2xl rounded-tl-md px-5 py-4 shadow-md border border-[#E5E7EB]">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-[#4F6BED] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-[#4F6BED] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-[#4F6BED] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
