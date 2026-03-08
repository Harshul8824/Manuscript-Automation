import { useState, useEffect } from "react";
import StepIndicator from "./StepIndicator";

// ══════════════════════════════════════════════════════════════
// SUB-COMPONENT 1: Navbar
// ══════════════════════════════════════════════════════════════
// 🎓 REACT LESSON: Props
// Props are inputs you pass into a component — like HTML attributes.
// e.g. <Navbar scrolled={true} currentStep={1} />  ← "currentStep" is a prop
// When currentStep is 1–3, we show app nav (StepIndicator + Help + Avatar).
// When currentStep is missing/0, we show landing nav (About, Demo, Get Started).
// ──────────────────────────────────────────────────────────────
function Navbar({ onStartClick, currentStep }) {
  const [scrolled, setScrolled] = useState(false);
  const isAppMode = currentStep >= 1;

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      style={{
        position: "fixed",
        top: 0, left: 0, right: 0,
        zIndex: 100,
        padding: "0 2rem",
        height: "64px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: scrolled
          ? "rgba(10,14,26,0.92)"
          : "transparent",
        backdropFilter: scrolled ? "blur(12px)" : "none",
        borderBottom: scrolled
          ? "1px solid rgba(212,175,55,0.15)"
          : "none",
        transition: "background 0.4s, border-color 0.4s",
      }}
    >
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <div style={{
          width: 32, height: 32,
          background: "linear-gradient(135deg, #d4af37, #f0d060)",
          borderRadius: 6,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 16,
        }}>📄</div>
        <span style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: "1.1rem",
          fontWeight: 700,
          color: "#e8e4d9",
          letterSpacing: "-0.02em",
        }}>
          Manuscript<span className="gold-text">Magic</span>
        </span>
      </div>

      {/* Center: Step indicator (app mode) or nothing (landing) */}
      <div style={{ position: "absolute", left: "50%", transform: "translateX(-50%)" }}>
        {isAppMode && <StepIndicator currentStep={currentStep} />}
      </div>

      {/* Right: App nav (Help + Avatar) or Landing nav (links + Get Started) */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        {isAppMode ? (
          <>
            <button
              type="button"
              className="ghost-btn"
              style={{
                padding: "8px 14px",
                borderRadius: 6,
                background: "transparent",
                color: "rgba(232,228,217,0.8)",
                fontSize: "0.875rem",
                fontFamily: "'DM Sans', sans-serif",
                cursor: "pointer",
              }}
            >
              Help
            </button>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.08)",
                border: "1px solid rgba(255,255,255,0.12)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1rem",
                cursor: "pointer",
              }}
              title="Account"
            >
              👤
            </div>
          </>
        ) : (
          <>
            {["About", "Demo", "GitHub"].map((link) => (
              <a
                key={link}
                href="#"
                className="nav-link"
                style={{
                  color: "rgba(232,228,217,0.65)",
                  fontSize: "0.875rem",
                  textDecoration: "none",
                  letterSpacing: "0.02em",
                }}
              >
                {link}
              </a>
            ))}
            <button
              onClick={onStartClick}
              className="gold-btn"
              style={{
                padding: "8px 20px",
                borderRadius: 6,
                border: "none",
                cursor: "pointer",
                fontSize: "0.875rem",
                fontWeight: 600,
                color: "#0a0e1a",
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              Get Started
            </button>
          </>
        )}
      </div>
    </nav>
  );
}


export default Navbar;