import ReactMarkdown from 'react-markdown'

function AnalysisOutput({ results, isLoading }) {
  if (isLoading && results.length === 0) {
    return (
      <div className="output-section">
        <h2>🔍 Analysis Results</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your photos with AI...</p>
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="output-section">
        <h2>🔍 Analysis Results</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
          Upload and analyze some photos to see results here.
        </p>
      </div>
    )
  }

  return (
    <div className="output-section">
      <h2>
        🔍 Analysis Results
        {isLoading && <span style={{ fontSize: '0.8em', marginLeft: '1rem' }}>(analyzing more...)</span>}
      </h2>
      <div className="analysis-results">
        {results.map((result, index) => (
          <div key={index} className="analysis-item">
            <img
              src={result.photo.storage_url}
              alt={result.photo.original_filename}
              className="analysis-image"
            />
            <div className="analysis-content">
              <h3>{result.photo.original_filename}</h3>

              {result.analysis.location_info && (
                <>
                  <h4>📍 Location</h4>
                  <div className="markdown-content">
                    <ReactMarkdown>{result.analysis.location_info}</ReactMarkdown>
                  </div>
                </>
              )}

              {result.analysis.historical_context && (
                <>
                  <h4>📚 Historical & Cultural Context</h4>
                  <div className="markdown-content">
                    <ReactMarkdown>{result.analysis.historical_context}</ReactMarkdown>
                  </div>
                </>
              )}

              {result.analysis.user_context && (
                <p style={{ marginTop: '1rem', fontStyle: 'italic', color: 'var(--text-muted)' }}>
                  Your context: "{result.analysis.user_context}"
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AnalysisOutput
