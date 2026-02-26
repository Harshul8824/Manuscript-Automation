import axios from 'axios'

const API_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Upload a document
export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// Process the document
export const processDocument = async (fileId) => {
  return api.get(`/api/process/${fileId}`)
}

// Download formatted document
export const downloadDocument = async (fileId, template) => {
  const response = await api.get(`/api/download/${fileId}`, {
    params: { template },
    responseType: 'blob',
  })
  
  // Trigger download
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `formatted_${template}_${fileId}.docx`)
  document.body.appendChild(link)
  link.click()
  link.parentNode.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export default api
