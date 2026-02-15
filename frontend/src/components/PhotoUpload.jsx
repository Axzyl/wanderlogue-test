import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

function PhotoUpload({ onUpload, onAnalyze, isAnalyzing, uploadedPhotos, setUploadedPhotos }) {
  const [previewFiles, setPreviewFiles] = useState([])
  const [context, setContext] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles) => {
    const filesWithPreview = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }))
    setPreviewFiles((prev) => [...prev, ...filesWithPreview])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.gif'],
    },
    multiple: true,
  })

  const removeFile = (index) => {
    setPreviewFiles((prev) => {
      const newFiles = [...prev]
      URL.revokeObjectURL(newFiles[index].preview)
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  const handleUploadAndAnalyze = async () => {
    if (previewFiles.length === 0) return

    setIsUploading(true)
    try {
      const files = previewFiles.map((p) => p.file)
      const photos = await onUpload(files, context)
      await onAnalyze(photos, context)

      // Clear previews after successful analysis
      previewFiles.forEach((p) => URL.revokeObjectURL(p.preview))
      setPreviewFiles([])
      setContext('')
    } catch (err) {
      console.error('Upload/analyze failed:', err)
    } finally {
      setIsUploading(false)
    }
  }

  const handleClear = () => {
    previewFiles.forEach((p) => URL.revokeObjectURL(p.preview))
    setPreviewFiles([])
    setUploadedPhotos([])
    setContext('')
  }

  const isLoading = isUploading || isAnalyzing

  return (
    <div className="upload-section">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-icon">📷</div>
        <h3>Upload Your Travel Photos</h3>
        <p>
          {isDragActive
            ? 'Drop the photos here...'
            : 'Drag & drop photos here, or click to select'}
        </p>
        <p>Supports: JPEG, PNG, WebP, GIF</p>
      </div>

      {previewFiles.length > 0 && (
        <div className="preview-grid">
          {previewFiles.map((file, index) => (
            <div key={index} className="preview-item">
              <img src={file.preview} alt={`Preview ${index + 1}`} />
              <button
                className="remove-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  removeFile(index)
                }}
                disabled={isLoading}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="context-input">
        <label htmlFor="context">Additional Context (Optional)</label>
        <textarea
          id="context"
          placeholder="e.g., This was during our trip to Italy in summer 2022..."
          value={context}
          onChange={(e) => setContext(e.target.value)}
          disabled={isLoading}
        />
      </div>

      <div className="action-buttons">
        <button
          className="btn btn-primary"
          onClick={handleUploadAndAnalyze}
          disabled={previewFiles.length === 0 || isLoading}
        >
          {isLoading ? 'Analyzing...' : `Analyze ${previewFiles.length} Photo${previewFiles.length !== 1 ? 's' : ''}`}
        </button>
        <button
          className="btn btn-secondary"
          onClick={handleClear}
          disabled={previewFiles.length === 0 || isLoading}
        >
          Clear
        </button>
      </div>
    </div>
  )
}

export default PhotoUpload
