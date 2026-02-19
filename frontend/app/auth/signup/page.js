/**
 * Signup Page
 * ===========
 * User registration page for creating new accounts.
 * 
 * FLOW:
 *   1. User enters username and password
 *   2. Submit to /auth/signup endpoint
 *   3. Account created with role='user' (default)
 *   4. Redirect to login page
 * 
 * FEATURES:
 *   - Form validation
 *   - Password strength indication
 *   - Error handling
 *   - Link to login page
 *   - Responsive design
 * 
 * SECURITY:
 *   - Minimum password length: 6 characters
 *   - Passwords are hashed server-side (bcrypt)
 *   - All users default to 'user' role
 *   - Admin role must be manually assigned
 */

"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { isAuthenticated } from '../../lib/auth';
import AuthForm from '../../components/auth/AuthForm';
import { API_BASE_URL } from '../../constants/api';

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
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

    // Validation
    if (!formData.username || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      // Success - redirect to login
      alert('Account created successfully! Please log in.');
      router.push('/auth/login');
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F5F7FA] px-4">
      <AuthForm
        formData={formData}
        onChange={handleChange}
        onSubmit={handleSubmit}
        error={error}
        setError={setError}
        loading={loading}
        isSignup={true}
      />
      {/* Login Link */}
      <div className="absolute bottom-8 text-center">
        <p className="text-[#6B7280]">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-[#4F6BED] hover:text-[#3D56D9] font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
