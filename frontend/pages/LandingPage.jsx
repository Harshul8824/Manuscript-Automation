/**
 * ============================================================
 *  ManuscriptMagic — Screen 1: Landing Page
 * ============================================================
 *
 * 🎓 REACT LESSON: What is a Component?
 * A component is just a JavaScript function that returns JSX
 * (HTML-like syntax). React builds your UI by composing many
 * small components together — like LEGO bricks.
 *
 * This file has:
 *   • 1 big "page" component  → LandingPage
 *   • 4 smaller sub-components → Navbar, HeroSection, HowItWorks, StatsRow
 *
 * Each sub-component is defined separately and used inside
 * LandingPage like a custom HTML tag: <Navbar />, <HeroSection />
 * ============================================================
 */

import { useState, useEffect } from "react";
import Navbar from "./Navbar";
import HeroSection from "./HeroSection";
import StatsRow from "./StatsRow";
import HowItWorks from "./HowItsWorks";

// ─────────────────────────────────────────────
// 🎓 REACT LESSON: Hooks — useState
// useState lets a component "remember" a value.
// Syntax: const [value, setValue] = useState(initialValue)
// When setValue() is called, React re-renders the component.
// ─────────────────────────────────────────────

// ── FONTS (injected into <head> at runtime) ──────────────────
const fontLink = document.createElement("link");
fontLink.rel = "stylesheet";
fontLink.href =
  "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500&display=swap";
document.head.appendChild(fontLink);

// ── GLOBAL STYLES ─────────────────────────────────────────────
const globalStyle = document.createElement("style");
globalStyle.textContent = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0e1a; color: #e8e4d9; font-family: 'DM Sans', sans-serif; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
  }
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-8px); }
  }
  @keyframes pulse-ring {
    0%   { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(212,175,55,0.4); }
    70%  { transform: scale(1);    box-shadow: 0 0 0 14px rgba(212,175,55,0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(212,175,55,0); }
  }
  .fade-up { animation: fadeUp 0.7s ease forwards; opacity: 0; }
  .delay-1 { animation-delay: 0.1s; }
  .delay-2 { animation-delay: 0.25s; }
  .delay-3 { animation-delay: 0.4s; }
  .delay-4 { animation-delay: 0.55s; }
  .delay-5 { animation-delay: 0.7s; }

  .gold-btn {
    background: linear-gradient(135deg, #d4af37, #f0d060, #d4af37);
    background-size: 200% auto;
    transition: background-position 0.5s ease, transform 0.2s, box-shadow 0.2s;
    animation: pulse-ring 2.5s ease infinite;
  }
  .gold-btn:hover {
    background-position: right center;
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(212,175,55,0.35);
    animation: none;
  }
  .ghost-btn {
    border: 1px solid rgba(232,228,217,0.25);
    transition: border-color 0.2s, background 0.2s, transform 0.2s;
  }
  .ghost-btn:hover {
    border-color: rgba(212,175,55,0.6);
    background: rgba(212,175,55,0.07);
    transform: translateY(-2px);
  }
  .stat-card {
    transition: transform 0.25s, box-shadow 0.25s;
  }
  .stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.4);
  }
  .step-dot {
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .step-dot:hover {
    transform: scale(1.1);
    box-shadow: 0 0 20px rgba(212,175,55,0.4);
  }
  .nav-link {
    position: relative;
    transition: color 0.2s;
  }
  .nav-link::after {
    content: '';
    position: absolute;
    bottom: -2px; left: 0;
    width: 0; height: 1px;
    background: #d4af37;
    transition: width 0.25s;
  }
  .nav-link:hover { color: #d4af37; }
  .nav-link:hover::after { width: 100%; }
  .mesh-bg {
    background:
      radial-gradient(ellipse 80% 50% at 20% 20%, rgba(212,175,55,0.07) 0%, transparent 60%),
      radial-gradient(ellipse 60% 60% at 80% 80%, rgba(59,130,246,0.05) 0%, transparent 60%),
      #0a0e1a;
  }
  .grid-overlay {
    background-image:
      linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 48px 48px;
  }
  .gold-text {
    background: linear-gradient(135deg, #d4af37, #f0d060);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .divider-line {
    width: 48px; height: 2px;
    background: linear-gradient(90deg, #d4af37, transparent);
  }
`;
document.head.appendChild(globalStyle);


// ══════════════════════════════════════════════════════════════
// MAIN COMPONENT: LandingPage
//
// 🎓 REACT LESSON: Component Composition
// Big pages are built by COMPOSING smaller components.
// LandingPage doesn't know HOW Navbar or HeroSection work —
// it just places them in order. This is React's superpower.
// ══════════════════════════════════════════════════════════════
export default function LandingPage() {
  // 🎓 This state will eventually navigate to the Upload page.
  // For now it just scrolls to top (we'll wire routing later).
  const handleStartClick = () => {
    alert("🚀 Navigate to Upload Page — we'll wire this in Step 2!");
  };

  return (
    // 🎓 JSX Rule: A component must return ONE root element.
    // We use a <div> wrapper here. Alternatively use <> (Fragment).
    <div className="mesh-bg grid-overlay" style={{ minHeight: "100vh" }}>
      <Navbar onStartClick={handleStartClick} />
      <HeroSection onStartClick={handleStartClick} />
      <StatsRow />
      <HowItWorks onStartClick={handleStartClick} />

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.05)",
        padding: "2rem",
        textAlign: "center",
        fontSize: "0.8rem",
        color: "rgba(232,228,217,0.2)",
        fontWeight: 300,
      }}>
        Built with ❤️ for researchers who deserve better tools · ManuscriptMagic 2025
      </footer>
    </div>
  );
}