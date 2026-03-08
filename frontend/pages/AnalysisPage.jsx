import { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";

const steps = [
    { id: 1, label: "Uploading Document..." },
    { id: 2, label: "Extracting Structure (AI Analysis)..." },
    { id: 3, label: "Formatting to IEEE Standard..." },
    { id: 4, label: "Ready for Download" },
];

export default function AnalysisPage() {
    const location = useLocation();
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(2); // Start at 2 since upload is done
    const [error, setError] = useState(null);
    const [analysisData, setAnalysisData] = useState(null);
    const hasStarted = useRef(false);

    const { fileName, jobId } = location.state || {};

    useEffect(() => {
        if (!jobId) {
            navigate("/upload");
            return;
        }

        if (hasStarted.current) return;
        hasStarted.current = true;

        const processDocument = async () => {
            try {
                // Step 2: Analyze
                setCurrentStep(2);
                const analyzeRes = await fetch(`http://127.0.0.1:5000/api/documents/analyze/${jobId}`, {
                    method: "POST",
                });

                if (!analyzeRes.ok) throw new Error("Analysis failed");
                const analyzeData = await analyzeRes.json();
                setAnalysisData(analyzeData);

                // Step 3: Format
                setCurrentStep(3);
                const formatRes = await fetch(`http://127.0.0.1:5000/api/documents/format/${jobId}`, {
                    method: "POST",
                });

                if (!formatRes.ok) throw new Error("Formatting failed");

                // Trigger Download
                const blob = await formatRes.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                // The backend returns it as formatted_<filename>.docx, let's just use what they gave or a default
                a.download = `Formatted_${fileName || "document.docx"}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);

                setCurrentStep(4);
            } catch (err) {
                console.error(err);
                setError(err.message || "An error occurred during processing.");
            }
        };

        processDocument();
    }, [jobId, navigate, fileName]);

    return (
        <div className="mesh-bg grid-overlay" style={{ minHeight: "100vh", paddingTop: 64 }}>
            <Navbar currentStep={2} />

            <main style={{ maxWidth: 720, margin: "0 auto", padding: "4rem 1.5rem" }}>
                <h1
                    style={{
                        fontFamily: "'Playfair Display', serif",
                        fontSize: "2rem",
                        color: "#e8e4d9",
                        marginBottom: "1rem",
                        textAlign: "center"
                    }}
                >
                    {error ? "Processing Failed" : "Processing Manuscript"}
                </h1>

                <div style={{
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(212,175,55,0.2)",
                    borderRadius: 12,
                    padding: "2rem",
                    marginTop: "2rem"
                }}>

                    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                        {steps.map((step) => {
                            const matches = currentStep === step.id;
                            const completed = currentStep > step.id;

                            let color = "rgba(232,228,217,0.3)";
                            if (completed) color = "#34d399"; // Green
                            if (matches && !error) color = "#d4af37"; // Gold
                            if (matches && error) color = "#f87171"; // Red

                            return (
                                <div key={step.id} style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                                    <div style={{
                                        width: 24, height: 24, borderRadius: "50%",
                                        background: completed ? "#34d399" : (matches && !error ? "rgba(212,175,55,0.2)" : "transparent"),
                                        border: `2px solid ${color}`,
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        color: completed ? "#000" : color,
                                        fontSize: "0.8rem", fontWeight: "bold"
                                    }}>
                                        {completed ? "✓" : step.id}
                                    </div>
                                    <span style={{ color: color, fontSize: "1.1rem", fontWeight: matches ? 600 : 400 }}>
                                        {step.label} {matches && !error && "..."}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    {error && (
                        <div style={{ marginTop: "2rem", padding: "1rem", background: "rgba(248,113,113,0.1)", border: "1px solid #f87171", borderRadius: 8, color: "#f87171" }}>
                            <strong>Error:</strong> {error}
                            <br /><br />
                            <button
                                onClick={() => navigate("/upload")}
                                className="ghost-btn"
                                style={{ padding: "8px 16px", borderRadius: 6, color: "#e8e4d9", background: "transparent", cursor: "pointer", border: "1px solid rgba(255,255,255,0.2)" }}
                            >
                                Try Again
                            </button>
                        </div>
                    )}

                    {currentStep === 4 && (
                        <div style={{ marginTop: "2rem", textAlign: "center" }}>
                            <p style={{ color: "#34d399", marginBottom: "1.5rem", fontSize: "1.1rem" }}>
                                Success! Your formatted document has been downloaded.
                            </p>
                            <button
                                onClick={() => navigate("/upload")}
                                className="gold-btn"
                                style={{
                                    padding: "12px 24px", borderRadius: 8, border: "none",
                                    cursor: "pointer", fontSize: "0.95rem", fontWeight: 600,
                                    color: "#0a0e1a", fontFamily: "'DM Sans', sans-serif"
                                }}
                            >
                                Process Another Document
                            </button>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
