/**
 * Protected Route Component
 * ==========================
 * Wrapper component that prevents unauthorized access to pages.
 * 
 * WHY: Enforce authentication and authorization
 * WHERE: Wrap protected pages (chat, admin)
 * HOW: Check auth status, redirect if not authorized
 * 
 * USAGE:
 *   <ProtectedRoute>
 *     <ChatPage />
 *   </ProtectedRoute>
 *   
 *   <ProtectedRoute requireAdmin>
 *     <AdminPanel />
 *   </ProtectedRoute>
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, requireAdmin = false }) {
  const { isAuthenticated, isAdmin, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for auth state to load
    if (isLoading) return;

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Redirect to chat if admin access required but user is not admin
    if (requireAdmin && !isAdmin) {
      alert('Access denied. Admin privileges required.');
      router.push('/');
      return;
    }
  }, [isAuthenticated, isAdmin, isLoading, requireAdmin, router]);

  //============= LOADING STATE =============
  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // ============= NOT AUTHENTICATED =============
  // Don't render children if not authenticated (will redirect)
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Redirecting to login...</p>
      </div>
    );
  }

  // ============= NOT AUTHORIZED (ADMIN REQUIRED) =============
  // Don't render children if admin required but user is not admin
  if (requireAdmin && !isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-2">Access Denied</h1>
          <p className="text-gray-600">You do not have permission to access this page.</p>
          <p className="text-gray-600 mt-4">Redirecting...</p>
        </div>
      </div>
    );
  }

  // ============= AUTHORIZED =============
  // Render protected content
  return <>{children}</>;
}
