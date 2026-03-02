// ══════════════════════════════════════════════════════════════
// SUB-COMPONENT 2: Hero Section
// ══════════════════════════════════════════════════════════════
function HeroSection({ onStartClick }) {
  return (
    <section style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      textAlign: "center",
      padding: "120px 2rem 80px",
      position: "relative",
    }}>

      {/* Floating badge */}
      <div
        className="fade-up delay-1"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          padding: "6px 16px",
          borderRadius: 999,
          border: "1px solid rgba(212,175,55,0.3)",
          background: "rgba(212,175,55,0.06)",
          marginBottom: "2rem",
          fontSize: "0.8rem",
          color: "#d4af37",
          letterSpacing: "0.06em",
          textTransform: "uppercase",
        }}
      >
        <span style={{ animation: "float 3s ease-in-out infinite" }}>✦</span>
        AI-Powered Academic Formatting
      </div>

      {/* Main Headline */}
      <h1
        className="fade-up delay-2"
        style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: "clamp(2.8rem, 6vw, 5rem)",
          fontWeight: 900,
          lineHeight: 1.08,
          letterSpacing: "-0.03em",
          maxWidth: 780,
          marginBottom: "1.5rem",
          color: "#e8e4d9",
        }}
      >
        From Raw Draft to{" "}
        <em style={{ fontStyle: "italic" }}>Publication-Ready</em>
        <br />
        <span className="gold-text">in 15 Minutes</span>
      </h1>

      {/* Subtitle */}
      <p
        className="fade-up delay-3"
        style={{
          fontSize: "clamp(1rem, 2vw, 1.2rem)",
          color: "rgba(232,228,217,0.55)",
          maxWidth: 520,
          lineHeight: 1.7,
          marginBottom: "2.5rem",
          fontWeight: 300,
        }}
      >
        Upload your manuscript. Choose a journal template. Download a
        perfectly formatted, submission-ready document — powered by Claude AI.
      </p>

      {/* CTA Buttons */}
      {/*
        🎓 REACT LESSON: Event Handlers
        onClick={onStartClick} — pass a function reference, NOT a call.
        ✅ onClick={onStartClick}        — correct
        ❌ onClick={onStartClick()}      — wrong (calls immediately on render)
      */}
      <div
        className="fade-up delay-4"
        style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}
      >
        <button
          onClick={onStartClick}
          className="gold-btn"
          style={{
            padding: "14px 32px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
            fontSize: "1rem",
            fontWeight: 600,
            color: "#0a0e1a",
            fontFamily: "'DM Sans', sans-serif",
            letterSpacing: "-0.01em",
          }}
        >
          🚀 Start Formatting
        </button>
        <button
          className="ghost-btn"
          style={{
            padding: "14px 32px",
            borderRadius: 8,
            cursor: "pointer",
            fontSize: "1rem",
            color: "#e8e4d9",
            background: "transparent",
            fontFamily: "'DM Sans', sans-serif",
            letterSpacing: "-0.01em",
          }}
        >
          🎬 Watch Demo
        </button>
      </div>

      {/* Small social proof line */}
      <p
        className="fade-up delay-5"
        style={{
          marginTop: "2rem",
          fontSize: "0.8rem",
          color: "rgba(232,228,217,0.3)",
          letterSpacing: "0.04em",
        }}
      >
        First 5 papers free · No sign-up required
      </p>
    </section>
  );
}

export default HeroSection;