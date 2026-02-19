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
          <div className="relative w-24 h-24 mx-auto bg-[#EEF2FF] rounded-full flex items-center justify-center shadow-md border-2 border-[#E5E7EB]">
            <span className="text-5xl">💬</span>
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-[#1F2937] text-lg font-semibold">Welcome to AI Chat</p>
          <p className="text-[#6B7280] text-sm">Start a conversation and let's explore together!</p>
        </div>
      </div>
    </div>
  );
}
