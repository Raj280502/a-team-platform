import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './JobPostingList.css';

const JobPostingList = ({ jobPostings }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobPostingsList, setJobPostingsList] = useState([]);

  useEffect(() => {
    const fetchJobPostings = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/job-postings');
        setJobPostingsList(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchJobPostings();
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="job-posting-list">
      <h2>Job Postings</h2>
      <ul>
        {jobPostingsList.map((jobPosting) => (
          <li key={jobPosting.id}>
            <h3>{jobPosting.title}</h3>
            <p>{jobPosting.description}</p>
            <p>Keywords: {jobPosting.keywords.join(', ')}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default JobPostingList;