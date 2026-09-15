import { useState } from 'react';
import { Cloud, Zap, DollarSign, Activity, Server, LayoutDashboard, Loader2 } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import './index.css';

function App() {
  const [source, setSource] = useState('aws');
  const [target, setTarget] = useState('azure');
  const [execMean, setExecMean] = useState(1200);
  const [memMean, setMemMean] = useState(256);
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

  const chartData = result ? [
    {
      name: 'Mean Latency (ms)',
      Source: parseFloat(execMean),
      Target: result.latency_ms
    },
    {
      name: '95th Percentile (ms)',
      Source: parseFloat(execMean) * 1.2, // synthetic p95 for source visualization
      Target: result.p95_ms
    }
  ] : [];

  return (
    <div className="app-wrapper">
      <header className="header">
        <h1>CloudPredict</h1>
        <p>AI-Powered Serverless Migration Forecaster</p>
      </header>
      
      <div className="dashboard-grid">
        
        {/* Left Column: Form */}
        <div className="glass-card form-section">
          <div className="results-header" style={{marginBottom: '1rem'}}>
            <LayoutDashboard size={24} className="accent-icon" color="#06b6d4" />
            <h2 style={{fontSize: '1.2rem'}}>Simulation Params</h2>
          </div>
          
          <form onSubmit={handlePredict} className="form-section">
            <div className="form-group">
              <label>Source Platform</label>
              <div className="input-wrapper">
                <Cloud size={18} className="input-icon" />
                <select value={source} onChange={(e) => setSource(e.target.value)}>
                  <option value="aws">AWS Lambda</option>
                  <option value="azure">Azure Functions</option>
                  <option value="gcp">Google Cloud Functions</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label>Target Platform</label>
              <div className="input-wrapper">
                <Server size={18} className="input-icon" />
                <select value={target} onChange={(e) => setTarget(e.target.value)}>
                  <option value="azure">Azure Functions</option>
                  <option value="aws">AWS Lambda</option>
                  <option value="gcp">Google Cloud Functions</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label>Current Latency (ms)</label>
              <div className="input-wrapper">
                <Activity size={18} className="input-icon" />
                <input 
                  type="number" 
                  value={execMean} 
                  onChange={(e) => setExecMean(e.target.value)} 
                  required 
                  min="1"
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Memory Configuration (MB)</label>
              <div className="input-wrapper">
                <Zap size={18} className="input-icon" />
                <input 
                  type="number" 
                  value={memMean} 
                  onChange={(e) => setMemMean(e.target.value)} 
                  required 
                  min="128"
                  step="128"
                />
              </div>
            </div>
            
            <button type="submit" className="btn-submit" disabled={loading || source === target}>
              {loading ? (
                <><Loader2 size={20} className="spinner" /> Analyzing Model...</>
              ) : (
                source === target ? 'Select Different Target' : 'Generate Forecast'
              )}
            </button>
          </form>

          {error && <div style={{color: '#ff7b72', marginTop: '1rem', textAlign: 'center'}}>{error}</div>}
        </div>

        {/* Right Column: Dashboard & Charts */}
        <div className="glass-card">
          <div className="results-header">
            <Activity size={28} color="#8b5cf6" />
            <h2>Migration Forecast: {source.toUpperCase()} → {target.toUpperCase()}</h2>
          </div>

          {!result && !loading && (
            <div className="empty-state">
              <Cloud size={48} opacity={0.2} />
              <p>Configure parameters and run the forecast to see predictions.</p>
            </div>
          )}

          {result && (
            <>
              <div className="metrics-row">
                <div className="metric-card">
                  <div className="icon-wrapper">
                    <Zap size={24} />
                  </div>
                  <div className="metric-value">{result.latency_ms.toFixed(0)}</div>
                  <div className="metric-label">Predicted Latency (ms)</div>
                </div>
                
                <div className="metric-card">
                  <div className="icon-wrapper">
                    <Activity size={24} color="#8b5cf6" />
                  </div>
                  <div className="metric-value">{result.p95_ms.toFixed(0)}</div>
                  <div className="metric-label">95th Percentile (ms)</div>
                </div>
                
                <div className="metric-card">
                  <div className="icon-wrapper">
                    <DollarSign size={24} color="#10b981" />
                  </div>
                  <div className="metric-value">${result.cost_usd.toFixed(6)}</div>
                  <div className="metric-label">Cost per Invoke</div>
                </div>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" tick={{fill: '#94a3b8'}} />
                    <YAxis stroke="#94a3b8" tick={{fill: '#94a3b8'}} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#151a2a', border: '1px solid #30363d', borderRadius: '8px' }}
                      itemStyle={{ color: '#e2e8f0' }}
                    />
                    <Legend wrapperStyle={{ paddingTop: '20px' }} />
                    <Bar dataKey="Source" fill="#8b5cf6" radius={[4, 4, 0, 0]} name={`${source.toUpperCase()} (Current)`} />
                    <Bar dataKey="Target" fill="#06b6d4" radius={[4, 4, 0, 0]} name={`${target.toUpperCase()} (Predicted)`} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
