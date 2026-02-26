import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ProgressBar from '../components/ProgressBar'
import { processDocument } from '../services/api'
import { getProgressStages } from '../utils/progressSimulator'
import '../styles/pages.css'

export default function AnalysisPage({ fileId }) {
  const navigate = useNavigate()
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState('Initializing...')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!fileId) {
      navigate('/')
      return
    }

    const processFile = async () => {
      try {
        // Simulate progress stages
        const stages = getProgressStages()
        for (let stage of stages) {
          setProgress(stage.progress)
          setCurrentStage(stage.label)
          await new Promise(resolve => setTimeout(resolve, stage.duration))
        }

        // Call backend to process
        await processDocument(fileId)
        
        // Navigate to template selection
        setTimeout(() => {
          navigate('/template')
        }, 500)
      } catch (err) {
        setError(err.message)
      }
    }

    processFile()
  }, [fileId, navigate])

  return (
    <div className="analysis-page">
      <h1>Analyzing Your Document</h1>
      <ProgressBar progress={progress} label={currentStage} />
      {error && <div className="error-message">{error}</div>}
      <p className="info-text">Please wait while we parse your document structure...</p>
    </div>
  )
}
