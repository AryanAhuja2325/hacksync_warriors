import React, { useState } from 'react';
import { Mail, Lock, User, Apple, Facebook } from 'lucide-react';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = () => {
    console.log('Form submitted:', formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-black mb-2">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-600">
            {isLogin ? 'Sign in to continue' : 'Sign up to get started'}
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white border-2 border-black rounded-2xl p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
          {/* Toggle Buttons */}
          <div className="flex gap-2 mb-8 p-1 bg-gray-100 rounded-lg">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 rounded-md font-semibold transition-all ${
                isLogin
                  ? 'bg-black text-white'
                  : 'bg-transparent text-gray-600 hover:text-black'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 rounded-md font-semibold transition-all ${
                !isLogin
                  ? 'bg-black text-white'
                  : 'bg-transparent text-gray-600 hover:text-black'
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <div className="space-y-5">
            {/* Username - Login only */}
            {isLogin && (
              <div>
                <label className="block text-sm font-semibold text-black mb-2">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-black transition-all"
                    placeholder="Enter your username"
                    required
                  />
                </div>
              </div>
            )}

            {/* Email - Sign Up only */}
            {!isLogin && (
              <div>
                <label className="block text-sm font-semibold text-black mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-black transition-all"
                    placeholder="Enter your email"
                    required
                  />
                </div>
              </div>
            )}

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-black mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-11 pr-4 py-3 border-2 border-black rounded-lg focus:outline-none focus:ring-2 focus:ring-black transition-all"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            {/* Forgot Password - Login only */}
            {isLogin && (
              <div className="text-right">
                <button
                  type="button"
                  className="text-sm text-gray-600 hover:text-black font-medium transition-colors"
                >
                  Forgot password?
                </button>
              </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,0.3)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,0.3)] hover:translate-x-[2px] hover:translate-y-[2px]"
            >
              {isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </div>

          {/* OAuth Options - Sign Up only */}
          {!isLogin && (
            <>
              <div className="flex items-center gap-4 my-6">
                <div className="flex-1 h-px bg-gray-300"></div>
                <span className="text-sm text-gray-500 font-medium">OR</span>
                <div className="flex-1 h-px bg-gray-300"></div>
              </div>

              <div className="space-y-3">
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-3 py-3 border-2 border-black rounded-lg font-semibold hover:bg-gray-50 transition-all"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-3 py-3 border-2 border-black rounded-lg font-semibold hover:bg-gray-50 transition-all"
                >
                  <Apple className="w-5 h-5" />
                  Continue with Apple
                </button>
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-3 py-3 border-2 border-black rounded-lg font-semibold hover:bg-gray-50 transition-all"
                >
                  <Facebook className="w-5 h-5 fill-[#1877F2]" />
                  Continue with Facebook
                </button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <p className="text-center mt-6 text-gray-600">
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-black font-semibold hover:underline"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}