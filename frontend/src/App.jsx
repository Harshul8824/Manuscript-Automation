import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import UploadPage from './pages/UploadPage'
import AnalysisPage from './pages/AnalysisPage'
import TemplateSelectPage from './pages/TemplateSelectPage'
import DownloadPage from './pages/DownloadPage'
import './App.css'

function App() {
  const [fileId, setFileId] = useState(null)
  const [fileName, setFileName] = useState(null)

  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<UploadPage onUpload={(id, name) => { setFileId(id); setFileName(name); }} />} />
            <Route path="/analysis" element={<AnalysisPage fileId={fileId} />} />
            <Route path="/template" element={<TemplateSelectPage fileId={fileId} />} />
            <Route path="/download" element={<DownloadPage fileId={fileId} fileName={fileName} />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
