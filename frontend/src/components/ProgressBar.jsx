import '../styles/components.css'

export default function ProgressBar({ progress, label }) {
  return (
    <div className="progress-container">
      <div className="progress-bar-wrapper">
        <div className="progress-bar-background">
          <div
            className="progress-bar-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <span className="progress-percentage">{progress}%</span>
      </div>
      {label && <p className="progress-label">{label}</p>}
    </div>
  )
}
