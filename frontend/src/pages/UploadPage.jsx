import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import UploadBox from '../components/UploadBox'
import { uploadDocument } from '../services/api'
import '../styles/pages.css'

export default function UploadPage({ onUpload }) {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileUpload = async (file) => {
    setLoading(true)
    setError(null)
    try {
      const response = await uploadDocument(file)
      const { fileId } = response.data
      onUpload(fileId, file.name)
      // Simulate processing then navigate
      setTimeout(() => {
        navigate('/analysis')
      }, 1000)
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-page">
      <h1>Transform Your Manuscript</h1>
      <p className="subtitle">Upload your DOCX file to get started</p>
      <UploadBox onUpload={handleFileUpload} loading={loading} />
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}
