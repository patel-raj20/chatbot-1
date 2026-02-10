/**
 * Admin Header Component
 * =====================
 * Header specific to admin panel
 */

export default function AdminHeader({ user, onBackToChat, onLogout }) {
  return (
    <div className="bg-slate-900/50 backdrop-blur-lg border-b border-white/10 p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-bold text-white">Admin Panel</h1>
        <div className="flex items-center gap-3">
          <span className="text-purple-200 text-sm">👤 {user?.username}</span>
          <button 
            onClick={onBackToChat}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors text-sm"
          >
            ← Back to Chat
          </button>
          <button 
            onClick={onLogout}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  );
}
