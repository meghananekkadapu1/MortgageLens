import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultPanel from './components/ResultPanel';
import LoadingCard from './components/LoadingCard';

const API_BASE = process.env.REACT_APP_API_URL || '';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleUpload(file) {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const body = new FormData();
      body.append('file', file);
      const res = await fetch(`${API_BASE}/explain/upload`, { method: 'POST', body });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Server error (HTTP ${res.status})`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function reset() { setResult(null); setError(null); }

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <span className="logo-icon">🏡</span>
        <div>
          <h1>Mortgage Lens 🔍</h1>
          <p>Upload your mortgage or escrow statement · Mortgage Lens will Analyze &amp; explains your payment change</p>
        </div>
      </header>

      <main className="app-main">
        {error && <div className="error-box"><strong>⚠️ Error: </strong>{error}</div>}
        {!result && !loading && <UploadForm onUpload={handleUpload} />}
        {loading && <LoadingCard />}
        {result && !loading && <ResultPanel result={result} onReset={reset} />}
      </main>
    </div>
  );
}
