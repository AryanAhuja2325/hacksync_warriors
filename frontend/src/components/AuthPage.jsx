import { useState } from 'react';
import { Mail, Lock, User, Chrome } from 'lucide-react';
import { signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "../config/firebase";

export default function AuthPage({ onAuthSuccess = () => {} }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.msg || 'Authentication failed');
      }

      // Store token and user data
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      console.log('Authentication successful:', data.user);
      if (typeof onAuthSuccess === 'function') onAuthSuccess();
    } catch (err) {
      console.error('Auth error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setError('');

    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log('Google sign-in successful:', result.user);

      // Send to backend - signup with just email (no password for Google auth)
      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: result.user.email,
          password: result.user.uid // Use Firebase UID as password for Google users
        })
      });

      const data = await response.json();

      // If user already exists, that's fine - just login
      if (response.ok || data.msg === 'Email already registered') {
        // Try login with same credentials
        const loginResponse = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: result.user.email,
            password: result.user.uid
          })
        });

        const loginData = await loginResponse.json();
        
        if (loginResponse.ok) {
          localStorage.setItem('token', loginData.token);
          localStorage.setItem('user', JSON.stringify({
            ...loginData.user,
            displayName: result.user.displayName,
            photoURL: result.user.photoURL
          }));
          if (typeof onAuthSuccess === 'function') onAuthSuccess();
        } else {
          if (loginData.msg === 'Wrong password') {
            throw new Error('An account exists for this email with a different password. Please use "Forgot password" to reset your password or sign in with your email/password.');
          }
          throw new Error(loginData.msg || 'Login failed');
        }
      } else if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify({
          ...data.user,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL
        }));
        if (typeof onAuthSuccess === 'function') onAuthSuccess();
      } else {
        throw new Error(data.msg || 'Google authentication failed');
      }
    } catch (error) {
      console.error('Google sign-in error:', error);
      setError(error.message || 'Failed to sign in with Google. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      background: 'radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Starfield background */}
      <div style={{
        position: 'absolute',
        inset: '-20%',
        pointerEvents: 'none',
        backgroundImage: 'radial-gradient(1px 1px at 20% 20%, #ffffff33 0, transparent 60%), radial-gradient(1px 1px at 80% 30%, #ffffff22 0, transparent 60%)',
        opacity: 0.4,
        animation: 'drift 60s linear infinite',
        zIndex: 0
      }} />

      <div style={{ width: '100%', maxWidth: '450px', position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-block',
            width: '3rem',
            height: '3rem',
            borderRadius: '50%',
            background: 'radial-gradient(circle at 30% 30%, #38bdf8 0, #6366f1 55%, #a855f7 100%)',
            boxShadow: '0 0 30px rgba(56, 189, 248, 0.8)',
            marginBottom: '1rem'
          }} />
          <h1 style={{ 
            fontSize: '2rem', 
            fontWeight: '700', 
            margin: '0 0 0.5rem', 
            color: '#f9fafb',
            letterSpacing: '-0.02em'
          }}>
            {isLogin ? 'Welcome Back' : 'Join BRANDPULSE'}
          </h1>
          <p style={{ 
            color: '#cbd5f5', 
            fontSize: '0.95rem',
            margin: 0
          }}>
            {isLogin ? 'Sign in to continue your campaign journey' : 'Start creating autonomous campaigns today'}
          </p>
        </div>

        {/* Main Card */}
        <div style={{
          borderRadius: '1.5rem',
          padding: '2.5rem',
          background: 'radial-gradient(circle at 0 0, rgba(56, 189, 248, 0.12), transparent 60%), radial-gradient(circle at 100% 100%, rgba(129, 140, 248, 0.1), transparent 55%), rgba(15, 23, 42, 0.97)',
          border: '1px solid rgba(148, 163, 184, 0.35)',
          boxShadow: '0 30px 90px rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(20px)'
        }}>
          {/* Toggle Buttons */}
          <div style={{
            display: 'flex',
            gap: '0.5rem',
            marginBottom: '2rem',
            padding: '0.35rem',
            borderRadius: '0.75rem',
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(148, 163, 184, 0.2)'
          }}>
            <button
              onClick={() => setIsLogin(true)}
              style={{
                flex: 1,
                padding: '0.75rem',
                borderRadius: '0.5rem',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.3s ease',
                background: isLogin ? 'linear-gradient(135deg, #4f46e5, #06b6d4)' : 'transparent',
                color: isLogin ? '#f9fafb' : '#9ca3af',
                border: 'none',
                cursor: 'pointer',
                boxShadow: isLogin ? '0 4px 15px rgba(56, 189, 248, 0.4)' : 'none'
              }}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              style={{
                flex: 1,
                padding: '0.75rem',
                borderRadius: '0.5rem',
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'all 0.3s ease',
                background: !isLogin ? 'linear-gradient(135deg, #4f46e5, #06b6d4)' : 'transparent',
                color: !isLogin ? '#f9fafb' : '#9ca3af',
                border: 'none',
                cursor: 'pointer',
                boxShadow: !isLogin ? '0 4px 15px rgba(56, 189, 248, 0.4)' : 'none'
              }}
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Error Message */}
            {error && (
              <div style={{
                padding: '0.75rem',
                borderRadius: '0.5rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#fca5a5',
                fontSize: '0.875rem'
              }}>
                {error}
              </div>
            )}

            {/* Email - for both Login and Signup */}
            
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '0.875rem', 
                fontWeight: '600', 
                marginBottom: '0.5rem', 
                color: '#e5e7eb',
                letterSpacing: '0.02em'
              }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  width: '1.25rem', 
                  height: '1.25rem', 
                  color: '#64748b' 
                }} />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    paddingLeft: '3rem',
                    paddingRight: '1rem',
                    paddingTop: '0.875rem',
                    paddingBottom: '0.875rem',
                    borderRadius: '0.75rem',
                    transition: 'all 0.2s',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid rgba(148, 163, 184, 0.3)',
                    color: '#f9fafb',
                    outline: 'none',
                    fontSize: '0.95rem'
                  }}
                  onFocus={(e) => e.target.style.border = '1px solid #6366f1'}
                  onBlur={(e) => e.target.style.border = '1px solid rgba(148, 163, 184, 0.3)'}
                  placeholder="your.email@example.com"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '0.875rem', 
                fontWeight: '600', 
                marginBottom: '0.5rem', 
                color: '#e5e7eb',
                letterSpacing: '0.02em'
              }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  width: '1.25rem', 
                  height: '1.25rem', 
                  color: '#64748b' 
                }} />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  style={{
                    boxSizing: 'border-box',
                    width: '100%',
                    paddingLeft: '3rem',
                    paddingRight: '1rem',
                    paddingTop: '0.875rem',
                    paddingBottom: '0.875rem',
                    borderRadius: '0.75rem',
                    transition: 'all 0.2s',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid rgba(148, 163, 184, 0.3)',
                    color: '#f9fafb',
                    outline: 'none',
                    fontSize: '0.95rem'
                  }}
                  onFocus={(e) => e.target.style.border = '1px solid #6366f1'}
                  onBlur={(e) => e.target.style.border = '1px solid rgba(148, 163, 184, 0.3)'}
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                />
              </div>
            </div>



            {/* Forgot Password - Login only */}
            {isLogin && (
              <div style={{ textAlign: 'right', marginTop: '-0.5rem' }}>
                <button
                  type="button"
                  style={{
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    color: '#38bdf8',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    textDecoration: 'none'
                  }}
                  onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                  onMouseOut={(e) => e.target.style.textDecoration = 'none'}
                >
                  Forgot password?
                </button>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.875rem',
                borderRadius: '0.75rem',
                fontWeight: '700',
                fontSize: '1rem',
                transition: 'all 0.3s ease',
                background: loading ? 'rgba(79, 70, 229, 0.5)' : 'linear-gradient(135deg, #4f46e5, #06b6d4)',
                color: '#f9fafb',
                border: 'none',
                boxShadow: loading ? 'none' : '0 12px 35px rgba(56, 189, 248, 0.5)',
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '0.5rem',
                opacity: loading ? 0.7 : 1
              }}
              onMouseOver={(e) => !loading && (e.target.style.transform = 'translateY(-2px)')}
              onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '1.75rem 0' }}>
            <div style={{ flex: 1, height: '1px', background: 'rgba(148, 163, 184, 0.25)' }} />
            <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              or continue with
            </span>
            <div style={{ flex: 1, height: '1px', background: 'rgba(148, 163, 184, 0.25)' }} />
          </div>

          {/* OAuth Button */}
          <button
            type="button"
            onClick={handleGoogleAuth}
            disabled={loading}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              padding: '0.875rem',
              borderRadius: '0.75rem',
              fontWeight: '600',
              fontSize: '0.95rem',
              transition: 'all 0.3s ease',
              background: 'rgba(255, 255, 255, 0.08)',
              color: '#e5e7eb',
              border: '1px solid rgba(148, 163, 184, 0.3)',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.5 : 1
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.target.style.background = 'rgba(255, 255, 255, 0.12)';
                e.target.style.borderColor = 'rgba(148, 163, 184, 0.5)';
              }
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.08)';
              e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
            }}
          >
            <Chrome style={{ width: '1.25rem', height: '1.25rem' }} />
            {loading ? 'Signing in...' : 'Continue with Google'}
          </button>
        </div>

        {/* Footer */}
        <p style={{ 
          textAlign: 'center', 
          marginTop: '1.5rem', 
          color: '#9ca3af',
          fontSize: '0.9rem'
        }}>
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => setIsLogin(!isLogin)}
            style={{
              fontWeight: '600',
              color: '#38bdf8',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              textDecoration: 'none',
              fontSize: '0.9rem'
            }}
            onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
            onMouseOut={(e) => e.target.style.textDecoration = 'none'}
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
