const cards = [
  ["Manager", "Investigation planning"],
  ["Execution", "Policy-bounded tool runtime"],
  ["Crypto", "Deterministic analysis"],
  ["Evidence", "Traceable findings and timeline"],
];

export default function Home() {
  return (
    <main>
      <div className="card">
        <span className="status">Alpha 0.1</span>
        <h1>CTF-OS</h1>
        <p className="muted">AI-native Capture The Flag investigation console.</p>
      </div>
      <section className="grid" style={{ marginTop: 16 }}>
        {cards.map(([name, description]) => (
          <div className="card" key={name}>
            <h2>{name}</h2>
            <p className="muted">{description}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
