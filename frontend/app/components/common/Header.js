/**
 * Header Component
 * ===============
 * Reusable header with gradient design
 */

import { GRADIENTS, BUTTON_STYLES } from '../../constants/styles';

export default function Header({ 
  user, 
  hasDocument, 
  onAdminClick, 
  onLogout,
  showAdminButton = false 
}) {
  return (
    <div className={`relative ${GRADIENTS.header} px-6 py-5 shadow-lg`}>
      <div className="relative flex items-center gap-4">
        <div className="relative">
          <div className="relative w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-md">
            <span className="text-2xl">🤖</span>
          </div>
          <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-[#2CB1A6] rounded-full border-2 border-white shadow-sm"></div>
        </div>
        <div>
          <h1 className="text-white text-xl font-bold tracking-wide">AI Assistant</h1>
          <p className="text-white/90 text-sm flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-[#2CB1A6] rounded-full animate-pulse"></span>
            Always here to help • {user?.username}
          </p>
        </div>
        {hasDocument && (
          <div className="ml-4 px-3 py-1.5 bg-white/90 rounded-xl border border-white/50 flex items-center gap-2 shadow-sm">
            <span className="text-sm">📄</span>
            <span className="text-[#4F6BED] text-xs font-medium">Document loaded</span>
          </div>
        )}
        <div className="ml-auto flex items-center gap-3">
          {showAdminButton && user?.role === 'ADMIN' && (
            <button
              onClick={onAdminClick}
              className={BUTTON_STYLES.secondary}
            >
              ⚙️ Admin
            </button>
          )}
          <button
            onClick={onLogout}
            className={BUTTON_STYLES.danger}
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  );
}
