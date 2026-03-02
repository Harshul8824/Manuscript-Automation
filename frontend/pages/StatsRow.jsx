// ══════════════════════════════════════════════════════════════
// SUB-COMPONENT 3: Stats Row (Fast / Accurate / Free)
// ══════════════════════════════════════════════════════════════
function StatsRow() {
  // 🎓 Array of objects — a common React pattern for rendering lists
  const stats = [
    {
      icon: "⚡",
      title: "15× Faster",
      desc: "15 minutes vs 3–8 hours of manual formatting",
      color: "#fbbf24",
    },
    {
      icon: "🎯",
      title: "92–95% Accurate",
      desc: "AI-powered section detection, tested on 500+ papers",
      color: "#34d399",
    },
    {
      icon: "🎁",
      title: "Free to Start",
      desc: "First 5 papers completely free, no credit card",
      color: "#60a5fa",
    },
  ];

  return (
    <section style={{
      padding: "0 2rem 100px",
      maxWidth: 960,
      margin: "0 auto",
    }}>
      {/* Section label */}
      <div style={{ textAlign: "center", marginBottom: "3rem" }}>
        <div className="divider-line" style={{ margin: "0 auto 1rem" }} />
        <p style={{
          fontSize: "0.75rem",
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: "rgba(232,228,217,0.35)",
        }}>
          Why researchers choose us
        </p>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: "1.5rem",
      }}>
        {stats.map((stat, index) => (
          // 🎓 key={index} is fine here since the list never reorders
          <div
            key={index}
            className="stat-card"
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: 16,
              padding: "2rem",
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Subtle glow in top-left corner */}
            <div style={{
              position: "absolute",
              top: -20, left: -20,
              width: 80, height: 80,
              borderRadius: "50%",
              background: stat.color,
              opacity: 0.06,
              filter: "blur(20px)",
            }} />

            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>
              {stat.icon}
            </div>
            <h3 style={{
              fontFamily: "'Playfair Display', serif",
              fontSize: "1.4rem",
              fontWeight: 700,
              color: stat.color,
              marginBottom: "0.5rem",
            }}>
              {stat.title}
            </h3>
            <p style={{
              fontSize: "0.9rem",
              color: "rgba(232,228,217,0.5)",
              lineHeight: 1.6,
              fontWeight: 300,
            }}>
              {stat.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default StatsRow;