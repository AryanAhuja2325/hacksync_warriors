import { useState } from 'react'
import { Clock, Plus, Search, Sparkles } from 'lucide-react'
import Navbar from './components/Navbar'
import CompetitorInsights from './components/CompetitorInsights'
import CampaignCanvas from './components/CampaignCanvas'
import './App.css' 

function App() {
  const [currentView, setCurrentView] = useState('start')
  const [prompt, setPrompt] = useState('')
  const [attachedPdf, setAttachedPdf] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [uploadedUrl, setUploadedUrl] = useState(null)
  const [insightsTab, setInsightsTab] = useState('overview')

  const uploadPdf = async (file) => {
    setUploading(true)
    setUploadError(null)
    setUploadedUrl(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://localhost:5000/files/upload', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `Upload failed: ${res.status}`)
      }

      const data = await res.json()
      setUploadedUrl(data.url)
      console.log('Uploaded PDF URL:', data.url)
      setAttachedPdf(file)
    } catch (err) {
      console.error('PDF upload error:', err)
      setUploadError(err.message || 'Upload failed')
      setAttachedPdf(null)
    } finally {
      setUploading(false)
    }
  }

  const handlePdfChange = (event) => {
    const file = event.target.files?.[0]
    if (!file) {
      setAttachedPdf(null)
      setUploadedUrl(null)
      setUploadError(null)
      return
    }
    if (file.type !== 'application/pdf') {
      setUploadError('Please select a PDF file')
      setAttachedPdf(null)
      return
    }
    uploadPdf(file)
  }

  return (
    <div className="app-root">
      <Navbar currentView={currentView} onViewChange={setCurrentView} />
      
      <div className="starfield" aria-hidden="true" />
      <div className="snow" aria-hidden="true" />

      <aside className="left-panel">
        <div className="history-panel">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Recent Projects
            </span>
            <button style={{ all: 'unset', cursor: 'pointer', color: '#38bdf8' }}>
              <Plus style={{ width: '1.1rem', height: '1.1rem' }} />
            </button>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div 
              className={currentView === 'start' ? "nav-item nav-item-active" : "nav-item"} 
              style={{ borderRadius: '0.75rem', padding: '0.6rem 0.8rem', cursor: 'pointer' }}
              onClick={() => setCurrentView('start')}
            >
              <Sparkles style={{ width: '1rem', height: '1rem' }} />
              <span style={{ fontSize: '0.85rem' }}>New Campaign</span>
            </div>
            
            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {[
                'Market Analysis Q1',
                'Brand Identity Revamp',
                'Social Media Concept',
                'Product Launch Deck'
              ].map((item, i) => (
                <div key={i} className="nav-item" style={{ borderRadius: '0.75rem', padding: '0.6rem 0.8rem', color: '#9ca3af' }}>
                  <Clock style={{ width: '0.9rem', height: '0.9rem', opacity: 0.6 }} />
                  <span style={{ fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item}
                  </span>
                </div>
              ))}
            </div>

            <p style={{ color: '#475569', fontSize: '0.75rem', textAlign: 'center', marginTop: '2.5rem', fontStyle: 'italic' }}>
              End of history
            </p>
          </div>
        </div>
      </aside>

      <main className="main" style={{ flex: 1, overflowY: 'auto' }}>
        {currentView === 'start' ? (
          <>
            <header className="hero">
              <p className="hero-kicker">Build</p>
              <h1 className="hero-title">Build your ideas with AI</h1>
              <p className="hero-subtitle">
                Describe what you want to build and we&apos;ll help you turn it into
                prompts, APIs, and code.
              </p>
            </header>

            <section className="prompt-shell" aria-label="AI prompt input">
              <div className="prompt-input-row">
                <input
                  className="prompt-input"
                  placeholder="Describe your idea"
                  autoComplete="off"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>

              <div className="prompt-toolbar">
                <div className="model-pill">
                  <span className="model-label">Model</span>
                  <span className="model-name">HackSync GPT Preview</span>
                </div>
                <div className="prompt-actions">
                  <label className="secondary-btn attach-btn">
                    {uploading ? 'Uploading…' : 'Attach PDF'}
                    <input
                      type="file"
                      accept="application/pdf"
                      onChange={handlePdfChange}
                    />
                  </label>
                  <button 
                    className="primary-btn" 
                    disabled={uploading}
                    onClick={() => setCurrentView('canvas')}
                  >
                    Build →
                  </button>  
                </div>
              </div>

              {(attachedPdf || uploading || uploadedUrl || uploadError) && (
                <div className="attachment-pill" aria-label="Attached PDF">
                  {uploading ? (
                    <span className="attachment-status">Uploading…</span>
                  ) : uploadError ? (
                    <span style={{ color: 'red' }}>{uploadError}</span>
                  ) : (
                    <>
                      <span className="attachment-label">PDF attached</span>
                      <span className="attachment-name">{attachedPdf?.name}</span>
                      {uploadedUrl && (
                        <span className="attachment-link" style={{ marginLeft: '10px' }}>
                          <a href={uploadedUrl} target="_blank" rel="noreferrer" style={{ color: '#38bdf8' }}>View</a>
                        </span>
                      )}
                    </>
                  )}
                </div>
              )}
            </section>
          </>
        ) : currentView === 'canvas' ? (
          <CampaignCanvas prompt={prompt} />
        ) : currentView === 'analytics' ? (
          <CompetitorInsights activeTab={insightsTab} onTabChange={setInsightsTab} />
        ) : (
          <CompetitorInsights activeTab={insightsTab} onTabChange={setInsightsTab} />
        )} 
      </main>
    </div>
  )
}

export default App