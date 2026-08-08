"use client";

import { FormEvent, useEffect, useState } from "react";

type Investigation = {
  id: string;
  title: string;
  challenge_type: string;
  status: string;
  input_text: string | null;
  created_at: string;
};

type Capability = {
  name: string;
  description: string;
  provider: string;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

const specialists = [
  ["Crypto", "Encoding, hashes and classical cryptanalysis"],
  ["Web", "Discovery and application analysis"],
  ["Forensics", "Files, artifacts and digital evidence"],
  ["Reverse", "Static and dynamic binary analysis"],
  ["Network", "PCAP and protocol investigation"],
  ["Stego", "Hidden data and media analysis"],
];

export default function Home() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [title, setTitle] = useState("");
  const [challengeType, setChallengeType] = useState("unknown");
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setError("");
      const [investigationResponse, capabilityResponse] = await Promise.all([
        fetch(`${API}/investigations`),
        fetch(`${API}/capabilities`),
      ]);
      if (!investigationResponse.ok || !capabilityResponse.ok) {
        throw new Error("CTF-OS backend is unavailable");
      }
      setInvestigations(await investigationResponse.json());
      setCapabilities(await capabilityResponse.json());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to connect to CTF-OS");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function createInvestigation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    setError("");
    try {
      const response = await fetch(`${API}/investigations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.trim(),
          challenge_type: challengeType,
          input_text: inputText.trim() || null,
        }),
      });
      if (!response.ok) throw new Error("Could not create investigation");
      setTitle("");
      setInputText("");
      setChallengeType("unknown");
      await loadDashboard();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not create investigation");
    } finally {
      setCreating(false);
    }
  }

  return (
    <main>
      <header className="topbar">
        <div>
          <div className="brand">CTF-OS</div>
          <div className="muted">AI-native CTF investigation console</div>
        </div>
        <span className="status">Alpha 0.1</span>
      </header>

      <section className="hero card">
        <div>
          <p className="eyebrow">INVESTIGATION WORKSPACE</p>
          <h1>Turn a challenge into a traceable investigation.</h1>
          <p className="muted hero-copy">
            Create a case, route work through specialist capabilities, and keep evidence attached to every meaningful action.
          </p>
        </div>
        <div className="pipeline">
          {['Challenge', 'Manager', 'Workflow', 'Capability', 'Evidence', 'Report'].map((step) => (
            <span key={step}>{step}</span>
          ))}
        </div>
      </section>

      {error && <div className="alert">{error}</div>}

      <section className="workspace">
        <form className="card form-card" onSubmit={createInvestigation}>
          <div className="section-heading">
            <div>
              <p className="eyebrow">NEW CASE</p>
              <h2>Start investigation</h2>
            </div>
            <span className="counter">{investigations.length} cases</span>
          </div>
          <label>
            Investigation title
            <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. CryptoCabana key recovery" />
          </label>
          <label>
            Challenge type
            <select value={challengeType} onChange={(event) => setChallengeType(event.target.value)}>
              <option value="unknown">Auto-detect</option>
              {specialists.map(([name]) => <option key={name} value={name.toLowerCase()}>{name}</option>)}
            </select>
          </label>
          <label>
            Challenge notes / input
            <textarea value={inputText} onChange={(event) => setInputText(event.target.value)} placeholder="Paste the challenge description, clues, URLs, hashes or observations..." rows={6} />
          </label>
          <button type="submit" disabled={creating || !title.trim()}>{creating ? "Creating..." : "Create investigation"}</button>
        </form>

        <section className="card cases-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">ACTIVE CASES</p>
              <h2>Investigations</h2>
            </div>
            <button className="ghost" type="button" onClick={() => void loadDashboard()}>Refresh</button>
          </div>
          {loading ? <p className="muted">Loading investigations...</p> : investigations.length === 0 ? (
            <div className="empty"><strong>No investigations yet.</strong><span>Create your first case to start the CTF-OS workflow.</span></div>
          ) : (
            <div className="case-list">
              {investigations.map((item) => (
                <article className="case" key={item.id}>
                  <div><strong>{item.title}</strong><span>{item.challenge_type} · {item.status}</span></div>
                  <time>{new Date(item.created_at).toLocaleString()}</time>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>

      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">SPECIALISTS</p><h2>Investigation capabilities</h2></div><span className="counter">{capabilities.length} registered</span></div>
        <div className="grid">
          {specialists.map(([name, description]) => <div className="card capability" key={name}><span className="capability-mark">{name.slice(0, 1)}</span><div><h3>{name}</h3><p className="muted">{description}</p></div></div>)}
        </div>
      </section>
    </main>
  );
}
