import React, { useState } from 'react';

const ICONS = {
  'Property tax increase': '🏛️',
  'Insurance premium increase': '🛡️',
  'Escrow shortage': '💸',
  'Escrow adjustment': '⚖️',
  'No increase detected': '✅',
};

const usd = (n) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 2,
  }).format(n);

function ExtractedData({ data }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button className="extracted-toggle" onClick={() => setOpen(o => !o)}>
        <span>🔢 Numbers extracted from your document</span>
        <span>{open ? '▲ hide' : '▼ show'}</span>
      </button>
      {open && (
        <div className="extracted-grid">
          <Row label="Previous monthly payment" value={usd(data.previous_payment)} />
          <Row label="Current monthly payment" value={usd(data.current_payment)} highlight />
          <Row label="Previous annual property tax" value={usd(data.previous_annual_tax)} />
          <Row label="Current annual property tax" value={usd(data.current_annual_tax)} />
          <Row label="Previous annual insurance" value={usd(data.previous_annual_insurance)} />
          <Row label="Current annual insurance" value={usd(data.current_annual_insurance)} />
          <Row label="Escrow account balance" value={usd(data.escrow_balance)} />
          {data.extraction_notes && (
            <div className="extraction-note">📝 {data.extraction_notes}</div>
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value, highlight }) {
  return (
    <div className={`extracted-row${highlight ? ' highlight' : ''}`}>
      <span>{label}</span><strong>{value}</strong>
    </div>
  );
}

export default function ResultPanel({ result, onReset }) {
  const {
    increase_detected, primary_reason, secondary_factors,
    monthly_increase_amount, explanation, recommendations,
    confidence, sources, extracted_data, metrics,
  } = result;

  return (
    <div>
      {/* Banner */}
      <div className={`result-banner ${increase_detected ? 'increase' : 'no-increase'}`}>
        <span className="banner-icon">{increase_detected ? '⚠️' : '✅'}</span>
        <div style={{ flex: 1 }}>
          <div className="banner-amount">
            {increase_detected ? `+${usd(monthly_increase_amount)}/mo` : 'No Increase Detected'}
          </div>
          <div className="banner-label">
            {increase_detected ? 'Your monthly payment went up' : 'Your payment appears unchanged'}
          </div>
        </div>
        <span className={`badge ${confidence}`}>{confidence} confidence</span>
      </div>

      {/* Extracted data */}
      {extracted_data && (
        <div className="card">
          <div className="card-title">📋 What MortgageLens Analyzed From Your Document</div>
          <ExtractedData data={extracted_data} />
        </div>
      )}

      {/* Causes */}
      {increase_detected && (
        <div className="card">
          <div className="card-title">🔎 Why Your Payment Increased</div>
          <div className="reasons-grid">
            <div className="reason-chip primary">
              <span style={{ fontSize: '1.4rem' }}>{ICONS[primary_reason] || '📌'}</span>
              <div>
                <div className="chip-label">Primary Cause</div>
                <div>{primary_reason}</div>
              </div>
            </div>
            {secondary_factors.map(f => (
              <div key={f} className="reason-chip secondary">
                <span style={{ fontSize: '1.4rem' }}>{ICONS[f] || '📌'}</span>
                <div>
                  <div className="chip-label">Also Contributing</div>
                  <div>{f}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      <div className="card">
        <div className="card-title">💬 Detailed Explanation</div>
        <div className="explanation-box">{explanation}</div>
        <div className="section-label" style={{ marginTop: 4 }}>Knowledge sources used</div>
        <div className="sources-list">
          {sources.map(s => <span key={s} className="source-tag">📄 {s}</span>)}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations?.length > 0 && (
        <div className="card">
          <div className="card-title">💡 What You Can Do</div>
          <ul className="recs-list">
            {recommendations.map((r, i) => (
              <li key={i}><span className="rec-num">{i + 1}</span><span>{r}</span></li>
            ))}
          </ul>
        </div>
      )}

      {/* Metrics */}
      {metrics && (
        <div className="card">
          <div className="card-title">📊 Response Quality Metrics</div>
          <div className="metrics-row">
            <div className="metric-box">
              <div className="metric-value">{Math.round((metrics.grounding_score ?? 0) * 100)}%</div>
              <div className="metric-label">Grounding Score</div>
            </div>
            <div className="metric-box">
              <div className="metric-value">{Math.round((1 - (metrics.hallucination_score ?? 0)) * 100)}%</div>
              <div className="metric-label">Factual Reliability</div>
            </div>
            <div className="metric-box">
              <div className="metric-value">{metrics.context_chunks_used ?? 0}</div>
              <div className="metric-label">KB Sources Used</div>
            </div>
          </div>
        </div>
      )}

      <div style={{ textAlign: 'center', marginTop: 4 }}>
        <button className="btn-primary" onClick={onReset}>← Analyze Another Statement</button>
      </div>
    </div>
  );
}
