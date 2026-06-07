import { useState } from 'react';
import './index.css';

function App() {
  const [source, setSource] = useState('aws');
  const [target, setTarget] = useState('azure');
  const [execMean, setExecMean] = useState(1200);
  const [memMean, setMemMean] = useState(150);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          target,
          exec_mean: parseFloat(execMean),
          mem_mean: parseFloat(memMean),
          runtime: 'python'
        })
      });

      if (!response.ok) throw new Error('API Request Failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>CloudPredict</h1>
      <p className="subtitle">AI-Powered Serverless Migration Forecaster</p>
      
      <div className="dashboard-card">
        <form onSubmit={handlePredict}>
          <div className="form-grid">
            <div className="form-group">
              <label>Source Platform</label>
              <select value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="aws">AWS Lambda</option>
                <option value="azure">Azure Functions</option>
                <option value="gcp">Google Cloud Functions</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Target Platform</label>
              <select value={target} onChange={(e) => setTarget(e.target.value)}>
                <option value="azure">Azure Functions</option>
                <option value="aws">AWS Lambda</option>
                <option value="gcp">Google Cloud Functions</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Execution Mean (ms)</label>
              <input type="number" value={execMean} onChange={(e) => setExecMean(e.target.value)} required />
            </div>
            
            <div className="form-group">
              <label>Memory Mean (MB)</label>
              <input type="number" value={memMean} onChange={(e) => setMemMean(e.target.value)} required />
            </div>
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Generate Forecast'}
          </button>
        </form>

        {error && <div style={{color: '#ff7b72', marginTop: '1rem', textAlign: 'center'}}>{error}</div>}

        {result && (
          <div className="results-section">
            <h3 style={{marginTop: 0}}>Migration Forecast: {source.toUpperCase()} → {target.toUpperCase()}</h3>
            <div className="metrics-grid">
              <div className="metric-box">
                <div className="metric-value">{result.latency_ms.toFixed(0)} ms</div>
                <div className="metric-label">Predicted Latency</div>
              </div>
              <div className="metric-box">
                <div className="metric-value">{result.p95_ms.toFixed(0)} ms</div>
                <div className="metric-label">95th Percentile</div>
              </div>
              <div className="metric-box">
                <div className="metric-value">${result.cost_usd.toFixed(6)}</div>
                <div className="metric-label">Cost per Invoke</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
