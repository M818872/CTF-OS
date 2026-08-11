"use client";

import { useRef, useState } from "react";
import type { ChangeEvent, DragEvent, FormEvent } from "react";

type SolveResponse = {
  job_id: string;
  status: string;
  flag?: string | null;
  message: string;
};

type JobResponse = {
  status: string;
  result?: { flag?: string | null; summary?: string } | null;
  error?: string | null;
};

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export default function Home() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [solving, setSolving] = useState(false);
  const [status, setStatus] = useState("READY");
  const [flag, setFlag] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function watchJob(jobId: string) {
    for (;;) {
      const response = await fetch(`${API}/tools/jobs/${jobId}`, { cache: "no-store" });
      const data = (await response.json()) as JobResponse;
      if (!response.ok) throw new Error(data.error ?? "Unable to read agent status");

      const discoveredFlag = data.result?.flag ?? null;
      if (discoveredFlag) {
        setFlag(discoveredFlag);
        setStatus("FLAG FOUND");
        setMessage(data.result?.summary ?? "The CTF agent found the flag.");
      } else {
        setStatus(data.status.toUpperCase());
        setMessage(data.result?.summary ?? "The agent is working through the challenge...");
      }

      if (data.status === "completed" || data.status === "failed") {
        if (data.status === "failed") throw new Error(data.error ?? "The agent could not solve the challenge");
        return;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  async function solve(selectedFile: File | null = file) {
    if (!selectedFile && !url.trim()) return;
    setSolving(true);
    setStatus("ANALYZING");
    setFlag(null);
    setError("");
    setMessage("Sending the challenge to the autonomous CTF agent...");
    try {
      const body = new FormData();
      body.append("challenge", "");
      if (url.trim()) body.append("url", url.trim());
      if (selectedFile) body.append("file", selectedFile);
      const response = await fetch(`${API}/agent/solve`, { method: "POST", body });
      const data = (await response.json()) as SolveResponse & { detail?: string };
      if (!response.ok) throw new Error(data.detail ?? "The CTF agent could not start");
      setStatus("SOLVING");
      setMessage(data.message);
      if (data.flag) {
        setFlag(data.flag);
        setStatus("FLAG FOUND");
      }
      await watchJob(data.job_id);
    } catch (cause) {
      setStatus("ERROR");
      setError(cause instanceof Error ? cause.message : "Unable to run the CTF agent");
    } finally {
      setSolving(false);
    }
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    if (selected) void solve(selected);
  }

  function dropFile(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const dropped = event.dataTransfer.files?.[0] ?? null;
    setFile(dropped);
    if (dropped) void solve(dropped);
  }

  function submitUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void solve(null);
  }

  return (
    <main className="solver-page">
      <header className="solver-header">
        <div className="brand">CTF-OS</div>
        <span className={`status ${status === "FLAG FOUND" ? "found" : ""}`}>{status}</span>
      </header>

      <section className="solver-hero">
        <p className="eyebrow">AUTONOMOUS CTF AGENT</p>
        <h1>Upload the challenge.<br />Get the flag.</h1>
        <p className="solver-subtitle">No cases. No investigation setup. Give the agent a challenge and let it work.</p>
      </section>

      <section className="solver-card">
        <div
          className={`drop-zone ${solving ? "busy" : ""}`}
          onClick={() => !solving && fileInput.current?.click()}
          onDragOver={(event) => event.preventDefault()}
          onDrop={dropFile}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") fileInput.current?.click(); }}
        >
          <input ref={fileInput} type="file" onChange={chooseFile} hidden />
          <div className="drop-icon">↑</div>
          <h2>{solving ? "Agent is solving..." : file ? file.name : "Drop your CTF challenge here"}</h2>
          <p>{solving ? message : "or click to choose a file"}</p>
        </div>

        <div className="or-divider"><span>OR</span></div>

        <form className="url-form" onSubmit={submitUrl}>
          <input
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="Paste CTF challenge URL..."
            disabled={solving}
          />
          <button type="submit" disabled={solving || !url.trim()}>Solve URL</button>
        </form>

        {solving && <div className="solve-status"><span className="pulse" /> {message || "Agent is solving the challenge..."}</div>}
        {error && <div className="solve-error">{error}</div>}
      </section>

      {flag && (
        <section className="flag-result">
          <p className="eyebrow">FLAG FOUND</p>
          <div className="flag-value">{flag}</div>
          <button type="button" onClick={() => navigator.clipboard?.writeText(flag)}>Copy flag</button>
        </section>
      )}

      {!flag && !solving && !error && <p className="solver-footer">The agent will analyze the challenge, choose tools, inspect results, and search for the flag.</p>}
    </main>
  );
}
