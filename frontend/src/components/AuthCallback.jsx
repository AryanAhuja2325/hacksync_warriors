import { useEffect } from 'react';

export default function AuthCallback({ onAuthSuccess }) {
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');

    if (error) {
      console.error('OAuth error:', error);
      alert('Authentication failed. Please try again.');
      window.location.href = '/';
      return;
    }

    if (code) {
      // For now, simulate successful auth
      // In production, send code to backend
      console.log('OAuth code received:', code);
      
      // TODO: Send code to backend
      // fetch('/api/auth/google/callback', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ code })
      // })
      //   .then(res => res.json())
      //   .then(data => {
      //     localStorage.setItem('token', data.token);
      //     onAuthSuccess();
      //   });

      // Simulate success for now
      setTimeout(() => {
        onAuthSuccess();
      }, 1000);
    }
  }, [onAuthSuccess]);

  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '100vh',
      background: 'radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%)',
      color: '#f9fafb',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <div style={{
        width: '3rem',
        height: '3rem',
        borderRadius: '50%',
        background: 'radial-gradient(circle at 30% 30%, #38bdf8 0, #6366f1 55%, #a855f7 100%)',
        boxShadow: '0 0 30px rgba(56, 189, 248, 0.8)',
        animation: 'pulse 2s ease-in-out infinite'
      }} />
      <div style={{ fontSize: '1.25rem', fontWeight: '600' }}>
        Authenticating with Google...
      </div>
      <div style={{ fontSize: '0.875rem', color: '#9ca3af' }}>
        Please wait while we verify your account
      </div>
    </div>
  );
}
