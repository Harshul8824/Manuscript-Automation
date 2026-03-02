// ══════════════════════════════════════════════════════════════
// SUB-COMPONENT 4: How It Works — 3-step process
// ══════════════════════════════════════════════════════════════
function HowItWorks({ onStartClick }) {
  const steps = [
    {
      number: "01",
      label: "Upload",
      desc: "Drag & drop your .docx manuscript — any structure, any length.",
      icon: "📤",
    },
    {
      number: "02",
      label: "Select Template",
      desc: "Choose from IEEE, APA, Springer, and more. Preview before formatting.",
      icon: "📋",
    },
    {
      number: "03",
      label: "Download",
      desc: "Get your perfectly formatted, submission-ready document instantly.",
      icon: "✅",
    },
  ];

  return (
    <section style={{
      padding: "80px 2rem 120px",
      maxWidth: 960,
      margin: "0 auto",
      borderTop: "1px solid rgba(255,255,255,0.05)",
    }}>
      <div style={{ textAlign: "center", marginBottom: "4rem" }}>
        <div className="divider-line" style={{ margin: "0 auto 1rem" }} />
        <h2 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: "clamp(1.8rem, 4vw, 2.8rem)",
          fontWeight: 700,
          color: "#e8e4d9",
          letterSpacing: "-0.02em",
          marginBottom: "0.75rem",
        }}>
          How It Works
        </h2>
        <p style={{
          color: "rgba(232,228,217,0.4)",
          fontSize: "0.95rem",
          fontWeight: 300,
        }}>
          Three steps. Under a minute. Zero formatting headaches.
        </p>
      </div>

      {/* Steps */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "2rem",
        position: "relative",
      }}>
        {steps.map((step, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              gap: "1rem",
            }}
          >
            {/* Step icon circle */}
            <div
              className="step-dot"
              style={{
                width: 56, height: 56,
                borderRadius: "50%",
                background: "rgba(212,175,55,0.1)",
                border: "1px solid rgba(212,175,55,0.3)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.5rem",
              }}
            >
              {step.icon}
            </div>

            <div>
              <span style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: "0.75rem",
                color: "#d4af37",
                letterSpacing: "0.1em",
                display: "block",
                marginBottom: 4,
              }}>
                STEP {step.number}
              </span>
              <h3 style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: "1.3rem",
                fontWeight: 700,
                color: "#e8e4d9",
                marginBottom: "0.5rem",
              }}>
                {step.label}
              </h3>
              <p style={{
                fontSize: "0.9rem",
                color: "rgba(232,228,217,0.45)",
                lineHeight: 1.65,
                fontWeight: 300,
              }}>
                {step.desc}
              </p>
            </div>

            {/* Arrow connector (not on last step) */}
            {index < steps.length - 1 && (
              <div style={{
                position: "absolute",
                // hacky but visual enough for demo
                display: "none", // hidden on mobile grid
              }} />
            )}
          </div>
        ))}
      </div>

      {/* Final CTA */}
      <div style={{ textAlign: "center", marginTop: "4rem" }}>
        <button
          onClick={onStartClick}
          className="gold-btn"
          style={{
            padding: "16px 44px",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
            fontSize: "1rem",
            fontWeight: 700,
            color: "#0a0e1a",
            fontFamily: "'DM Sans', sans-serif",
            letterSpacing: "-0.01em",
          }}
        >
          🚀 Format My Manuscript — It's Free
        </button>
      </div>
    </section>
  );
}

export default HowItWorks;