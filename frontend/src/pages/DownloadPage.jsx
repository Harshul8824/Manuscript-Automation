import { useNavigate, useLocation } from 'react-router-dom'
import { downloadDocument } from '../services/api'
import '../styles/pages.css'

export default function DownloadPage({ fileId, fileName }) {
  const navigate = useNavigate()
  const location = useLocation()
  const template = location.state?.template || 'ieee'

  const handleDownload = async () => {
    try {
      await downloadDocument(fileId, template)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  return (
    <div className="download-page">
      <div className="success-container">
        <div className="success-icon">✓</div>
        <h1>Format Complete!</h1>
        <p className="subtitle">Your manuscript has been successfully formatted</p>
        
        <div className="download-info">
          <p><strong>Original File:</strong> {fileName}</p>
          <p><strong>Template:</strong> {template.toUpperCase()}</p>
        </div>

        <button className="btn-primary download-btn" onClick={handleDownload}>
          📥 Download Formatted Document
        </button>

        <button className="btn-secondary" onClick={() => navigate('/')}>
          Start Over
        </button>
      </div>
    </div>
  )
}
