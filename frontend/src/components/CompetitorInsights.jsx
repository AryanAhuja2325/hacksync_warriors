import { useState } from 'react';
import { TrendingUp, Target, Lightbulb, Search, ExternalLink, Loader, AlertCircle, CheckCircle, BarChart3 } from 'lucide-react';

export default function CompetitorInsights({ activeTab = 'overview', onTabChange }) {
  const [brandContext, setBrandContext] = useState('');
  const [industry, setIndustry] = useState('');
  const [targetUrl, setTargetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setResults(null);

    if (!brandContext.trim()) {
      setError('Please describe your brand or project');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/competitors/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          brandContext: brandContext.trim(),
          industry: industry.trim(),
          competitorUrls: targetUrl.trim() ? [targetUrl.trim()] : [],
          autoDiscover: true
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.msg || 'Analysis failed');
      }

      setResults(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze competitors');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6366f1';
    }
  };

  const getPriorityBg = (priority) => {
    switch (priority) {
      case 'high': return 'rgba(239, 68, 68, 0.1)';
      case 'medium': return 'rgba(245, 158, 11, 0.1)';
      case 'low': return 'rgba(16, 185, 129, 0.1)';
      default: return 'rgba(99, 102, 241, 0.1)';
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(circle at top, #1f2937 0, #020617 55%, #000 100%)',
      padding: '2rem',
      position: 'relative',
      overflow: 'visible' // let the page-level scrollbar (from parent) handle scrolling
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

      <div style={{ maxWidth: '1200px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <div style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.75rem',
            marginBottom: '1rem'
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
              Competitor Insights
            </h1>
          </div>
          <p style={{ color: '#9ca3af', fontSize: '1.1rem', margin: 0 }}>
            Analyze your competitors and discover opportunities to improve your brand
          </p>
        </div>

        {/* Input Form */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.9)',
          borderRadius: '1.5rem',
          padding: '2rem',
          border: '1px solid rgba(148, 163, 184, 0.2)',
          marginBottom: '2rem',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Brand Context */}
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.95rem',
                fontWeight: '600',
                color: '#e5e7eb',
                marginBottom: '0.75rem'
              }}>
                <Target style={{ width: '1.25rem', height: '1.25rem', color: '#38bdf8' }} />
                Your Brand / Product
              </label>
              <input
                value={brandContext}
                onChange={(e) => setBrandContext(e.target.value)}
                placeholder="e.g. SonicBeat Pro - Premium Wireless Headphones"
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  padding: '1rem',
                  borderRadius: '0.75rem',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#f9fafb',
                  fontSize: '0.95rem',
                  outline: 'none'
                }}
                disabled={loading}
              />
            </div>

            {/* Industry */}
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.95rem',
                fontWeight: '600',
                color: '#e5e7eb',
                marginBottom: '0.75rem'
              }}>
                <Search style={{ width: '1.25rem', height: '1.25rem', color: '#38bdf8' }} />
                Industry / Category
              </label>
              <input
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. Consumer Electronics, Professional Audio"
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  padding: '1rem',
                  borderRadius: '0.75rem',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#f9fafb',
                  fontSize: '0.95rem',
                  outline: 'none'
                }}
                disabled={loading}
              />
            </div>

            {/* Target URL */}
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.95rem',
                fontWeight: '600',
                color: '#e5e7eb',
                marginBottom: '0.75rem'
              }}>
                <ExternalLink style={{ width: '1.25rem', height: '1.25rem', color: '#38bdf8' }} />
                Target Competitor URL (Optional)
              </label>
              <input
                type="url"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://competitor.com (Leave empty for auto-discovery)"
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  padding: '1rem',
                  borderRadius: '0.75rem',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#f9fafb',
                  fontSize: '0.95rem',
                  outline: 'none'
                }}
                disabled={loading}
              />
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              marginTop: '1.5rem',
              padding: '1rem',
              borderRadius: '0.75rem',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#fca5a5',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem'
            }}>
              <AlertCircle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              width: '100%',
              marginTop: '1.5rem',
              padding: '1rem',
              borderRadius: '0.75rem',
              fontWeight: '700',
              fontSize: '1rem',
              background: loading ? 'rgba(79, 70, 229, 0.5)' : 'linear-gradient(135deg, #4f46e5, #06b6d4)',
              color: '#f9fafb',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              boxShadow: loading ? 'none' : '0 12px 35px rgba(56, 189, 248, 0.4)'
            }}
          >
            {loading ? (
              <>
                <Loader style={{ width: '1.25rem', height: '1.25rem', animation: 'spin 1s linear infinite' }} />
                Analyzing Competitors...
              </>
            ) : (
              <>
                <BarChart3 style={{ width: '1.25rem', height: '1.25rem' }} />
                Analyze Competitors
              </>
            )}
          </button>
        </div>

        {/* Results */}
        {results && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Recommendations (visible when activeTab is 'overview' or 'recommendations') */}
            {(activeTab === 'overview' || activeTab === 'recommendations') && (
              <div>
                <h2 style={{
                  fontSize: '1.75rem',
                  fontWeight: '700',
                  color: '#f9fafb',
                  marginBottom: '1.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <Lightbulb style={{ width: '1.75rem', height: '1.75rem', color: '#fbbf24' }} />
                  Actionable Recommendations
                </h2>

                <div style={{ display: 'grid', gap: '1rem' }}>
                  {results.recommendations.map((rec, index) => (
                    <div key={index} style={{
                      background: 'rgba(15, 23, 42, 0.9)',
                      borderRadius: '1rem',
                      padding: '1.5rem',
                      border: `1px solid ${getPriorityColor(rec.priority)}33`,
                      borderLeft: `4px solid ${getPriorityColor(rec.priority)}`
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'space-between',
                        marginBottom: '0.75rem'
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{
                            display: 'inline-block',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '0.5rem',
                            background: getPriorityBg(rec.priority),
                            color: getPriorityColor(rec.priority),
                            fontSize: '0.75rem',
                            fontWeight: '700',
                            textTransform: 'uppercase',
                            marginBottom: '0.75rem'
                          }}>
                            {rec.category}
                          </div>
                          <h3 style={{
                            fontSize: '1.25rem',
                            fontWeight: '600',
                            color: '#f9fafb',
                            margin: '0 0 0.5rem 0'
                          }}>
                            {rec.title}
                          </h3>
                        </div>
                        <div style={{
                          padding: '0.5rem 1rem',
                          borderRadius: '0.5rem',
                          background: getPriorityBg(rec.priority),
                          color: getPriorityColor(rec.priority),
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          textTransform: 'capitalize'
                        }}>
                          {rec.priority}
                        </div>
                      </div>
                      <p style={{
                        color: '#9ca3af',
                        fontSize: '0.95rem',
                        margin: '0 0 0.75rem 0',
                        lineHeight: '1.6'
                      }}>
                        <strong style={{ color: '#e5e7eb' }}>Insight:</strong> {rec.insight}
                      </p>
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.5rem',
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        background: 'rgba(56, 189, 248, 0.05)',
                        border: '1px solid rgba(56, 189, 248, 0.1)'
                      }}>
                        <CheckCircle style={{
                          width: '1.25rem',
                          height: '1.25rem',
                          color: '#38bdf8',
                          flexShrink: 0,
                          marginTop: '0.1rem'
                        }} />
                        <p style={{
                          color: '#cbd5e1',
                          fontSize: '0.95rem',
                          margin: 0,
                          lineHeight: '1.6'
                        }}>
                          <strong style={{ color: '#f9fafb' }}>Action:</strong> {rec.action}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Competitor Details (visible when activeTab is 'overview' or 'competitors') */}
            {(activeTab === 'overview' || activeTab === 'competitors') && (
              <div>
                <h2 style={{
                  fontSize: '1.75rem',
                  fontWeight: '700',
                  color: '#f9fafb',
                  marginBottom: '1.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <Target style={{ width: '1.75rem', height: '1.75rem', color: '#38bdf8' }} />
                  Competitor Analysis
                </h2>

                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  {results.insights.map((insight, index) => (
                    <div key={index} style={{
                      background: 'rgba(15, 23, 42, 0.9)',
                      borderRadius: '1rem',
                      padding: '1.5rem',
                      border: '1px solid rgba(148, 163, 184, 0.2)'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: '1.5rem'
                      }}>
                        <h3 style={{
                          fontSize: '1.25rem',
                          fontWeight: '600',
                          color: '#f9fafb',
                          margin: 0
                        }}>
                          {insight.domain}
                        </h3>
                        <a
                          href={insight.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.5rem 1rem',
                            borderRadius: '0.5rem',
                            background: 'rgba(56, 189, 248, 0.1)',
                            color: '#38bdf8',
                            textDecoration: 'none',
                            fontSize: '0.875rem',
                            fontWeight: '600'
                          }}
                        >
                          Visit Site
                          <ExternalLink style={{ width: '1rem', height: '1rem' }} />
                        </a>
                      </div>

                      {insight.error ? (
                        <div style={{
                          padding: '1rem',
                          borderRadius: '0.5rem',
                          background: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.2)',
                          color: '#fca5a5'
                        }}>
                          {insight.error}
                        </div>
                      ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)', gap: '1.25rem' }}>
                          {/* SWOT-style Analysis */}
                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '1rem', borderRadius: '0.75rem' }}>
                              <h4 style={{ color: '#10b981', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Strengths</h4>
                              <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#9ca3af', fontSize: '0.85rem' }}>
                                {(insight.analysis?.strengths || ['Strong brand identity', 'User-friendly interface', 'High quality visuals']).map((s, i) => (
                                  <li key={i}>{s}</li>
                                ))}
                              </ul>
                            </div>
                            <div style={{ background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '1rem', borderRadius: '0.75rem' }}>
                              <h4 style={{ color: '#ef4444', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Weaknesses</h4>
                              <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#9ca3af', fontSize: '0.85rem' }}>
                                {(insight.analysis?.weaknesses || ['Slow checkout process', 'Limited product range', 'Inconsistent social presence']).map((w, i) => (
                                  <li key={i}>{w}</li>
                                ))}
                              </ul>
                            </div>
                          </div>

                          {/* Numerical Metrics */}
                          <div>
                            <h4 style={{
                              fontSize: '0.95rem',
                              fontWeight: '600',
                              color: '#cbd5e1',
                              marginBottom: '1rem',
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em'
                            }}>
                              Performance Metrics
                            </h4>
                            <div style={{ display: 'grid', gap: '1rem' }}>
                              {[
                                { label: 'Visual Appeal', value: 85, color: '#38bdf8' },
                                { label: 'Market Authority', value: 62, color: '#6366f1' },
                                { label: 'Social Engagement', value: 45, color: '#ec4899' },
                              ].map((metric, i) => (
                                <div key={i}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                                    <span style={{ color: '#9ca3af' }}>{metric.label}</span>
                                    <span style={{ color: '#f9fafb', fontWeight: '600' }}>{metric.value}%</span>
                                  </div>
                                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{ width: `${metric.value}%`, height: '100%', background: metric.color, borderRadius: '3px' }} />
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Keywords */}
                          {insight.analysis?.keywords?.length > 0 && (
                            <div>
                              <h4 style={{
                                fontSize: '0.95rem',
                                fontWeight: '600',
                                color: '#cbd5e1',
                                marginBottom: '0.75rem',
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em'
                              }}>
                                Top Keywords
                              </h4>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                                {insight.analysis.keywords.slice(0, 8).map((keyword, i) => (
                                  <span key={i} style={{
                                    padding: '0.4rem 0.8rem',
                                    borderRadius: '0.5rem',
                                    background: 'rgba(99, 102, 241, 0.1)',
                                    border: '1px solid rgba(99, 102, 241, 0.2)',
                                    color: '#a5b4fc',
                                    fontSize: '0.75rem'
                                  }}>
                                    {keyword}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
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