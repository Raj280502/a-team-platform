import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const JobPostingForm = ({ jobPostingId, onFormSubmit }) => {
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobRequirements, setJobRequirements] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (jobPostingId) {
      axios.get(`/api/job-postings/${jobPostingId}`)
        .then(response => {
          const jobPosting = response.data;
          setJobTitle(jobPosting.jobTitle);
          setCompanyName(jobPosting.companyName);
          setJobDescription(jobPosting.jobDescription);
          setJobRequirements(jobPosting.jobRequirements);
        })
        .catch(error => {
          setError(error.message);
        });
    }
  }, [jobPostingId]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    const jobPostingData = {
      jobTitle,
      companyName,
      jobDescription,
      jobRequirements
    };

    if (jobPostingId) {
      axios.put(`/api/job-postings/${jobPostingId}`, jobPostingData)
        .then(response => {
          onFormSubmit(response.data);
          setIsSubmitting(false);
        })
        .catch(error => {
          setError(error.message);
          setIsSubmitting(false);
        });
    } else {
      axios.post('/api/job-postings', jobPostingData)
        .then(response => {
          onFormSubmit(response.data);
          setIsSubmitting(false);
        })
        .catch(error => {
          setError(error.message);
          setIsSubmitting(false);
        });
    }
  };

  return (
    <div style={{ maxWidth: '500px', margin: '40px auto', padding: '20px', border: '1px solid #ddd', borderRadius: '10px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
      <h2 style={{ marginBottom: '20px' }}>{jobPostingId ? 'Update Job Posting' : 'Create Job Posting'}</h2>
      {error && <p style={{ color: 'red', marginBottom: '20px' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px' }}>Job Title:</label>
          <input type="text" value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} style={{ width: '100%', height: '40px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }} />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px' }}>Company Name:</label>
          <input type="text" value={companyName} onChange={(event) => setCompanyName(event.target.value)} style={{ width: '100%', height: '40px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }} />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px' }}>Job Description:</label>
          <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} style={{ width: '100%', height: '100px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }} />
        </div>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '10px' }}>Job Requirements:</label>
          <textarea value={jobRequirements} onChange={(event) => setJobRequirements(event.target.value)} style={{ width: '100%', height: '100px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }} />
        </div>
        <button type="submit" disabled={isSubmitting} style={{ width: '100%', height: '40px', padding: '10px', border: 'none', borderRadius: '5px', backgroundColor: '#4CAF50', color: '#fff', cursor: 'pointer' }}>{isSubmitting ? 'Submitting...' : 'Submit'}</button>
      </form>
    </div>
  );
};

export default JobPostingForm;