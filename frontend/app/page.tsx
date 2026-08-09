"use client";

import { useState } from "react";
import type { FormEvent } from "react";

type SolveResponse = {
  id: string;
  job_id: string;
  status: string;
  specialists: string[];
  capabilities: string[];
  flag?: string | null;
  message: string;
};

type JobResponse = {
  status: string;
  result?: { flag?: string | null; summary?: string; steps?: Array<{ name: string; tokens?: string[] }> } | null;
  error?: string | null;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export default function Home() {
  const [challenge, setChallenge] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [solving, setSolving] = useState(false);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState("");

  async function watchJob(jobId: string) {
    for (;;) {
      const response = await fetch(`${API}/tools/jobs/${jobId}`, { cache: "no-store" });
      const data = (await response.json()) as JobResponse;
      if (!response.ok) throw new Error(data.error ?? "Unable to read solve status");
      setJob(data);
      if (data.status === "completed" || data.status === "failed") return;
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  async function startSolve(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!challenge.trim() && !url.trim() && !file) return;
    setSolving(true);
    setError("");
    setResult(null);
    setJob(null);
    try {
      const body = new FormData();
      body.append("challenge", challenge.trim());
      if (url.trim()) body.append("url", url.trim());
      if (file) body.append("file", file);
      const response = await fetch(`${API}/agent/solve`, { method: "POST", body });
      const data = (await response.json()) as SolveResponse & { detail?: string };
      if (!response.ok) throw new Error(data.detail ?? "The CTF agent could not start");
      setResult(data);
      await watchJob(data.job_id);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to run the CTF agent");
    } finally {
      setSolving(false);
    }
  }

  const flag = job?.result?.flag ?? result?.flag ?? null;

  return (
    <main>
      <header className="topbar">
        <div><div className="brand">CTF-OS</div><div className="muted">Autonomous CTF solving agent</div></div>
        <span className="status">{solving ? "SOLVING" : flag ? "FLAG FOUND" : "READY"}</span>
      </header>

      <section className="hero card">
        <div>
          <p className="eyebrow">CTF AGENT</p>
          <h1>Give it a challenge. Let the agent solve it.</h1>
          <p className="muted hero-copy">Upload a challenge file or give the agent a CTF URL. It queues the solve, runs the available inspection tools, checks every result for a flag, and keeps going through the runtime loop.</p>
        </div>
        <div className="pipeline"><span>INPUT</span><span>ANALYZE</span><span>TOOLS</span><span>INSPECT</span><span>FLAG</span></div>
      </section>

      {error && <div className="alert">{error}</div>}

      {flag && <section className="card flag-card"><p className="eyebrow">FLAG FOUND</p><div className="flag-value">{flag}</div><p className="muted">The agent found this token in the supplied challenge or collected tool output.</p></section>}

      <section className="workspace">
        <form className="card form-card" onSubmit={startSolve}>
          <div className="section-heading"><div><p className="eyebrow">START SOLVE</p><h2>Challenge input</h2></div></div>
          <label>Challenge description / prompt<textarea value={challenge} onChange={(event) => setChallenge(event.target.value)} placeholder="Paste the challenge text or clues (optional if you upload a file or provide a URL)..." rows={9} /></label>
          <label>Target URL <span className="muted">(optional)</span><input type="url" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://target.ctf.local" /></label>
          <label>Challenge file <span className="muted">(optional, max 10 MiB)</span><input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label>
          {file && <div className="muted">Selected: {file.name} ({Math.ceil(file.size / 1024)} KB)</div>}
          <button type="submit" disabled={solving || (!challenge.trim() && !url.trim() && !file)}>{solving ? "Agent is solving..." : "🚀 Start CTF Agent"}</button>
        </form>

        <section className="card cases-card">
          <div className="section-heading"><div><p className="eyebrow">LIVE SOLVE</p><h2>{job?.status ?? result?.status ?? "Ready"}</h2></div></div>
          {!result ? <div className="empty"><strong>Ready for a challenge.</strong><span>Give the agent a file, URL, challenge text, or any combination.</span></div> : <div className="case-list">
            <div className="case"><div><strong>Specialists</strong><span>{result.specialists.join(" · ") || "Auto"}</span></div></div>
            <div className="case"><div><strong>Capabilities</strong><span>{result.capabilities.join(" · ") || "Preparing"}</span></div></div>
            <div className="case"><div><strong>Runtime</strong><span>{job?.result?.summary ?? result.message}</span></div></div>
            {job?.result?.steps?.map((step) => <div className="case" key={step.name}><div><strong>{step.name}</strong><span>{step.tokens?.join(" · ") || "completed"}</span></div></div>)}
          </div>}
        </section>
      </section>
    </main>
  );
}
