import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useAuth } from './AuthContext'
import LoginRegister from './LoginRegister'
import './index.css'

function App() {
  const { token, logout } = useAuth()
  const [article, setArticle] = useState('')
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('report') // 'report', 'variants', 'claims'

  const handleAnalyze = async () => {
    if (!article.trim()) {
      setError('Please enter an article to analyze.')
      return
    }
    setError('')
    setLoading(true)
    setAnalysisData(null)

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ article }),
      })

      if (response.status === 401) {
        logout()
        throw new Error('Session expired, please login again')
      }

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || 'Failed to analyze article')
      }

      const data = await response.json()
      setAnalysisData(data)
      setActiveTab('report')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Helper to format claim for rendering in UI
  const formatClaim = (claimObj) => {
    if (!claimObj) return "";
    return (
      <span style={{ lineHeight: '1.4' }}>
        <strong style={{ color: '#93c5fd' }}>{claimObj.subject}</strong> {claimObj.predicate} <strong style={{ color: '#fca5a5' }}>{claimObj.object}</strong>
      </span>
    );
  }

  if (!token) {
    return <LoginRegister />
  }

  return (
    <>
      <div style={{ position: 'absolute', top: '20px', right: '20px' }}>
        <button onClick={logout} style={{ fontSize: '0.85em', padding: '0.5em 1em', width: 'auto', marginTop: 0 }}>Log Out</button>
      </div>
      <h1>News Stability Analyzer</h1>
      <p className="description">
        Paste a news article below. This tool generates variations of the text and extracts factual claims
        to identify which parts of the story are robust (Stable) against manipulation, and which parts
        easily change (Drift Prone).
      </p>

      <div className="glass-panel">
        <textarea
          placeholder="Paste news article here..."
          value={article}
          onChange={(e) => setArticle(e.target.value)}
          disabled={loading}
        />

        {error && <div style={{ color: '#ef4444', marginTop: '1rem' }}>{error}</div>}

        <button onClick={handleAnalyze} disabled={loading || !article.trim()}>
          {loading ? (
            <>
              <span className="loading-spinner"></span>
              Generating Variants & Analyzing...
            </>
          ) : (
            'Analyze Article'
          )}
        </button>
      </div>

      {analysisData && (
        <div className="glass-panel report-container" style={{ maxWidth: '1000px' }}>

          <div className="tabs-container">
            <button
              className={`tab-button ${activeTab === 'report' ? 'active' : ''}`}
              onClick={() => setActiveTab('report')}
            >
              Stability Report
            </button>
            <button
              className={`tab-button ${activeTab === 'variants' ? 'active' : ''}`}
              onClick={() => setActiveTab('variants')}
            >
              Generated Variants ({analysisData.variants?.length || 0})
            </button>
            <button
              className={`tab-button ${activeTab === 'claims' ? 'active' : ''}`}
              onClick={() => setActiveTab('claims')}
            >
              Extracted Claims
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'report' && (
              <div>
                <div style={{ marginBottom: '2rem', padding: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', borderLeft: '3px solid #f87171' }}>
                  <h3 style={{ marginTop: 0, color: '#f87171' }}>How to read this report:</h3>
                  <ul style={{ color: '#d1d5db', paddingLeft: '1.2rem', margin: 0 }}>
                    <li style={{ marginBottom: '0.5rem', border: 'none', background: 'transparent', padding: 0 }}><strong>Stable (Green):</strong> Core facts that the AI consistently preserved across every single rewrite. These are highly reliable.</li>
                    <li style={{ marginBottom: '0.5rem', border: 'none', background: 'transparent', padding: 0 }}><strong>Style-Sensitive (Yellow):</strong> Facts that survived, but the LLM significantly altered their wording, framing, or sentiment.</li>
                    <li style={{ border: 'none', background: 'transparent', padding: 0 }}><strong>Drift Prone (Red):</strong> Specific details, numbers, or nuance that the AI completely dropped or severely altered. These are vulnerable to manipulation.</li>
                  </ul>
                </div>

                {analysisData.comparison && (
                  <>
                    {/* Stable Claims */}
                    {analysisData.comparison.filter(c => c.drift_category === 'stable').length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h2 style={{ color: '#4ade80', borderBottom: '1px solid rgba(74, 222, 128, 0.2)', paddingBottom: '0.5rem' }}>Stable Claims</h2>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                          {analysisData.comparison.filter(c => c.drift_category === 'stable').map((claim, idx) => (
                            <li key={idx} className="category-stable" style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '6px', borderLeft: '3px solid #4ade80', marginBottom: '0.8rem' }}>
                              {formatClaim(claim.example_claim)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Style-Sensitive Claims */}
                    {analysisData.comparison.filter(c => c.drift_category === 'style_sensitive').length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h2 style={{ color: '#facc15', borderBottom: '1px solid rgba(250, 204, 21, 0.2)', paddingBottom: '0.5rem' }}>Style-Sensitive Claims</h2>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                          {analysisData.comparison.filter(c => c.drift_category === 'style_sensitive').map((claim, idx) => (
                            <li key={idx} className="category-style" style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '6px', borderLeft: '3px solid #facc15', marginBottom: '0.8rem' }}>
                              {formatClaim(claim.example_claim)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Drift Prone Claims */}
                    {analysisData.comparison.filter(c => c.drift_category === 'drift_prone').length > 0 && (
                      <div style={{ marginBottom: '2rem' }}>
                        <h2 style={{ color: '#f87171', borderBottom: '1px solid rgba(248, 113, 113, 0.2)', paddingBottom: '0.5rem' }}>Drift Prone Claims</h2>
                        <ul style={{ listStyle: 'none', padding: 0 }}>
                          {analysisData.comparison.filter(c => c.drift_category === 'drift_prone').map((claim, idx) => (
                            <li key={idx} className="category-drift" style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '6px', borderLeft: '3px solid #f87171', marginBottom: '0.8rem' }}>
                              {formatClaim(claim.example_claim)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {activeTab === 'variants' && (
              <div>
                <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
                  The Gemini AI generated these distinct stylistic variations of your article to test its informational stability.
                </p>
                {analysisData.variants?.map((v, i) => (
                  <div key={i} className="variant-box">
                    <h3>Variant {i + 1}: {v.style || "Standard"}</h3>
                    <p style={{ whiteSpace: 'pre-wrap' }}>{typeof v === 'string' ? v : v.text}</p>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'claims' && (
              <div>
                <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
                  Before comparing, the AI broke down each variant into atomic factual claims.
                  By breaking paragraphs into simple sentences, our Sentence-Transformer model can measure exact semantic similarity.
                </p>
                {analysisData.claims?.map((variantClaims, idx) => (
                  <div key={idx} className="variant-box">
                    <h3>Claims from Variant {idx + 1}</h3>
                    <div className="claims-list">
                      {variantClaims.map((claim, cIdx) => (
                        <div key={cIdx} className="claim-card">
                          <p style={{ fontSize: '1.1em', margin: '0 0 10px 0', lineHeight: '1.4' }}>
                            <strong style={{ color: '#93c5fd' }}>{claim.subject}</strong> {claim.predicate} <strong style={{ color: '#fca5a5' }}>{claim.object}</strong>
                          </p>
                          <div style={{ fontSize: '0.85em', color: '#94a3b8' }}>
                            <span><strong style={{ color: '#4ade80' }}>✓</strong> AI Confidence: {(claim.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

export default App
