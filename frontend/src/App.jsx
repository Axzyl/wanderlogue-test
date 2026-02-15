import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from '@clerk/clerk-react'
import { useState, useEffect } from 'react'
import PhotoUpload from './components/PhotoUpload'
import AnalysisOutput from './components/AnalysisOutput'
import Gallery from './components/Gallery'

const API_URL = import.meta.env.VITE_API_URL || ''

function App() {
  const { getToken } = useAuth()
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadedPhotos, setUploadedPhotos] = useState([])
  const [analysisResults, setAnalysisResults] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [galleryPhotos, setGalleryPhotos] = useState([])

  // Fetch gallery photos on mount
  useEffect(() => {
    if (activeTab === 'gallery') {
      fetchGalleryPhotos()
    }
  }, [activeTab])

  const fetchGalleryPhotos = async () => {
    try {
      const token = await getToken()
      const response = await fetch(`${API_URL}/api/photos/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setGalleryPhotos(data.photos)
      }
    } catch (err) {
      console.error('Failed to fetch gallery:', err)
    }
  }

  const handleUpload = async (files, context) => {
    setError(null)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    if (context) {
      formData.append('context', context)
    }

    try {
      const token = await getToken()
      const response = await fetch(`${API_URL}/api/photos/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      setUploadedPhotos(data.photos)
      return data.photos
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  const handleAnalyze = async (photos, context) => {
    setIsAnalyzing(true)
    setError(null)
    setAnalysisResults([])

    try {
      const token = await getToken()
      const results = []

      for (const photo of photos) {
        const response = await fetch(`${API_URL}/api/photos/${photo.id}/analyze`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ context }),
        })

        if (response.ok) {
          const analysis = await response.json()
          results.push({
            photo,
            analysis,
          })
          // Update results incrementally
          setAnalysisResults([...results])
        }
      }

      setActiveTab('results')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleGalleryItemClick = (photo) => {
    if (photo.analysis) {
      setAnalysisResults([{ photo, analysis: photo.analysis }])
      setActiveTab('results')
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📸 Photo Memory</h1>
        <div className="header-right">
          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </div>
      </header>

      <main className="main-content">
        <SignedOut>
          <div className="auth-container">
            <h2>Welcome to Photo Memory</h2>
            <p>
              Upload your travel photos and discover where they were taken, along with fascinating historical context.
            </p>
            <SignInButton mode="modal">
              <button className="btn btn-primary">Sign In to Get Started</button>
            </SignInButton>
          </div>
        </SignedOut>

        <SignedIn>
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              Upload & Analyze
            </button>
            <button
              className={`tab ${activeTab === 'results' ? 'active' : ''}`}
              onClick={() => setActiveTab('results')}
              disabled={analysisResults.length === 0}
            >
              Results
            </button>
            <button
              className={`tab ${activeTab === 'gallery' ? 'active' : ''}`}
              onClick={() => setActiveTab('gallery')}
            >
              Gallery
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}

          {activeTab === 'upload' && (
            <PhotoUpload
              onUpload={handleUpload}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              uploadedPhotos={uploadedPhotos}
              setUploadedPhotos={setUploadedPhotos}
            />
          )}

          {activeTab === 'results' && (
            <AnalysisOutput results={analysisResults} isLoading={isAnalyzing} />
          )}

          {activeTab === 'gallery' && (
            <Gallery photos={galleryPhotos} onItemClick={handleGalleryItemClick} />
          )}
        </SignedIn>
      </main>
    </div>
  )
}

export default App
