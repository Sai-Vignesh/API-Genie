import { useState } from "react";
import axios from "axios";
import "./App.css";

export default function App() {
  const [nlQuery, setNlQuery] = useState("");
  const [rows, setRows] = useState<any[]>([]);
  const [sql, setSql] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const askAgent = async () => {
    if (!nlQuery.trim()) return;
    setLoading(true);
    setError("");
    setSql("");
    setRows([]);
    try {
      const { data } = await axios.post("http://localhost:8000/query", {
        query: nlQuery,
      });
      if (data.error) {
        setError(data.error);
      } else {
        setSql(data.sql);
        setRows(data.results || []);
      }
    } catch (e) {
      setError("Agent request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>API Genie 🧞‍♂️</h1>
      
      <div className="search-card">
        <div className="search-input-group">
          <input 
            value={nlQuery} 
            onChange={e=>setNlQuery(e.target.value)} 
            onKeyDown={e => e.key === 'Enter' && askAgent()}
            placeholder="Ask anything (e.g., Show me free weather APIs)..." 
          />
          <button onClick={askAgent} disabled={loading}>
            {loading ? <><span className="loading-spinner"></span>Thinking...</> : "Ask Agent"}
          </button>
        </div>

        {error && <div className="error-msg">{error}</div>}

        {sql && (
          <div className="sql-box">
            <div style={{ fontSize: '0.8rem', color: '#888', marginBottom: '4px' }}>GENERATED SQL</div>
            <pre>{sql}</pre>
          </div>
        )}
      </div>

      {rows.length > 0 && (
        <div className="search-card" style={{ marginTop: 0 }}>
          <table className="results-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Auth</th>
                <th>HTTPS</th>
                <th>CORS</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.api_id || i}>
                  <td><strong>{r.api_name}</strong></td>
                  <td>{r.category || r.category_name}</td>
                  <td><span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    background: 'rgba(255,255,255,0.1)',
                    fontSize: '0.9em'
                  }}>{r.auth_type}</span></td>
                  <td>{r.https_supported ? "✅" : "❌"}</td>
                  <td>{r.cors_supported ? "✅" : "❌"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {rows.length === 0 && !loading && !error && sql && (
        <div style={{ color: "#888", marginTop: "1rem" }}>No results found for your query.</div>
      )}
    </div>
  );
}
