import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import styles from './UploadForm.module.css';

const UploadForm = ({ onUpload, isUploading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  const handleFile = (file) => {
    if (!file) return;
    
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      setError('Invalid file type. Please upload image or video.');
      return;
    }

    if (file.size > 100 * 1024 * 1024) { // 100MB limit
      setError('File size exceeds 100MB limit');
      return;
    }

    setError('');
    onUpload(file);
  };

  return (
    <div 
      className={`${styles.uploadContainer} ${dragActive ? styles.dragActive : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <form onSubmit={(e) => e.preventDefault()} className={styles.form}>
        <input
          id="file-input"
          type="file"
          onChange={handleFileSelect}
          accept="image/*, video/*"
          className={styles.input}
          disabled={isUploading}
        />
        <label htmlFor="file-input" className={styles.dropZone}>
          <div className={styles.uploadText}>
            {dragActive ? 'Drop files here' : 'Drag & drop or click to upload'}
          </div>
          <button 
            type="button" 
            className={styles.button} 
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <span className={styles.spinner} />
                Processing...
              </>
            ) : 'Analyze'}
          </button>
        </label>
        {error && <div className={styles.error}>{error}</div>}
      </form>
    </div>
  );
};

UploadForm.propTypes = {
  onUpload: PropTypes.func.isRequired,
  isUploading: PropTypes.bool.isRequired
};

export default UploadForm;