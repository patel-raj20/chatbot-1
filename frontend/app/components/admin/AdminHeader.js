/**
 * Admin Header Component
 * =====================
 * Header specific to admin panel
 */

export default function AdminHeader({ user, onBackToChat, onLogout }) {
  return (
    <div className="bg-[#4F6BED] border-b border-white/10 p-4 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold text-white">Admin Panel</h1>
        <div className="flex items-center gap-3">
          <span className="text-white/90 text-sm">👤 {user?.username}</span>
          <button 
            onClick={onBackToChat}
            className="px-4 py-2 bg-white/90 hover:bg-white text-[#4F6BED] rounded-xl transition-all duration-200 text-sm font-medium shadow-md"
          >
            ← Back to Chat
          </button>
          <button 
            onClick={onLogout}
            className="px-4 py-2 bg-[#E5533D] hover:bg-[#CC3F2B] text-white rounded-xl transition-all duration-200 text-sm font-medium shadow-md"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  );
}
