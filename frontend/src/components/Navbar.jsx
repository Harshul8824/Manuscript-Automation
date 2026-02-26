import { Link } from 'react-router-dom'
import '../styles/components.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          ✨ ManuscriptMagic
        </Link>
        <div className="navbar-menu">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          <a href="#about">About</a>
        </div>
      </div>
    </nav>
  )
}
