import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const ResumeSummary = ({ resumeId }) => {
  const [resume, setResume] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResume = async () => {
      try {
        const response = await axios.get(`/api/resumes/${resumeId}`);
        setResume(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchResume();
  }, [resumeId]);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div className="resume-summary">
      <h2>{resume.name}</h2>
      <p>{resume.summary}</p>
      <ul>
        {resume.skills.map((skill, index) => (
          <li key={index}>{skill}</li>
        ))}
      </ul>
      <p>
        <strong>Experience:</strong> {resume.experience} years
      </p>
      <p>
        <strong>Education:</strong> {resume.education}
      </p>
    </div>
  );
};

export default ResumeSummary;