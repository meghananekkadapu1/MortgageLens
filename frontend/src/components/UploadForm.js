import React, { useCallback, useRef, useState } from 'react';

const VALID_EXT = /\.(pdf|png|jpg|jpeg)$/i;
const VALID_TYPES = ['application/pdf', 'image/png', 'image/jpeg'];

export default function UploadForm({ onUpload }) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const inputRef = useRef(null);

  const pickFile = useCallback((f) => {
    if (!f) return;
    if (!VALID_EXT.test(f.name) && !VALID_TYPES.includes(f.type)) {
      alert('Please upload a PDF, PNG, or JPEG file.');
      return;
    }
    setFile(f);
  }, []);

  const onDrop = (e) => { e.preventDefault(); setDragging(false); pickFile(e.dataTransfer.files[0]); };
  const onDragOver = (e) => { e.preventDefault(); setDragging(true); };
  const onDragLeave = () => setDragging(false);

  function submit(e) { e.preventDefault(); if (file) onUpload(file); }

  return (
    <>
      {/* How it works */}
      <div className="card">
        <div className="card-title">⚡ How It Works</div>
        <div className="how-it-works">
          <div className="step">
            <div className="step-num">1</div>
            <div>
              <strong>Upload your statement</strong>
              <p>Drop your escrow analysis or mortgage payment-change letter (PDF or image)</p>
            </div>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-num">2</div>
            <div>
              <strong>AI analyze the document</strong>
              <p>Vision model extracts all payment, tax, insurance &amp; escrow figures</p>
            </div>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-num">3</div>
            <div>
              <strong>Get a clear explanation</strong>
              <p>Get detailed explanation on why your payment changed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upload */}
      <div className="card">
        <div className="card-title">📄 Upload Your Document</div>
        <form onSubmit={submit}>
          <div
            className={`drop-zone${dragging ? ' dragging' : ''}${file ? ' has-file' : ''}`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={() => !file && inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && !file && inputRef.current?.click()}
          >
            <input
              ref={inputRef} type="file" accept=".pdf,.png,.jpg,.jpeg"
              style={{ display: 'none' }}
              onChange={e => pickFile(e.target.files[0])}
            />
            {!file ? (
              <div className="drop-zone-inner">
                <div className="drop-icon">📑</div>
                <div className="drop-title">Drop your document here</div>
                <div className="drop-sub">or click to browse files</div>
                <div className="drop-types">PDF &nbsp;·&nbsp; PNG &nbsp;·&nbsp; JPEG &nbsp;·&nbsp; max 20 MB</div>
              </div>
            ) : (
              <div className="file-selected">
                <span className="file-icon">{/\.pdf$/i.test(file.name) ? '📕' : '🖼️'}</span>
                <div>
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">{(file.size / 1024).toFixed(0)} KB</div>
                </div>
                <button type="button" className="file-remove" title="Remove"
                  onClick={e => { e.stopPropagation(); setFile(null); }}>✕</button>
              </div>
            )}
          </div>

          <div className="what-works">
            <strong>Accepted documents:</strong> Monthly Mortgage
            Account Statement, Annual Escrow Analysis Statement, Payment Change Notice, or any lender letter showing your
            previous vs. new payment with tax and insurance breakdowns.
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={!file}>
              🔍 Analyze Statement
            </button>
            {file && (
              <button type="button" className="btn-secondary" onClick={() => setFile(null)}>
                Clear
              </button>
            )}
          </div>
        </form>
      </div>
    </>
  );
}
