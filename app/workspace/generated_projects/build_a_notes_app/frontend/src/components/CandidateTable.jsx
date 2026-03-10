import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const CandidateTable = ({ jobPostingId }) => {
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCandidates = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/candidate-search?jobPostingId=${jobPostingId}`);
        setCandidates(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, [jobPostingId]);

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
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Name</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Email</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Phone</th>
          <th style={{ border: '1px solid #ddd', padding: '10px' }}>Match Score</th>
        </tr>
      </thead>
      <tbody>
        {candidates.map((candidate) => (
          <tr key={candidate.id}>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{candidate.name}</td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{candidate.email}</td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{candidate.phone}</td>
            <td style={{ border: '1px solid #ddd', padding: '10px' }}>{candidate.matchScore}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default CandidateTable;