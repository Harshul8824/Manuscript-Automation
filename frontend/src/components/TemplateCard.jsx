import '../styles/components.css'

export default function TemplateCard({ template, selected, onSelect }) {
  return (
    <div
      className={`template-card ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(template.id)}
    >
      <div className="template-icon">{template.icon}</div>
      <h3>{template.name}</h3>
      <p>{template.description}</p>
      {selected && <div className="checkmark">✓</div>}
    </div>
  )
}
