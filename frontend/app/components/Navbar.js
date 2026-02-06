/**
 * Navigation Bar Component
 * ========================
 * Displays navigation links and user authentication status.
 * 
 * WHY: Consistent navigation across all pages
 * WHERE: Rendered in app/layout.js
 * HOW: Shows different links based on user role
 * 
 * FEATURES:
 *   - Shows username when logged in
 *   - Admin link (only for admins)
 *   - Logout button
 *   - Login/Register links for guests
 */

'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  // ============= LOADING STATE =============
  // Don't show anything while checking auth status
  if (user === undefined) {
    return null;
  }

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* ============= LEFT SIDE - LOGO & LINKS ============= */}
          <div className="flex items-center space-x-6">
            <Link href="/" className="text-xl font-bold hover:text-blue-200">
              ChatBot
            </Link>

            {/* Show navigation links only when authenticated */}
            {isAuthenticated && (
              <>
                <Link 
                  href="/" 
                  className={`hover:text-blue-200 ${
                    pathname === '/' ? 'border-b-2 border-white' : ''
                  }`}
                >
                  Chat
                </Link>

                {/* Admin link - only for admins */}
                {isAdmin && (
                  <Link 
                    href="/admin" 
                    className={`hover:text-blue-200 ${
                      pathname === '/admin' ? 'border-b-2 border-white' : ''
                    }`}
                  >
                    Admin
                  </Link>
                )}
              </>
            )}
          </div>

          {/* ============= RIGHT SIDE - USER INFO ============= */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* User info */}
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-400 rounded-full flex items-center justify-center">
                    <span className="text-sm font-semibold">
                      {user?.username?.[0]?.toUpperCase() || 'U'}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{user?.username}</span>
                    {isAdmin && (
                      <span className="text-xs text-blue-200">Admin</span>
                    )}
                  </div>
                </div>

                {/* Logout button */}
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-blue-700 hover:bg-blue-800 rounded transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                {/* Guest user - show login/register */}
                <Link
                  href="/login"
                  className="px-4 py-2 hover:text-blue-200 transition"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 bg-blue-700 hover:bg-blue-800 rounded transition"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
