import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Download, 
  FileText, 
  Share2, 
  Edit3, 
  Camera, 
  Layout, 
  Twitter, 
  MessageSquare,
  Users,
  ChevronRight
} from 'lucide-react';

export default function CampaignCanvas({ data, prompt }) {
  const [isEditMode, setIsEditMode] = useState(false);
  const [loading, setLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  // Simulate API response for campaign data
  useEffect(() => {
    // Simulate endpoint delay
    const timer = setTimeout(() => {
      setLoading(false);
    }, 20000); // 2 second delay for skeleton

    return () => clearTimeout(timer);
  }, []);

  // Replace Instagram posting with a simple share helper (copies image URL to clipboard)
  const handleShare = (post) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(post.image).then(() => {
        alert('Image URL copied to clipboard');
      }).catch(() => {
        alert(post.image);
      });
    } else {
      alert(post.image);
    }
  }; 

  // Mock data if none provided (loaded after simulation)
  const campaign = data || {
    overview: {
      product: "SonicBeat Pro",
      audience: "Fitness Enthusiasts",
      goal: "Raise Brand Awareness"
    },
    socialPosts: [
      { id: 1, type: 'social', image: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400', caption: 'Feel the beat, Elevate your performance. #SonicBeatPro' },
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

  // Skeleton Components
  const SkeletonBar = ({ width = '100%' }) => (
    <div style={{
      width,
      height: '12px',
      background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)',
      backgroundSize: '200% 100%',
      animation: 'loading 1.5s infinite',
      borderRadius: '4px',
      marginBottom: '8px'
    }} />
  );

  const SkeletonOverview = () => (
    <div style={{ display: 'grid', gridTemplateColumns: window.innerWidth < 640 ? '1fr' : 'repeat(3, 1fr)', gap: '1rem' }}>
      {[1, 2, 3].map(i => (
        <div key={i}>
          <SkeletonBar width="60%" />
          <SkeletonBar width="80%" />
        </div>
      ))}
    </div>
  );

  const SkeletonSocialPost = () => (
    <div style={{ minWidth: '180px', background: 'rgba(0,0,0,0.3)', borderRadius: '0.75rem', overflow: 'hidden', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
      <div style={{ width: '100%', height: '120px', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '0.75rem 0.75rem 0 0' }} />
      <div style={{ padding: '0.75rem' }}>
        <SkeletonBar width="40%" />
        <SkeletonBar width="100%" />
        <SkeletonBar width="70%" />
        <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.75rem' }}>
          <div style={{ flex: 1, height: '24px', background: 'rgba(255,255,255,0.05)', borderRadius: '0.4rem', border: '1px solid rgba(148, 163, 184, 0.2)' }} />
          <div style={{ flex: 1, height: '24px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '0.4rem', border: '1px solid rgba(56, 189, 248, 0.2)' }} />
        </div>
      </div>
    </div>
  );

  const SkeletonSocialPosts = () => (
    <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
      {[1, 2, 3].map(i => <SkeletonSocialPost key={i} />)}
    </div>
  );

  const SkeletonInfluencer = () => (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.75rem', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <div style={{ width: '1.75rem', height: '1.75rem', borderRadius: '50%', background: 'linear-gradient(135deg, #4f46e5, #06b6d4)', animation: 'loading 1.5s infinite' }} />
        <div>
          <SkeletonBar width="70%" />
          <SkeletonBar width="50%" />
        </div>
      </div>
      <div style={{ width: '0.4rem', height: '0.4rem', borderRadius: '50%', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite' }} />
    </div>
  );

  const SkeletonInfluencers = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {[1, 2, 3].map(i => <SkeletonInfluencer key={i} />)}
      <div style={{ height: '32px', background: 'rgba(255,255,255,0.02)', borderRadius: '0.75rem', border: '1px dotted rgba(148, 163, 184, 0.3)', marginTop: '0.5rem' }} />
    </div>
  );

  const SkeletonExportOption = () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(148, 163, 184, 0.1)', borderRadius: '0.75rem' }}>
      <div style={{ width: '1rem', height: '1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
      <SkeletonBar width="80%" />
    </div>
  );

  const SkeletonExportOptions = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
      {[1, 2, 3, 4].map(i => <SkeletonExportOption key={i} />)}
    </div>
  );

  const SkeletonBlogPost = () => (
    <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1.25rem', borderRadius: '1rem', border: '1px solid rgba(148, 163, 184, 0.1)' }}>
      <SkeletonBar width="60%" />
      <SkeletonBar width="100%" />
      <SkeletonBar width="100%" />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
        <div style={{ height: '28px', width: '60px', background: 'rgba(255,255,255,0.05)', borderRadius: '0.4rem' }} />
        <div style={{ height: '28px', width: '80px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '0.4rem' }} />
      </div>
    </div>
  );

  const SkeletonMoodboardImage = () => (
    <div style={{ width: '100%', height: '80px', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '0.6rem', border: '1px solid rgba(148, 163, 184, 0.1)' }} />
  );

  const SkeletonMoodboard = () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
      {[1, 2, 3, 4].map(i => <SkeletonMoodboardImage key={i} />)}
    </div>
  );

  const SectionHeader = ({ title, icon: Icon }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
      {Icon && <Icon style={{ width: '1.1rem', height: '1.1rem', color: '#38bdf8' }} />}
      <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{title}</h3>
    </div>
  );

  if (loading) {
    return (
      <div style={{ padding: '1rem', maxWidth: '1200px', margin: '0 auto', color: '#f9fafb', position: 'relative' }}>
        {/* Header Bar Skeleton */}
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
                borderLeft: '4px solid #38bdf8',
                minHeight: '60px'
              }}>
                <SkeletonBar />
                <SkeletonBar width="70%" />
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingTop: '1.5rem' }}>
              <div style={{ height: '32px', width: '120px', background: 'rgba(255,255,255,0.05)', borderRadius: '0.5rem', border: '1px solid rgba(148, 163, 184, 0.2)' }} />
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: window.innerWidth < 640 ? '1fr' : window.innerWidth < 1024 ? 'repeat(6, 1fr)' : 'repeat(12, 1fr)', gap: '1rem' }}>
          {/* Campaign Overview Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 12', 
            background: 'rgba(15, 23, 42, 0.6)', 
            backdropFilter: 'blur(10px)', 
            borderRadius: '1.25rem', 
            padding: '1rem', 
            border: '1px solid rgba(148, 163, 184, 0.2)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonOverview />
          </div>

          {/* Social Media Content Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 6', 
            background: 'rgba(15, 23, 42, 0.6)', 
            borderRadius: '1.25rem', 
            padding: '1.5rem', 
            border: '1px solid rgba(148, 163, 184, 0.2)' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonSocialPosts />
          </div>

          {/* Influencer Outreach Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 3' : 'span 3', 
            background: 'rgba(15, 23, 42, 0.6)', 
            borderRadius: '1.25rem', 
            padding: '1.5rem', 
            border: '1px solid rgba(148, 163, 184, 0.2)' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonInfluencers />
          </div>

          {/* Export Options Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 3' : 'span 3', 
            background: 'rgba(15, 23, 42, 0.3)', 
            borderRadius: '1.25rem', 
            padding: '1.5rem', 
            border: '1px solid rgba(148, 163, 184, 0.1)' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonExportOptions />
          </div>

          {/* Blog Post Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 7', 
            background: 'rgba(15, 23, 42, 0.6)', 
            borderRadius: '1.25rem', 
            padding: '1.5rem', 
            border: '1px solid rgba(148, 163, 184, 0.2)' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonBlogPost />
          </div>

          {/* Moodboard Skeleton */}
          <div style={{ 
            gridColumn: window.innerWidth < 640 ? 'span 1' : window.innerWidth < 1024 ? 'span 6' : 'span 5', 
            background: 'rgba(15, 23, 42, 0.6)', 
            borderRadius: '1.25rem', 
            padding: '1.5rem', 
            border: '1px solid rgba(148, 163, 184, 0.2)' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.1)', paddingBottom: '0.5rem' }}>
              <div style={{ width: '1.1rem', height: '1.1rem', background: 'linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%)', backgroundSize: '200% 100%', animation: 'loading 1.5s infinite', borderRadius: '2px' }} />
              <SkeletonBar width="40%" />
            </div>
            <SkeletonMoodboard />
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
              <div style={{ flex: 1, height: '32px', background: 'rgba(255,255,255,0.05)', borderRadius: '0.5rem', border: '1px solid rgba(148, 163, 184, 0.2)' }} />
              <div style={{ flex: 1, height: '32px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '0.5rem', border: '1px solid rgba(56, 189, 248, 0.2)' }} />
            </div>
          </div>
        </div>
        
        <style>{`
          @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
          }
        `}</style>
      </div>
    );
  }

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
          {/* <button className="secondary-btn" style={{ gap: '0.5rem' }}>
            <RefreshCw style={{ width: '1rem', height: '1rem', paddingRight: '0.50rem' }} />
            Regenerate All
          </button> */}
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
          <SectionHeader title="Campaign Overview" icon={Layout} />
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
                    {post.type === 'tiktok' && <MessageSquare style={{ width: '0.9rem', height: '0.9rem', color: '#00f2ea' }} />}
                    {post.type === 'twitter' && <Twitter style={{ width: '0.9rem', height: '0.9rem', color: '#1da1f2' }} />}
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: 0, height: '2.5rem', overflow: 'hidden' }}>{post.caption}</p>
                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.75rem' }}>
                    <button style={{ flex: 1, padding: '0.35rem', borderRadius: '0.4rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(148, 163, 184, 0.2)', color: '#fff', fontSize: '0.65rem', cursor: 'pointer' }}>Edit</button>
                    <button 
                      onClick={() => handleShare(post)}
                      style={{ 
                        flex: 1, 
                        padding: '0.35rem', 
                        borderRadius: '0.4rem', 
                        background: 'rgba(56, 189, 248, 0.1)', 
                        border: '1px solid rgba(56, 189, 248, 0.2)',
                        color: '#38bdf8', 
                        fontSize: '0.65rem', 
                        cursor: 'pointer'
                      }}
                    >
                      Share
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