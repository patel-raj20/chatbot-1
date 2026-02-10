/**
 * Login Page
 * ==========
 * User authentication page with username/password login.
 * 
 * FLOW:
 *   1. User enters username and password
 *   2. Submit credentials to /auth/login endpoint
 *   3. Receive JWT token + user info
 *   4. Save to localStorage
 *   5. Redirect based on role:
 *      - admin → /admin
 *      - user → /chatbot
 * 
 * FEATURES:
 *   - Form validation
 *   - Error handling
 *   - Link to signup page
 *   - Responsive design
 */

"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { isAuthenticated, saveAuth } from '../../lib/auth';
import AuthForm from '../../components/auth/AuthForm';
import { API_BASE_URL } from '../../constants/api';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/chatbot');
    }
  }, [router]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Basic validation
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Save authentication data
      saveAuth(data.access_token, {
        user_id: data.user_id,
        username: data.username,
        role: data.role
      });

      // Redirect based on role
      if (data.role === 'ADMIN') {
        router.push('/admin');
      } else {
        router.push('/chatbot');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <AuthForm
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        error={error}
        setError={setError}
        loading={loading}
        isSignup={false}
      />
      {/* Signup Link */}
      <div className="absolute bottom-8 text-center">
        <p className="text-gray-600">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="text-indigo-600 hover:text-indigo-500 font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
