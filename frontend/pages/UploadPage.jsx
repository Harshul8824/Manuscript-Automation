/**
 * ============================================================
 *  ManuscriptMagic — Screen 2: Upload Page (/upload)
 * ============================================================
 *
 * 🎓 REACT LESSON: useRef, useNavigate, useLocation
 * - useRef: holds a reference to the hidden <input type="file"> so we can
 *   trigger .click() when user clicks "Browse Files".
 * - useNavigate: programmatic navigation (e.g. navigate("/analysis")).
 * - useLocation: read state passed from previous page (we'll use it on /analysis).
 *
 * State lifted in this component: selectedFile (the File object or null).
 * We pass fileName via router state when continuing to /analysis.
 */

import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";

// ── Ensure fonts and shared styles exist (same as Landing) ─────
const fontLink = document.createElement("link");
fontLink.rel = "stylesheet";
fontLink.href =
  "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500;600&display=swap";
if (!document.querySelector('link[href*="Playfair+Display"]')) document.head.appendChild(fontLink);

// Page-specific keyframes (spinner for "Uploading...")
const pageStyles = document.createElement("style");
pageStyles.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .upload-spinner {
    animation: spin 0.9s linear infinite;
  }
`;
if (!document.getElementById("upload-page-styles")) {
  pageStyles.id = "upload-page-styles";
  document.head.appendChild(pageStyles);
}

const MAX_SIZE_MB = 20;
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ALLOWED_EXT = ".docx";

// Mock recent uploads and sample docs
const MOCK_RECENT_UPLOADS = [
  { id: 1, name: "thesis_chapter2.docx", size: "1.2 MB", date: "Mar 5, 2025" },
  { id: 2, name: "paper_revision_v3.docx", size: "890 KB", date: "Mar 3, 2025" },
];
const MOCK_SAMPLES = [
  { id: "ieee", label: "Try with IEEE Sample Paper", filename: "ieee_sample.docx" },
  { id: "apa", label: "Try with APA Sample Paper", filename: "apa_sample.docx" },
];

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function validateFile(file) {
  if (!file) return null;
  const name = (file.name || "").toLowerCase();
  if (!name.endsWith(ALLOWED_EXT))
    return "Only .docx files are allowed.";
  if (file.size > MAX_BYTES)
    return `File must be under ${MAX_SIZE_MB} MB.`;
  return null;
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [validationError, setValidationError] = useState(null);

  // 🎓 useRef: reference to the hidden file input so we can trigger .click()
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer?.files?.[0];
    if (!file) return;
    const err = validateFile(file);
    setValidationError(err || null);
    setSelectedFile(err ? null : file);
  };

  const handleFileInputChange = (e) => {
    const file = e.target?.files?.[0];
    if (!file) return;
    const err = validateFile(file);
    setValidationError(err || null);
    setSelectedFile(err ? null : file);
    e.target.value = "";
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleUseAgain = (name) => {
    // Mock: set a fake file so UI shows "file selected" with that name
    setSelectedFile({
      name,
      size: 1024000,
      __mock: true,
    });
    setValidationError(null);
  };

  const handleLoadSample = (filename) => {
    setSelectedFile({
      name: filename,
      size: 2048000,
      __mock: true,
    });
    setValidationError(null);
  };

  const handleContinue = async () => {
    if (!selectedFile || isUploading) return;
    setIsUploading(true);
    setValidationError(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setIsUploading(false);

      navigate("/analysis", {
        state: {
          fileName: selectedFile.name,
          fileSize: selectedFile.size,
          jobId: data.job_id
        }
      });
    } catch (err) {
      console.error(err);
      setValidationError("Upload failed. Make sure the Flask backend is running on port 5000.");
      setIsUploading(false);
    }
  };

  const fileName = selectedFile?.name || "";
  const fileSize = selectedFile?.size;
  const canContinue = !!selectedFile && !isUploading;

  return (
    <div className="mesh-bg grid-overlay" style={{ minHeight: "100vh", paddingTop: 64 }}>
      <Navbar currentStep={1} />

      <main style={{ maxWidth: 720, margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <h1
          style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "1.75rem",
            fontWeight: 700,
            color: "#e8e4d9",
            marginBottom: "0.5rem",
          }}
        >
          Upload Your Manuscript
        </h1>
        <p
          style={{
            fontSize: "0.95rem",
            color: "rgba(232,228,217,0.7)",
            marginBottom: "2rem",
            lineHeight: 1.5,
          }}
        >
          Your document will be analyzed using AI to detect sections, references, and structure
        </p>

        {/* Hidden file input — useRef gives us access to trigger .click() */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".docx"
          onChange={handleFileInputChange}
          style={{ display: "none" }}
        />

        {/* Drag-and-drop zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          style={{
            background: "rgba(255,255,255,0.03)",
            border: `2px dashed ${selectedFile ? "#34d399" : isDragging ? "#d4af37" : "rgba(212,175,55,0.5)"}`,
            borderRadius: 12,
            padding: "2.5rem",
            textAlign: "center",
            transition: "border-color 0.2s, box-shadow 0.2s",
            boxShadow: isDragging ? "0 0 24px rgba(212,175,55,0.2)" : selectedFile ? "0 0 20px rgba(52,211,153,0.15)" : "none",
          }}
        >
          {selectedFile ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.75rem" }}>
              <span style={{ fontSize: "2rem" }}>📄</span>
              <span style={{ color: "#e8e4d9", fontWeight: 600 }}>{fileName}</span>
              <span style={{ color: "rgba(232,228,217,0.6)", fontSize: "0.875rem" }}>
                {typeof fileSize === "number" ? formatFileSize(fileSize) : "2.0 MB"}
              </span>
              <button
                type="button"
                onClick={handleRemoveFile}
                className="ghost-btn"
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  background: "transparent",
                  color: "rgba(232,228,217,0.9)",
                  fontSize: "0.85rem",
                  cursor: "pointer",
                  marginTop: "0.5rem",
                }}
              >
                Remove
              </button>
            </div>
          ) : (
            <>
              <span style={{ fontSize: "2.5rem", display: "block", marginBottom: "0.5rem" }}>
                {isDragging ? "📥" : "📤"}
              </span>
              <p style={{ color: "#e8e4d9", fontSize: "1rem", marginBottom: "0.5rem" }}>
                Drag & Drop DOCX Here
              </p>
              <p style={{ color: "rgba(232,228,217,0.5)", fontSize: "0.9rem", marginBottom: "1rem" }}>or</p>
              <button
                type="button"
                onClick={handleBrowseClick}
                className="ghost-btn"
                style={{
                  padding: "10px 20px",
                  borderRadius: 6,
                  border: "1px solid rgba(212,175,55,0.5)",
                  background: "rgba(212,175,55,0.08)",
                  color: "#e8e4d9",
                  fontSize: "0.9rem",
                  cursor: "pointer",
                }}
              >
                Browse Files
              </button>
            </>
          )}
        </div>

        {validationError && (
          <p style={{ color: "#f87171", fontSize: "0.875rem", marginTop: "0.75rem" }}>
            {validationError}
          </p>
        )}

        {/* Info banner — blue tint */}
        <div
          style={{
            marginTop: "1.5rem",
            padding: "1rem 1.25rem",
            background: "rgba(96,165,250,0.08)",
            border: "1px solid rgba(96,165,250,0.2)",
            borderRadius: 8,
            color: "rgba(232,228,217,0.9)",
            fontSize: "0.9rem",
            lineHeight: 1.5,
          }}
        >
          Your document will be analyzed using AI to identify title, authors, sections, references, tables, and figures. No data is stored without your consent.
        </div>

        {/* Recent Uploads */}
        <h2
          style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "1.1rem",
            color: "#e8e4d9",
            marginTop: "2.5rem",
            marginBottom: "0.75rem",
          }}
        >
          Recent Uploads
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {MOCK_RECENT_UPLOADS.map((item) => (
            <div
              key={item.id}
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 8,
                padding: "0.75rem 1rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "0.5rem",
              }}
            >
              <div>
                <span style={{ color: "#e8e4d9", fontSize: "0.9rem" }}>{item.name}</span>
                <span style={{ color: "rgba(232,228,217,0.5)", fontSize: "0.8rem", marginLeft: "0.5rem" }}>
                  {item.size} · {item.date}
                </span>
              </div>
              <button
                type="button"
                onClick={() => handleUseAgain(item.name)}
                className="ghost-btn"
                style={{
                  padding: "6px 12px",
                  borderRadius: 6,
                  background: "transparent",
                  color: "rgba(232,228,217,0.9)",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                Use Again
              </button>
            </div>
          ))}
        </div>

        {/* Sample Documents */}
        <h2
          style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "1.1rem",
            color: "#e8e4d9",
            marginTop: "2rem",
            marginBottom: "0.75rem",
          }}
        >
          Sample Documents
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          {MOCK_SAMPLES.map((sample) => (
            <div
              key={sample.id}
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 8,
                padding: "0.75rem 1rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: "0.5rem",
              }}
            >
              <span style={{ color: "#e8e4d9", fontSize: "0.9rem" }}>{sample.label}</span>
              <button
                type="button"
                onClick={() => handleLoadSample(sample.filename)}
                className="ghost-btn"
                style={{
                  padding: "6px 12px",
                  borderRadius: 6,
                  background: "transparent",
                  color: "rgba(232,228,217,0.9)",
                  fontSize: "0.8rem",
                  cursor: "pointer",
                }}
              >
                Load Sample
              </button>
            </div>
          ))}
        </div>

        {/* Continue button — bottom right */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "2.5rem" }}>
          <button
            type="button"
            onClick={handleContinue}
            disabled={!canContinue}
            className="gold-btn"
            style={{
              padding: "12px 24px",
              borderRadius: 8,
              border: "none",
              cursor: canContinue ? "pointer" : "not-allowed",
              fontSize: "0.95rem",
              fontWeight: 600,
              color: "#0a0e1a",
              fontFamily: "'DM Sans', sans-serif",
              opacity: canContinue ? 1 : 0.5,
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            {isUploading ? (
              <>
                <span className="upload-spinner" style={{ display: "inline-block", fontSize: "1.1rem" }}>⏳</span>
                Uploading...
              </>
            ) : (
              "Continue →"
            )}
          </button>
        </div>
      </main>
    </div>
  );
}
