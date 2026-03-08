import { Routes, Route } from 'react-router-dom'
import LandingPage from "./../pages/LandingPage";
import UploadPage from "./../pages/UploadPage";
import './App.css'

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/upload" element={<UploadPage />} />
      </Routes>
    </>
  )
}

export default App  
