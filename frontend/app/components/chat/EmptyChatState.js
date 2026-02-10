/**
 * Empty Chat State Component
 * =========================
 * Displayed when no messages exist
 */

export default function EmptyChatState() {
  return (
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
  );
}
