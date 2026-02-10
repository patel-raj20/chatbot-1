/**
 * Auth Form Component
 * ==================
 * Reusable form for login and signup
 */

import ErrorMessage from '../common/ErrorMessage';

export default function AuthForm({ 
  formData, 
  onChange, 
  onSubmit, 
  error, 
  setError,
  loading, 
  isSignup = false 
}) {
  return (
    <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-2xl">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          {isSignup ? 'Create Account' : 'Welcome Back'}
        </h1>
        <p className="text-gray-600">
          {isSignup ? 'Sign up to get started' : 'Sign in to access your account'}
        </p>
      </div>

      {/* Error Message */}
      <ErrorMessage error={error} onClose={() => setError('')} />

      {/* Form */}
      <form onSubmit={onSubmit} className="mt-8 space-y-6">
        <div className="space-y-4">
          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={formData.username}
              onChange={onChange}
              className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 ${
                isSignup ? 'focus:ring-purple-500 focus:border-purple-500' : 'focus:ring-indigo-500 focus:border-indigo-500'
              } transition`}
              placeholder={isSignup ? "Choose a username (min 3 characters)" : "Enter your username"}
            />
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={onChange}
              className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 ${
                isSignup ? 'focus:ring-purple-500 focus:border-purple-500' : 'focus:ring-indigo-500 focus:border-indigo-500'
              } transition`}
              placeholder={isSignup ? "Create a password (min 6 characters)" : "Enter your password"}
            />
          </div>

          {/* Confirm Password Field (Signup only) */}
          {isSignup && (
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword || ''}
                onChange={onChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                placeholder="Confirm your password"
              />
            </div>
          )}
        </div>

        {/* Info Box (Signup only) */}
        {isSignup && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg text-sm">
            <p className="font-medium">📝 Account Info</p>
            <p className="mt-1">All new accounts start with <strong>user</strong> role. Contact admin for role upgrades.</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full ${
            isSignup ? 'bg-purple-600 hover:bg-purple-700 focus:ring-purple-500' : 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500'
          } text-white py-3 px-4 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {loading ? (isSignup ? 'Creating account...' : 'Signing in...') : (isSignup ? 'Sign Up' : 'Sign In')}
        </button>
      </form>
    </div>
  );
}
