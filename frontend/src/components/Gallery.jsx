function Gallery({ photos, onItemClick }) {
  if (photos.length === 0) {
    return (
      <div className="gallery-section">
        <h2>🖼️ Your Photo Gallery</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
          No photos yet. Upload and analyze some photos to build your gallery.
        </p>
      </div>
    )
  }

  return (
    <div className="gallery-section">
      <h2>🖼️ Your Photo Gallery</h2>
      <div className="gallery-grid">
        {photos.map((photo) => (
          <div
            key={photo.id}
            className="gallery-item"
            onClick={() => onItemClick(photo)}
          >
            <img src={photo.storage_url} alt={photo.original_filename} />
            <div className="gallery-item-content">
              <h4>{photo.original_filename}</h4>
              {photo.analysis ? (
                <p>{photo.analysis.location_info?.substring(0, 100)}...</p>
              ) : (
                <p style={{ fontStyle: 'italic' }}>Not analyzed yet</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Gallery
