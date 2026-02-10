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
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
