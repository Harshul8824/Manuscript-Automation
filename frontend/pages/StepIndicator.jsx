/**
 * StepIndicator — Shows "Step 1 of 3", "Step 2 of 3", "Step 3 of 3"
 * with the current step highlighted (gold + label).
 *
 * 🎓 REACT LESSON: Props
 * currentStep (1 | 2 | 3) tells which step is active.
 * The component uses .map() to avoid repeating the same JSX three times.
 */
function StepIndicator({ currentStep = 1 }) {
  const steps = [
    { num: 1, label: "Upload" },
    { num: 2, label: "Review" },
    { num: 3, label: "Download" },
  ];

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      {steps.map((step) => {
        const isActive = step.num === currentStep;
        const isPast = step.num < currentStep;
        return (
          <div
            key={step.num}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <div
              className="step-dot"
              style={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.75rem",
                fontWeight: 600,
                fontFamily: "'DM Sans', sans-serif",
                background: isActive
                  ? "linear-gradient(135deg, #d4af37, #f0d060)"
                  : isPast
                  ? "#34d399"
                  : "rgba(255,255,255,0.08)",
                color: isActive || isPast ? "#0a0e1a" : "rgba(232,228,217,0.5)",
                border: isActive ? "2px solid rgba(212,175,55,0.8)" : "none",
                boxShadow: isActive ? "0 0 16px rgba(212,175,55,0.3)" : "none",
              }}
            >
              {isPast ? "✓" : step.num}
            </div>
            <span
              style={{
                fontSize: "0.8rem",
                color: isActive ? "#e8e4d9" : "rgba(232,228,217,0.5)",
                fontWeight: isActive ? 600 : 400,
              }}
            >
              {step.label}
            </span>
            {step.num < 3 && (
              <span
                style={{
                  width: 24,
                  height: 1,
                  background: "rgba(255,255,255,0.15)",
                  marginLeft: 4,
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default StepIndicator;
