import React, { useState } from 'react';
import { 
  RefreshCw, 
  Download, 
  FileText, 
  Share2, 
  Edit3, 
  Camera, 
  Layout, 
  Instagram, 
  Twitter, 
  MessageSquare,
  Users,
  ChevronRight
} from 'lucide-react';

export default function CampaignCanvas({ data, prompt }) {
  const [isEditMode, setIsEditMode] = useState(false);
  const [postingStatus, setPostingStatus] = useState({}); // Track posting state per post
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const handlePostToInstagram = async (post) => {
    setPostingStatus(prev => ({ ...prev, [post.id]: 'posting' }));

    try {
      const token = localStorage.getItem('token');
      
      // Call backend proxy endpoint instead of Instagram API directly
      const response = await fetch(`${API_URL}/api/instagram/post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          image_url: post.image,
          caption: post.caption || ''
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.msg || 'Failed to post to Instagram');
      }
      
      setPostingStatus(prev => ({ ...prev, [post.id]: 'success' }));
      console.log('Successfully posted to Instagram:', data);
      
      // Show success toast
      setSuccessMessage('🎉 Successfully posted to Instagram!');
      setShowSuccessToast(true);
      
      // Hide toast after 5 seconds
      setTimeout(() => {
        setShowSuccessToast(false);
      }, 5000);
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setPostingStatus(prev => ({ ...prev, [post.id]: null }));
      }, 3000);

    } catch (error) {
      console.error('Instagram posting error:', error);
      setPostingStatus(prev => ({ ...prev, [post.id]: 'error' }));
      alert(`Failed to post: ${error.message}`);
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setPostingStatus(prev => ({ ...prev, [post.id]: null }));
      }, 3000);
    }
  };

  // Mock data if none provided
  const campaign = data || {
    overview: {
      product: "SonicBeat Pro",
      audience: "Fitness Enthusiasts",
      goal: "Raise Brand Awareness"
    },
    socialPosts: [
      { id: 1, type: 'instagram', image: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400', caption: 'Feel the beat, Elevate your performance. #SonicBeatPro' },
      { id: 2, type: 'tiktok', image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400', caption: 'Crush your workout with world-class sound.' },
      { id: 3, type: 'twitter', image: 'https://images.unsplash.com/photo-1491833485246-7588b2e5d994?w=400', caption: 'Wireless freedom for your toughest sets. 🎧🔥' }
    ],
    influencers: [
      { name: "FitWithMaya", followers: "125K", status: "Active" },
      { name: "HealthHero Blog", followers: "88K", status: "Contacted" },
      { name: "ActiveGuy", followers: "210K", status: "Pending" }
    ],
    blogPost: {
      title: "Top 5 Workout Songs to Fuel Your Motivation",
      excerpt: "Get pumped with our ultimate playlist, perfectly paired with the SonicBeat Pro headphones for your best workout ever!"
    },
    moodboard: [
      'https://images.unsplash.com/photo-1548611635-b6e78bb0d50d?w=200',
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=200',
      'https://images.unsplash.com/photo-1571731956672-f2b94d7dd0cb?w=200',
      'https://images.unsplash.com/photo-1538805060514-97d9cc17730c?w=200'
    ]
  };

  const SectionHeader = ({ title, icon: Icon }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
      {Icon && <Icon style={{ width: '1.1rem', height: '1.1rem', color: '#38bdf8' }} />}
      <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{title}</h3>
    </div>
  );

  return (
    <div style={{ padding: '1rem', maxWidth: '1200px', margin: '0 auto', color: '#f9fafb', position: 'relative' }}>
      {/* Success Toast */}
      {showSuccessToast && (
        <div style={{
          position: 'fixed',
          top: '2rem',
          right: '2rem',
          background: 'linear-gradient(135deg, #10b981, #059669)',
          color: '#fff',
          padding: '1rem 1.5rem',
          borderRadius: '0.75rem',
          boxShadow: '0 10px 40px rgba(16, 185, 129, 0.4)',
          zIndex: 9999,
          fontSize: '0.95rem',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          animation: 'slideIn 0.3s ease-out'
        }}>
          {successMessage}
        </div>
      )}
      {/* Header Bar */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', flexDirection: window.innerWidth < 768 ? 'column' : 'row', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1.5rem' }}>
        <div style={{ flex: 1 }}>
          <span style={{ fontSize: '0.7rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.5rem', display: 'block' }}>
            Generation Prompt
          </span>
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.4)', 
            border: '1px solid rgba(148, 163, 184, 0.15)', 
            borderRadius: '0.75rem', 
            padding: '1rem', 
            fontSize: '0.95rem',
            lineHeight: '1.5',
            color: '#e2e8f0',
            fontStyle: 'italic',
            borderLeft: '4px solid #38bdf8'
          }}>
            "{prompt || "No prompt provided. Using default campaign template."}"
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingTop: '1.5rem' }}>
          <button className="secondary-btn" style={{ gap: '0.5rem' }}>
            <RefreshCw style={{ width: '1rem', height: '1rem', paddingRight: '0.50rem' }} />
            Regenerate All
          </button>
          {/* <button className="primary-btn" style={{ gap: '0.5rem' }}>
            <Download style={{ width: '1rem', height: '1rem' }} />
            Export Campaign
          </button> */}
          <div style={{ marginLeft: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem 0.75rem', borderRadius: '999px', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            {/* <span style={{ fontSize: '0.8rem', fontWeight: '600', color: isEditMode ? '#38bdf8' : '#94a3b8' }}>Edit Mode</span> */}
            {/* <button 
              onClick={() => setIsEditMode(!isEditMode)}
              style={{
                width: '2.25rem',
                height: '1.25rem',
                borderRadius: '999px',
                background: isEditMode ? '#38bdf8' : 'rgba(148, 163, 184, 0.3)',
                border: 'none',
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
            >
              <div style={{
                width: '0.85rem',
                height: '0.85rem',
                borderRadius: '50%',
                background: '#fff',
                position: 'absolute',
                top: '0.2rem',
                left: isEditMode ? '1.2rem' : '0.2rem',
                transition: 'all 0.3s'
              }} />
            </button> */}
          </div>
        </div>
      </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: window.innerWidth < 640 ? '1fr' : window.innerWidth < 1024 ? 'repeat(6, 1fr)' : 'repeat(12, 1fr)', gap: '1rem' }}>
        {/* Campaign Overview */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 12', 
          background: 'rgba(15, 23, 42, 0.6)', 
          backdropFilter: 'blur(10px)', 
          borderRadius: '1.25rem', 
          padding: '1rem', 
          border: '1px solid rgba(148, 163, 184, 0.2)',
          display: 'grid',
          gridTemplateColumns: window.innerWidth < 640 ? '1fr' : 'repeat(3, 1fr)',
          gap: '1rem'
        }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase' }}>Product</span>
            <p style={{ margin: '0.25rem 0 0', fontWeight: '600', color: '#e2e8f0' }}>{campaign.overview.product}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase' }}>Audience</span>
            <p style={{ margin: '0.25rem 0 0', fontWeight: '600', color: '#e2e8f0' }}>{campaign.overview.audience}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase' }}>Goal</span>
            <p style={{ margin: '0.25rem 0 0', fontWeight: '600', color: '#e2e8f0' }}>{campaign.overview.goal}</p>
          </div>
        </div>

        {/* Social Media Content */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 6', 
          background: 'rgba(15, 23, 42, 0.6)', 
          borderRadius: '1.25rem', 
          padding: '1.5rem', 
          border: '1px solid rgba(148, 163, 184, 0.2)' 
        }}>
          <SectionHeader title="Social Media Content" icon={Layout} />
          <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
            {campaign.socialPosts.map(post => (
              <div key={post.id} style={{ 
                minWidth: '180px', 
                background: 'rgba(0,0,0,0.3)', 
                borderRadius: '0.75rem', 
                overflow: 'hidden', 
                border: '1px solid rgba(148, 163, 184, 0.1)' 
              }}>
                <img src={post.image} alt="Social" style={{ width: '100%', height: '120px', objectFit: 'cover' }} />
                <div style={{ padding: '0.75rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    {post.type === 'instagram' && <Instagram style={{ width: '0.9rem', height: '0.9rem', color: '#e1306c' }} />}
                    {post.type === 'tiktok' && <MessageSquare style={{ width: '0.9rem', height: '0.9rem', color: '#00f2ea' }} />}
                    {post.type === 'twitter' && <Twitter style={{ width: '0.9rem', height: '0.9rem', color: '#1da1f2' }} />}
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: 0, height: '2.5rem', overflow: 'hidden' }}>{post.caption}</p>
                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.75rem' }}>
                    <button style={{ flex: 1, padding: '0.35rem', borderRadius: '0.4rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(148, 163, 184, 0.2)', color: '#fff', fontSize: '0.65rem', cursor: 'pointer' }}>Edit</button>
                    <button 
                      onClick={() => handlePostToInstagram(post)}
                      disabled={postingStatus[post.id] === 'posting'}
                      style={{ 
                        flex: 1, 
                        padding: '0.35rem', 
                        borderRadius: '0.4rem', 
                        background: postingStatus[post.id] === 'success' ? 'rgba(16, 185, 129, 0.2)' : postingStatus[post.id] === 'error' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.1)', 
                        border: `1px solid ${postingStatus[post.id] === 'success' ? 'rgba(16, 185, 129, 0.3)' : postingStatus[post.id] === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(56, 189, 248, 0.2)'}`, 
                        color: postingStatus[post.id] === 'success' ? '#10b981' : postingStatus[post.id] === 'error' ? '#ef4444' : '#38bdf8', 
                        fontSize: '0.65rem', 
                        cursor: postingStatus[post.id] === 'posting' ? 'not-allowed' : 'pointer',
                        opacity: postingStatus[post.id] === 'posting' ? 0.6 : 1
                      }}
                    >
                      {postingStatus[post.id] === 'posting' ? '...' : postingStatus[post.id] === 'success' ? '✓' : postingStatus[post.id] === 'error' ? '✗' : 'Post'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Influencer Outreach */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 3' : 'span 3', 
          background: 'rgba(15, 23, 42, 0.6)', 
          borderRadius: '1.25rem', 
          padding: '1.5rem', 
          border: '1px solid rgba(148, 163, 184, 0.2)' 
        }}>
          <SectionHeader title="Influencer Outreach" icon={Users} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {campaign.influencers.map((inf, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.75rem', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ width: '1.75rem', height: '1.75rem', borderRadius: '50%', background: 'linear-gradient(135deg, #4f46e5, #06b6d4)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem' }}>{inf.name[0]}</div>
                  <div>
                    <p style={{ margin: 0, fontSize: '0.8rem', fontWeight: '600' }}>{inf.name}</p>
                    <p style={{ margin: 0, fontSize: '0.65rem', color: '#64748b' }}>{inf.followers} followers</p>
                  </div>
                </div>
                <div style={{ width: '0.4rem', height: '0.4rem', borderRadius: '50%', background: inf.status === 'Active' ? '#10b981' : '#f59e0b' }} />
              </div>
            ))}
            <button style={{ all: 'unset', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', padding: '0.6rem', background: 'rgba(255,255,255,0.02)', border: '1px dotted rgba(148, 163, 184, 0.3)', borderRadius: '0.75rem', color: '#94a3b8', fontSize: '0.75rem', cursor: 'pointer', marginTop: '0.5rem' }}>
              Edit Pitches <ChevronRight style={{ width: '0.9rem', height: '0.9rem' }} />
            </button>
          </div>
        </div>

        {/* Export Options */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 3' : 'span 3', 
          background: 'rgba(15, 23, 42, 0.3)', 
          borderRadius: '1.25rem', 
          padding: '1.5rem', 
          border: '1px solid rgba(148, 163, 184, 0.1)' 
        }}>
          <SectionHeader title="Export Options" icon={Share2} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {[
              { label: 'Download Campaign Kit', icon: Layout },
              { label: 'Export as PDF', icon: FileText },
              { label: 'Export to PPT', icon: Layout },
              { label: 'Generate Report', icon: FileText },
            ].map((opt, i) => (
              <button key={i} style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.75rem', 
                padding: '0.75rem', 
                background: 'rgba(255,255,255,0.05)', 
                border: '1px solid rgba(148, 163, 184, 0.1)', 
                borderRadius: '0.75rem', 
                color: '#e2e8f0', 
                fontSize: '0.8rem', 
                textAlign: 'left',
                cursor: 'pointer' 
              }}>
                <opt.icon style={{ width: '1rem', height: '1rem', color: '#64748b' }} />
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Blog Post */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 7', 
          background: 'rgba(15, 23, 42, 0.6)', 
          borderRadius: '1.25rem', 
          padding: '1.5rem', 
          border: '1px solid rgba(148, 163, 184, 0.2)' 
        }}>
          <SectionHeader title="Blog Post" icon={FileText} />
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1.25rem', borderRadius: '1rem', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
            <h4 style={{ margin: '0 0 0.75rem', color: '#fff', fontSize: '1.1rem' }}>{campaign.blogPost.title}</h4>
            <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.5' }}>{campaign.blogPost.excerpt}</p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button className="secondary-btn" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>Edit</button>
              <button className="primary-btn" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>Regenerate</button>
            </div>
          </div>
        </div>

        {/* Moodboard */}
        <div style={{ 
          gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 5', 
          background: 'rgba(15, 23, 42, 0.6)', 
          borderRadius: '1.25rem', 
          padding: '1.5rem', 
          border: '1px solid rgba(148, 163, 184, 0.2)' 
        }}>
          <SectionHeader title="Moodboard" icon={Camera} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
            {campaign.moodboard.map((url, i) => (
              <img key={i} src={url} alt="Mood" style={{ width: '100%', height: '80px', objectFit: 'cover', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.1)' }} />
            ))}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
            <button style={{ flex: 1, padding: '0.5rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(148, 163, 184, 0.2)', color: '#fff', fontSize: '0.75rem', cursor: 'pointer' }}>Edit</button>
            <button style={{ flex: 1, padding: '0.5rem', borderRadius: '0.5rem', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.2)', color: '#38bdf8', fontSize: '0.75rem', cursor: 'pointer' }}>Refresh</button>
          </div>
        </div>
      </div>
      
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        
        @media (max-width: 768px) {
          .secondary-btn, .primary-btn {
            font-size: 0.75rem;
            padding: 0.5rem 0.75rem;
          }
        }
      `}</style>
    </div>
  );
}
