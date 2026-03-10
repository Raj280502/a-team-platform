import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './ResumeParser.css';

const ResumeParser = ({ resumeId }) => {
  const [resume, setResume] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchResume = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/resumes/${resumeId}`);
      setResume(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeResume = async () => {
    try {
      const response = await axios.post('/api/resume-analysis', resume);
      console.log(response.data);
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchResume();
    }
  }, [resumeId]);

  if (isLoading) {
    return <div className="loader">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="resume-parser">
      <h2>Resume Information</h2>
      <p><strong>Name:</strong> {resume.name}</p>
      <p><strong>Email:</strong> {resume.email}</p>
      <p><strong>Phone:</strong> {resume.phone}</p>
      <p><strong>Summary:</strong> {resume.summary}</p>
      <button className="analyze-button" onClick={analyzeResume}>Analyze Resume</button>
    </div>
  );
};

export default ResumeParser;