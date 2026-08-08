"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Activity = { id: string; kind: string; action: string; status: string; details: string | null; created_at: string };
type Workspace = {
  investigation: { id: string; title: string; challenge_type: string; status: string; input_text: string | null; created_at: string };
  specialists: string[];
  capabilities: string[];
  activities: Activity[];
};
type ToolResult = { capability: string; status: string; summary: string; data: Record<string, unknown> };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export default function InvestigationPage({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState("");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [goal, setGoal] = useState("");
  const [selected, setSelected] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ToolResult | null>(null);

  async function load(caseId: string) {
    const response = await fetch(`${API}/investigations/${caseId}/workspace`);
    if (!response.ok) throw new Error("Investigation could not be loaded");
    const data = (await response.json()) as Workspace;
    setWorkspace(data);
    setSelected(data.capabilities[0] ?? "");
    setGoal(data.investigation.input_text ?? "");
  }

  useEffect(() => {
    void params.then(({ id: caseId }) => {
      setId(caseId);
      void load(caseId).catch((cause) => setError(cause instanceof Error ? cause.message : "Load failed"));
    });
  }, [params]);

  async function plan() {
    if (!id) return;
    setBusy(true); setError("");
    try {
      const response = await fetch(`${API}/investigations/${id}/plan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ goal }) });
      if (!response.ok) throw new Error("Planning failed");
      await load(id);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Planning failed"); }
    finally { setBusy(false); }
  }

  async function executeCapability() {
    if (!id || !selected) return;
    setBusy(true); setError(""); setResult(null);
    try {
      const response = await fetch(`${API}/tools/execute`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ capability: selected, input_text: goal }) });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || "Capability execution failed");
      }
      const data = (await response.json()) as ToolResult;
      setResult(data);
      await fetch(`${API}/investigations/${id}/execute`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ capability: selected, input_text: goal }) });
      await load(id);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Execution failed"); }
    finally { setBusy(false); }
  }

  if (!workspace) return <main><Link href="/">← Dashboard</Link><div className="card" style={{ marginTop: 16 }}>{error || "Loading workspace..."}</div></main>;

  return (
    <main>
      <header className="topbar">
        <div><Link href="/" className="muted">← Dashboard</Link><div className="brand" style={{ marginTop: 8 }}>{workspace.investigation.title}</div></div>
        <span className="status">{workspace.investigation.status}</span>
      </header>
      {error && <div className="alert">{error}</div>}

      <section className="grid" style={{ gridTemplateColumns: "1.1fr .9fr", marginTop: 16 }}>
        <div className="card">
          <p className="eyebrow">CHALLENGE INPUT</p>
          <h2>{workspace.investigation.challenge_type}</h2>
          <pre style={{ whiteSpace: "pre-wrap", color: "#9aa6ba", lineHeight: 1.6 }}>{workspace.investigation.input_text || "No challenge input supplied."}</pre>
        </div>
        <div className="card">
          <p className="eyebrow">MANAGER</p>
          <h2>Build the next workflow</h2>
          <textarea rows={5} value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="Describe what you want CTF-OS to investigate..." />
          <button onClick={() => void plan()} disabled={busy} style={{ marginTop: 12, padding: "11px 15px", borderRadius: 9, background: "#8eb0ff", fontWeight: 800 }}>{busy ? "Working..." : "Plan investigation"}</button>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">ROUTING</p><h2>Selected specialists</h2></div><span className="counter">{workspace.specialists.length} routed</span></div>
        <div className="grid">{workspace.specialists.length ? workspace.specialists.map((name) => <div className="card capability" key={name}><span className="capability-mark">{name[0].toUpperCase()}</span><div><h3>{name}</h3><p className="muted">Specialist selected by the deterministic manager.</p></div></div>) : <div className="card muted">Plan the investigation to route specialists.</div>}</div>
      </section>

      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">CAPABILITIES</p><h2>Controlled execution</h2></div></div>
        <div className="card">
          <select value={selected} onChange={(event) => setSelected(event.target.value)} disabled={!workspace.capabilities.length}>
            {!workspace.capabilities.length && <option value="">No capabilities routed yet</option>}
            {workspace.capabilities.map((capability) => <option key={capability} value={capability}>{capability}</option>)}
          </select>
          <button className="ghost" onClick={() => void executeCapability()} disabled={busy || !selected} style={{ marginTop: 12 }}>{busy ? "Executing..." : "Run capability"}</button>
          <p className="muted" style={{ fontSize: 12, marginBottom: 0 }}>Execution is allow-listed and policy-bounded. No arbitrary shell commands are run.</p>
        </div>
        {result && <div className="card" style={{ marginTop: 12 }}><p className="eyebrow">RESULT</p><h3>{result.capability} · {result.status}</h3><p className="muted">{result.summary}</p><pre style={{ whiteSpace: "pre-wrap", color: "#9aa6ba" }}>{JSON.stringify(result.data, null, 2)}</pre></div>}
      </section>

      <section className="section-block">
        <div className="section-heading"><div><p className="eyebrow">EVIDENCE / TIMELINE</p><h2>Activity</h2></div><span className="counter">{workspace.activities.length} events</span></div>
        <div className="case-list">{workspace.activities.length ? workspace.activities.map((event) => <article className="case" key={event.id}><div><strong>{event.action}</strong><span>{event.kind} · {event.status}{event.details ? ` · ${event.details}` : ""}</span></div><time>{new Date(event.created_at).toLocaleString()}</time></article>) : <div className="card muted">No activity yet.</div>}</div>
      </section>
    </main>
  );
}
