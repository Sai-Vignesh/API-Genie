import { useState } from "react";
import axios from "axios";

export default function App() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<any[]>([]);

  const search = async () => {
    const { data } = await axios.get("http://localhost:8000/catalog/search", {
      params: { q },
    });
    setRows(data);
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>API Genie</h1>
      <div>
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Find APIs..." />
        <button onClick={search}>Search</button>
      </div>
      <table style={{ marginTop: 16, width: "100%" }}>
        <thead>
          <tr>
            <th>Name</th><th>Category</th><th>Auth</th><th>HTTPS</th><th>CORS</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.api_id}>
              <td>{r.api_name}</td>
              <td>{r.category}</td>
              <td>{r.auth_type}</td>
              <td>{String(r.https_supported)}</td>
              <td>{String(r.cors_supported)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
