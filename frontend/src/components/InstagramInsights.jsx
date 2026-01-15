import { useState, useEffect } from 'react';
import { TrendingUp, Users, Eye, MousePointer, Mail, Phone, MessageSquare, MapPin, Globe, Calendar, Loader, AlertCircle, RefreshCw } from 'lucide-react';

export default function InstagramInsights() {
  const [insights, setInsights] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [period, setPeriod] = useState('day');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const fetchInsights = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/instagram/insights?period=${period}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.msg || 'Failed to fetch insights');
      }

      setInsights(data.insights);
      setProfile(data.profile || null);
    } catch (err) {
      console.error('Insights error:', err);
      setError(err.message || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [period]);

  const AnimatedCounter = ({ value, duration = 2000 }) => {
    const [count, setCount] = useState(0);

    useEffect(() => {
      let start = 0;
      const end = parseInt(value);
      if (start === end) return;

      const increment = end / (duration / 16);
      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setCount(end);
          clearInterval(timer);
        } else {
          setCount(Math.ceil(start));
        }
      }, 16);

      return () => clearInterval(timer);
    }, [value, duration]);

    return <span>{count.toLocaleString()}</span>;
  };

  const metricConfigs = [
    { key: 'reach', icon: TrendingUp, label: 'Reach', color: '#38bdf8', gradient: 'linear-gradient(135deg, #38bdf8, #06b6d4)' },
    { key: 'impressions', icon: Eye, label: 'Impressions', color: '#10b981', gradient: 'linear-gradient(135deg, #10b981, #059669)' },
    { key: 'profile_views', icon: MousePointer, label: 'Profile Views', color: '#f59e0b', gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' },
    { key: 'follower_count', icon: Users, label: 'Followers', color: '#6366f1', gradient: 'linear-gradient(135deg, #6366f1, #8b5cf6)' },
    { key: 'website_clicks', icon: Globe, label: 'Website Clicks', color: '#06b6d4', gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)' },
    { key: 'online_followers', icon: Users, label: 'Online Followers', color: '#ec4899', gradient: 'linear-gradient(135deg, #ec4899, #db2777)' },
    { key: 'accounts_engaged', icon: Users, label: 'Accounts Engaged', color: '#8b5cf6', gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' },
    { key: 'total_interactions', icon: MessageSquare, label: 'Total Interactions', color: '#14b8a6', gradient: 'linear-gradient(135deg, #14b8a6, #0d9488)' },
    { key: 'profile_links_taps', icon: MousePointer, label: 'Profile Link Taps', color: '#f97316', gradient: 'linear-gradient(135deg, #f97316, #ea580c)' },
    { key: 'likes', icon: MessageSquare, label: 'Likes', color: '#ef4444', gradient: 'linear-gradient(135deg, #ef4444, #dc2626)' },
    { key: 'comments', icon: MessageSquare, label: 'Comments', color: '#3b82f6', gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)' },
    { key: 'shares', icon: TrendingUp, label: 'Shares', color: '#22c55e', gradient: 'linear-gradient(135deg, #22c55e, #16a34a)' },
    { key: 'saves', icon: MapPin, label: 'Saves', color: '#a855f7', gradient: 'linear-gradient(135deg, #a855f7, #9333ea)' },
    { key: 'replies', icon: MessageSquare, label: 'Replies', color: '#06b6d4', gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)' },
    { key: 'follows_and_unfollows', icon: Users, label: 'Follows & Unfollows', color: '#84cc16', gradient: 'linear-gradient(135deg, #84cc16, #65a30d)' }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%)',
      padding: '2rem',
      position: 'relative',
      overflow: 'visible'
    }}>
      {/* Starfield background */}
      <div style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        backgroundImage: 'radial-gradient(1px 1px at 20% 20%, #ffffff33 0, transparent 60%), radial-gradient(1px 1px at 80% 30%, #ffffff22 0, transparent 60%)',
        opacity: 0.4,
        zIndex: 0
      }} />

      <div style={{ maxWidth: '1400px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <div style={{ marginBottom: '3rem' }}>
          {/* Profile Section */}
          {profile && (
            <div style={{
              background: 'rgba(15, 23, 42, 0.9)',
              borderRadius: '1.5rem',
              padding: '2rem',
              border: '1px solid rgba(148, 163, 184, 0.2)',
              marginBottom: '2rem',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
                flexWrap: 'wrap'
              }}>
                {profile.profile_picture_url && (
                  <img
                    src={profile.profile_picture_url}
                    alt={profile.username}
                    style={{
                      width: '100px',
                      height: '100px',
                      borderRadius: '50%',
                      border: '3px solid rgba(56, 189, 248, 0.5)',
                      boxShadow: '0 8px 25px rgba(56, 189, 248, 0.3)'
                    }}
                  />
                )}
                <div style={{ flex: 1 }}>
                  <h2 style={{
                    fontSize: '1.75rem',
                    fontWeight: '700',
                    color: '#f9fafb',
                    margin: '0 0 0.5rem 0'
                  }}>
                    {profile.name || profile.username}
                  </h2>
                  <p style={{
                    color: '#38bdf8',
                    fontSize: '1.1rem',
                    margin: '0 0 0.75rem 0',
                    fontWeight: '600'
                  }}>
                    @{profile.username}
                  </p>
                  {profile.biography && (
                    <p style={{
                      color: '#9ca3af',
                      fontSize: '0.95rem',
                      margin: '0 0 1rem 0',
                      maxWidth: '600px'
                    }}>
                      {profile.biography}
                    </p>
                  )}
                  <div style={{
                    display: 'flex',
                    gap: '2rem',
                    flexWrap: 'wrap'
                  }}>
                    <div>
                      <span style={{ color: '#f9fafb', fontWeight: '700', fontSize: '1.25rem' }}>
                        {profile.followers_count?.toLocaleString() || 0}
                      </span>
                      <span style={{ color: '#9ca3af', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
                        Followers
                      </span>
                    </div>
                    <div>
                      <span style={{ color: '#f9fafb', fontWeight: '700', fontSize: '1.25rem' }}>
                        {profile.follows_count?.toLocaleString() || 0}
                      </span>
                      <span style={{ color: '#9ca3af', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
                        Following
                      </span>
                    </div>
                    <div>
                      <span style={{ color: '#f9fafb', fontWeight: '700', fontSize: '1.25rem' }}>
                        {profile.media_count?.toLocaleString() || 0}
                      </span>
                      <span style={{ color: '#9ca3af', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
                        Posts
                      </span>
                    </div>
                  </div>
                  {profile.website && (
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: '#38bdf8',
                        fontSize: '0.9rem',
                        marginTop: '0.75rem',
                        display: 'inline-block',
                        textDecoration: 'none'
                      }}
                    >
                      {profile.website}
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1.5rem'
          }}>
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '0.75rem'
              }}>
                <TrendingUp style={{ width: '2.5rem', height: '2.5rem', color: '#38bdf8' }} />
                <h1 style={{
                  fontSize: '2.5rem',
                  fontWeight: '700',
                  background: 'linear-gradient(135deg, #38bdf8, #6366f1)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  margin: 0
                }}>
                  Instagram Insights
                </h1>
              </div>
              <p style={{ color: '#9ca3af', fontSize: '1.1rem', margin: 0 }}>
                Track your account performance and engagement metrics
              </p>
            </div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                style={{
                  padding: '0.75rem 1rem',
                  borderRadius: '0.75rem',
                  background: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#f9fafb',
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  outline: 'none'
                }}
                disabled={loading}
              >
                <option value="day">Daily</option>
                <option value="week">Weekly</option>
                <option value="days_28">28 Days</option>
              </select>

              <button
                onClick={fetchInsights}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.25rem',
                  borderRadius: '0.75rem',
                  background: loading ? 'rgba(56, 189, 248, 0.3)' : 'linear-gradient(135deg, #38bdf8, #06b6d4)',
                  border: 'none',
                  color: '#fff',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.95rem',
                  fontWeight: '600',
                  boxShadow: loading ? 'none' : '0 8px 25px rgba(56, 189, 248, 0.3)'
                }}
              >
                <RefreshCw style={{ width: '1.1rem', height: '1.1rem', animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div style={{
            padding: '1.5rem',
            borderRadius: '1rem',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#fca5a5',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <AlertCircle style={{ width: '1.5rem', height: '1.5rem', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Loading State */}
        {loading && !insights && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '400px',
            gap: '1rem'
          }}>
            <Loader style={{ width: '3rem', height: '3rem', color: '#38bdf8', animation: 'spin 1s linear infinite' }} />
            <p style={{ color: '#9ca3af', fontSize: '1.1rem' }}>Loading insights...</p>
          </div>
        )}

        {/* Metrics Grid */}
        {!loading && insights && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem'
          }}>
            {metricConfigs.map(config => {
              const metric = insights[config.key];
              
              // Always show metric even if value is 0
              const displayValue = metric?.value ?? 0;
              const displayPeriod = metric?.period || period;

              return (
                <div
                  key={config.key}
                  style={{
                    background: 'rgba(15, 23, 42, 0.9)',
                    borderRadius: '1.25rem',
                    padding: '1.75rem',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    position: 'relative',
                    overflow: 'hidden',
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
                    transition: 'transform 0.3s, box-shadow 0.3s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.boxShadow = `0 20px 60px ${config.color}40`;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)';
                  }}
                >
                  {/* Gradient Background Accent */}
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    width: '120px',
                    height: '120px',
                    background: config.gradient,
                    opacity: 0.1,
                    borderRadius: '50%',
                    filter: 'blur(40px)',
                    zIndex: 0
                  }} />

                  <div style={{ position: 'relative', zIndex: 1 }}>
                    {/* Icon */}
                    <div style={{
                      width: '3.5rem',
                      height: '3.5rem',
                      borderRadius: '1rem',
                      background: config.gradient,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.25rem',
                      boxShadow: `0 8px 25px ${config.color}40`
                    }}>
                      <config.icon style={{ width: '1.75rem', height: '1.75rem', color: '#fff' }} />
                    </div>

                    {/* Label */}
                    <p style={{
                      color: '#9ca3af',
                      fontSize: '0.9rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      margin: '0 0 0.5rem 0'
                    }}>
                      {config.label}
                    </p>

                    {/* Value with Animated Counter */}
                    <h2 style={{
                      fontSize: '2.75rem',
                      fontWeight: '800',
                      color: '#f9fafb',
                      margin: '0 0 0.75rem 0',
                      letterSpacing: '-0.02em'
                    }}>
                      <AnimatedCounter value={displayValue} />
                    </h2>

                    {/* Period Badge */}
                    <div style={{
                      display: 'inline-block',
                      padding: '0.35rem 0.75rem',
                      borderRadius: '0.5rem',
                      background: `${config.color}15`,
                      border: `1px solid ${config.color}30`,
                      color: config.color,
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'capitalize'
                    }}>
                      {displayPeriod}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
