import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './ResumeUploadForm.css';

const ResumeUploadForm = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('resume', selectedFile);

    try {
      const response = await axios.post('/api/resumes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 201) {
        onUploadSuccess(response.data);
      } else {
        setError('Failed to upload resume');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setError(error.response.data.message);
      } else {
        setError('An error occurred while uploading the resume');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="resume-upload-form">
      <h2>Upload Resume</h2>
      <input
        type="file"
        accept=".pdf, .docx, .doc"
        onChange={handleFileChange}
        disabled={uploading}
      />
      {error && <p className="error-message">{error}</p>}
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload Resume'}
      </button>
    </div>
  );
};

export default ResumeUploadForm;