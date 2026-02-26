import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import TemplateCard from '../components/TemplateCard'
import '../styles/pages.css'

const TEMPLATES = [
  {
    id: 'ieee',
    name: 'IEEE',
    description: 'IEEE Standard Format',
    icon: '📋'
  },
  {
    id: 'apa',
    name: 'APA',
    description: 'American Psychological Association',
    icon: '📚'
  },
  {
    id: 'mla',
    name: 'MLA',
    description: 'Modern Language Association',
    icon: '✍️'
  },
  {
    id: 'chicago',
    name: 'Chicago',
    description: 'Chicago Manual of Style',
    icon: '📖'
  }
]

export default function TemplateSelectPage({ fileId }) {
  const navigate = useNavigate()
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSelect = (templateId) => {
    setSelectedTemplate(templateId)
  }

  const handleConfirm = () => {
    if (!selectedTemplate) return
    setLoading(true)
    // Simulate template application
    setTimeout(() => {
      navigate('/download', { state: { template: selectedTemplate } })
    }, 1500)
  }

  return (
    <div className="template-page">
      <h1>Select Template</h1>
      <p className="subtitle">Choose the formatting style for your paper</p>
      
      <div className="template-grid">
        {TEMPLATES.map(template => (
          <TemplateCard
            key={template.id}
            template={template}
            selected={selectedTemplate === template.id}
            onSelect={handleSelect}
          />
        ))}
      </div>

      <div className="button-group">
        <button
          className="btn-secondary"
          onClick={() => navigate('/analysis')}
        >
          Back
        </button>
        <button
          className="btn-primary"
          onClick={handleConfirm}
          disabled={!selectedTemplate || loading}
        >
          {loading ? 'Formatting...' : 'Format & Download'}
        </button>
      </div>
    </div>
  )
}
