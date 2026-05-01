import React from 'react';

export default function LoadingCard() {
  return (
    <div className="card loading-card">
      <div className="spinner" />
      <p>Analyzing your document</p>
      <p className="loading-sub">
        AI extracting data · RAG retrieval · Generating explanation
      </p>
    </div>
  );
}
