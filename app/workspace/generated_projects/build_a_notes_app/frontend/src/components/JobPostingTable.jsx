import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const JobPostingTable = () => {
  const [jobPostings, setJobPostings] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobPostings = async () => {
      try {
        const response = await axios.get('/api/job-postings');
        setJobPostings(response.data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };
    fetchJobPostings();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Job Title</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Company</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Keywords</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Details</th>
        </tr>
      </thead>
      <tbody>
        {jobPostings.map((jobPosting) => (
          <tr key={jobPosting.id}>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{jobPosting.title}</td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{jobPosting.company}</td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>
              {jobPosting.keywords.join(', ')}
            </td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{jobPosting.details}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default JobPostingTable;