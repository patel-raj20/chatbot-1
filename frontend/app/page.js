/**
 * Landing Page
 * ============
 * Entry point that redirects users based on authentication status.
 * 
 * FLOW:
 *   - Not logged in  /auth/login
 *   - Logged in as user  /chatbot
 *   - Logged in as admin  /chatbot (or /admin based on preference)
 */

"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from './lib/auth';

export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      // User is logged in, redirect to chatbot
      router.push('/chatbot');
    } else {
      // User is not logged in, redirect to login
      router.push('/auth/login');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700">
      <div className="text-white text-xl">Redirecting...</div>
    </div>
  );
}
