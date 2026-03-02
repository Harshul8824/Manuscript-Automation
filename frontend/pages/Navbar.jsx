import { useState, useEffect } from "react";

// ══════════════════════════════════════════════════════════════
// SUB-COMPONENT 1: Navbar
// ══════════════════════════════════════════════════════════════
// 🎓 REACT LESSON: Props
// Props are inputs you pass into a component — like HTML attributes.
// e.g. <Navbar scrolled={true} />  ← "scrolled" is a prop
// Inside the component, access via: function Navbar({ scrolled })
// ──────────────────────────────────────────────────────────────
function Navbar({ onStartClick }) {
  // 🎓 useState: track if user has scrolled (for nav background)
  const [scrolled, setScrolled] = useState(false);

  // 🎓 REACT LESSON: useEffect
  // useEffect runs *after* the component renders.
  // The [] means "run this only ONCE when component first mounts."
  // Use it for: event listeners, API calls, timers, DOM access.
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll); // cleanup
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
        // 🎓 Dynamic styles: use JS expressions inside style={{}}
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

      {/* Nav Links */}
      <div style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
        {["About", "Demo", "GitHub"].map((link) => (
          // 🎓 .map() renders a list — always add a unique "key" prop!
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
      </div>
    </nav>
  );
}


export default Navbar;