import React, { useState } from 'react'
import axios from 'axios'
import './styles.css'
import Logo from './assets/citibank-logo.svg'

export default function App() {
  const [q, setQ] = useState('')
  const [resp, setResp] = useState(null)
  const [ingestUrl, setIngestUrl] = useState('')
  const [ingestStatus, setIngestStatus] = useState(null)

  async function submit() {
    if (!q) return;
    setResp({ answer: '', sources: [] });
    try {
      // Use fetch for streaming support
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 4 })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep the last incomplete line in buffer

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const part = JSON.parse(line);
            if (part.type === 'sources') {
              setResp(prev => ({ ...prev, sources: part.data }));
            } else if (part.type === 'chunk') {
              setResp(prev => ({ ...prev, answer: prev.answer + part.data }));
            }
          } catch (e) {
            console.error('Error parsing stream line:', line, e);
          }
        }
      }
    } catch (err) {
      setResp({ answer: `Error: ${err.message}`, sources: [] });
    }
  }

  async function doIngest() {
    if (!ingestUrl) return setIngestStatus('Please enter a URL')
    setIngestStatus('Ingesting from URL...')
    try {
      const r = await axios.post('/api/ingest', { url: ingestUrl })
      setIngestStatus(`Success: Ingested ${r.data.ingested_chunks} chunks`)
      await refreshDocs()
    } catch (err) {
      setIngestStatus(`Error: ${err?.response?.data?.detail || err.message || err}`)
    }
  }

  async function uploadFile(e) {
    const f = e.target.files?.[0]
    if (!f) return
    const fd = new FormData(); fd.append('file', f, f.name)
    setIngestStatus('Uploading file to server...')
    try {
      console.log('Sending upload request for:', f.name)
      const r = await axios.post('/api/ingest/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      console.log('Upload response:', r.data)
      setIngestStatus(`Success: Ingested ${r.data.ingested_chunks} chunks from ${f.name}`)
      // Force a small delay to allow Chroma to sync if needed
      setTimeout(() => refreshDocs(), 500);
    } catch (err) {
      console.error('Upload failed:', err)
      const msg = err?.response?.data?.detail || err.message || 'Unknown error'
      setIngestStatus(`Error: ${msg}`)
    }
  }

  async function refreshDocs() {
    try {
      console.log('Refreshing document list...')
      const r = await axios.get('/api/docs')
      console.log('Docs received:', r.data.docs)
      setDocs(r.data.docs || [])
    } catch (e) {
      console.error('Failed to refresh docs:', e)
      setDocs([])
    }
  }

  async function resetDb() {
    if (!window.confirm("Are you sure you want to clear all data? This cannot be undone.")) return;
    setIngestStatus('Clearing database...');
    try {
      const r = await axios.post('/api/reset');
      setIngestStatus('Database cleared successfully');
      await refreshDocs();
    } catch (err) {
      setIngestStatus(`Error clearing database: ${err.message}`);
    }
  }

  function formatSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  React.useEffect(() => { refreshDocs() }, [])
  const [docs, setDocs] = React.useState([])

  return (
    <div className="app-root">
      <header className="app-header">
        <img src={Logo} alt="Citibank" className="brand-logo" />
        <h1 className="brand-title">Citibank — Usecase Explorer</h1>
      </header>

      <main className="app-main">
        <div className="query-panel">
          <input className="query-input" value={q} onChange={e => setQ(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && submit()}
            placeholder="Ask something about the usecases..." />
          <button className="btn-primary" onClick={submit}>Ask</button>
        </div>

        <div className="ingest-section" style={{ marginTop: 20, padding: 15, border: '1px solid #eee', borderRadius: 8, background: '#fff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 }}>
            <h4 style={{ margin: 0 }}>Document Management</h4>
            <button onClick={resetDb} className="btn-secondary" style={{ backgroundColor: '#fee2e2', color: '#dc2626', border: '1px solid #fecaca', padding: '4px 12px', fontSize: 12 }}>Clear Database</button>
          </div>

          <div style={{ display: 'flex', gap: 10, marginBottom: 15 }}>
            <input style={{ flex: 1, padding: 8, border: '1px solid #ddd', borderRadius: 4 }}
              value={ingestUrl} onChange={e => setIngestUrl(e.target.value)}
              placeholder="Ingest from PDF URL (https://...)" />
            <button onClick={doIngest} className="btn-primary" style={{ padding: '8px 16px' }}>Ingest URL</button>
          </div>

          <div style={{ marginBottom: 15 }}>
            <label style={{ display: 'block', marginBottom: 5, fontSize: 14, fontWeight: 'bold' }}>Upload Local PDF</label>
            <input type="file" accept="application/pdf" onChange={uploadFile}
              style={{ display: 'block', fontSize: 13 }} />
          </div>

          {ingestStatus && <div style={{ padding: 8, backgroundColor: '#f9fafb', borderLeft: '4px solid var(--citi-blue)', fontSize: 13, color: '#374151', marginBottom: 15 }}>{ingestStatus}</div>}

          <div className="ingested-list">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <h5 style={{ margin: 0 }}>Ingested Documents</h5>
              <button onClick={refreshDocs} className="btn-secondary" style={{ fontSize: 12, padding: '2px 8px' }}>Refresh List</button>
            </div>
            <ul style={{ maxHeight: 150, overflowY: 'auto', paddingLeft: 20, margin: 0, fontSize: 13 }}>
              {docs.length === 0 && <li style={{ color: '#6b7280', listStyle: 'none', marginLeft: -20 }}>No documents ingested</li>}
              {docs.map(d => <li key={d.source} style={{ marginBottom: 8 }}>
                <div style={{ fontWeight: 'bold' }}>{d.source}</div>
                <div style={{ color: '#666', fontSize: 11 }}>
                  {d.count} chunks {d.size ? `• ${formatSize(d.size)}` : ''} {d.timestamp ? `• ${new Date(d.timestamp).toLocaleString()}` : ''}
                </div>
              </li>)}
            </ul>
          </div>
        </div>

        {resp && (resp.answer || resp.sources?.length > 0) && (
          <section className="results" style={{ marginTop: 24 }}>
            <h2 style={{ fontSize: 18, borderBottom: '1px solid #eee', paddingBottom: 8 }}>AI Assistant Response</h2>
            <div className="answer-box" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {resp.answer || <span style={{ color: '#999' }}>Generating answer...</span>}
            </div>

            {resp.sources?.length > 0 && (
              <div style={{ marginTop: 20 }}>
                <h3 style={{ fontSize: 16, color: '#444' }}>Sources</h3>
                <div className="sources-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {resp.sources.map((s, idx) => (
                    <div key={idx} style={{ padding: 10, backgroundColor: '#f8fbff', border: '1px solid #e1e8f5', borderRadius: 6, fontSize: 12 }}>
                      <div style={{ fontWeight: 'bold', color: 'var(--citi-blue)', marginBottom: 4 }}>Source {idx + 1}</div>
                      <div style={{ color: '#555', height: 60, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 4, WebkitBoxOrient: 'vertical' }}>
                        {s.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="app-footer">Local demo — non-commercial use only</footer>
    </div>
  )
}
