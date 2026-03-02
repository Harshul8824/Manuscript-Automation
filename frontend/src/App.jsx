import { useState } from 'react'
import LandingPage from "./../pages/LandingPage";
import { Routes, Route } from 'react-router-dom'
import './App.css'

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
      </Routes>
    </>
  )
}

export default App  
