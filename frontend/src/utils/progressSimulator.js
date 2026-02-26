// Frontend progress stages for the analysis page
// Simulates processing steps while backend is working

export const getProgressStages = () => {
  return [
    { progress: 10, label: 'Parsing document structure...', duration: 800 },
    { progress: 25, label: 'Extracting content...', duration: 1000 },
    { progress: 40, label: 'Classifying sections...', duration: 1200 },
    { progress: 60, label: 'Analyzing metadata...', duration: 900 },
    { progress: 75, label: 'Processing references...', duration: 1100 },
    { progress: 90, label: 'Finalizing analysis...', duration: 700 },
    { progress: 100, label: 'Complete!', duration: 500 },
  ]
}
