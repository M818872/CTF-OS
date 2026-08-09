"use client";

import { useState } from "react";
import type { FormEvent } from "react";

type SolveResponse = {
  id: string;
  status: string;
  specialists: string[];
  capabilities: string[];
  message: string;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export default function Home() {
  const [challenge, setChallenge] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [solving, setSolving] = useState(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState("");

  async function startSolve(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!challenge.trim() && !url.trim() && !file) return;
    setSolving(true);
    setError("");
    setResult(null);
    try {
      const body = new FormData();
      body.append("challenge", challenge.trim());
      if (url.trim()) body.append("url", url.trim());
      if (file) body.append("file", file);
      const response = await fetch(`${API}/agent/solve`, { method: "POST", body });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "The CTF agent could not start");
      setResult(data);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to start the CTF agent");
    } finally {
      setSolving(false);
    }
  }

  return (
    <main>
      <header className="topbar">
        <div><div className="brand">CTF-OS</div><div className="muted">Autonomous CTF solving agent</div></div>
        <span className="status">READY</span>
      </header>

      <section className="hero card">
        <div>
          <p className="eyebrow">CTF AGENT</p>
          <h1>Give it a challenge. Let the agent solve it.</h1>
          <p className="muted hero-copy">Paste the challenge, provide a target URL, or upload the challenge files. CTF-OS will classify the challenge and prepare the appropriate specialist tools.</p>
        </div>
        <div className="pipeline"><span>INPUT</span><span>ANALYZE</span><span>TOOLS</span><span>EVIDENCE</span><span>FLAG</span></div>
      </section>

      {error && <div className="alert">{error}</div>}

      <section className="workspace">
        <form className="card form-card" onSubmit={startSolve}>
          <div className="section-heading"><div><p className="eyebrow">START SOLVE</p><h2>Challenge input</h2></div></div>
          <label>Challenge description / prompt<textarea value={challenge} onChange={(event) => setChallenge(event.target.value)} placeholder="Paste the CTF challenge description, clues, ciphertext, credentials, source code, or anything you were given..." rows={9} /></label>
          <label>Target URL <span className="muted">(optional)</span><input type="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://target.ctf.local" /></label>
          <label>Challenge file <span className="muted">(optional, max 10 MiB)</span><input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
          {file && <div className="muted">Selected: {file.name} ({Math.ceil(file.size / 1024)} KB)</div>}
          <button type="submit" disabled={solving || (!challenge.trim() && !url.trim() && !file)}>{solving ? "Agent starting..." : "🚀 Start CTF Agent"}</button>
        </form>

        <section className="card cases-card">
          <div className="section-heading"><div><p className="eyebrow">AGENT STATUS</p><h2>What happens next</h2></div></div>
          {!result ? <div className="empty"><strong>Ready for a challenge.</strong><span>Nothing is executed until you press Start CTF Agent.</span></div> : <div className="case-list">
            <div className="case"><div><strong>Challenge received</strong><span>{result.status}</span></div></div>
            <div className="case"><div><strong>Specialists</strong><span>{result.specialists.join(" · ") || "Auto"}</span></div></div>
            <div className="case"><div><strong>Capabilities</strong><span>{result.capabilities.join(" · ") || "Preparing"}</span></div></div>
            <div className="case"><div><strong>Agent</strong><span>{result.message}</span></div></div>
          </div>}
        </section>
      </section>

      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">SOLVE LOOP</p><h2>From challenge to flag</h2></div></div>
        <div className="grid">
          {["Receive challenge", "Classify automatically", "Select specialist", "Use authorized tools", "Collect evidence", "Extract flag"].map((step, index) => <div className="card capability" key={step}><span className="capability-mark">{index + 1}</span><div><h3>{step}</h3><p className="muted">{index < 2 ? "No manual case setup required." : "Handled by the agent runtime."}</p></div></div>)}
        </div>
      </section>
    </main>
  );
}
