import { useCallback } from 'react'
import '../styles/components.css'

export default function UploadBox({ onUpload, loading }) {
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      onUpload(file)
    }
  }, [onUpload])

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <div
      className="upload-box"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <input
        type="file"
        id="file-input"
        accept=".docx"
        onChange={handleFileSelect}
        disabled={loading}
        hidden
      />
      <label htmlFor="file-input">
        <div className="upload-icon">📄</div>
        <p className="upload-text">
          {loading ? 'Uploading...' : 'Drag & drop your DOCX file here'}
        </p>
        <p className="upload-subtext">or click to select</p>
      </label>
    </div>
  )
}
