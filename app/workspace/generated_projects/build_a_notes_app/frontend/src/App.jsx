import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './App.css';
import JobPostingList from './components/JobPostingList';
import ResumeUploadForm from './components/ResumeUploadForm';
import MatchScoreChart from './components/MatchScoreChart';
import JobPostingTable from './components/JobPostingTable';
import JobPostingForm from './components/JobPostingForm';
import ResumeParser from './components/ResumeParser';
import ResumeSummary from './components/ResumeSummary';
import SkillMatrix from './components/SkillMatrix';
import SearchBar from './components/SearchBar';
import CandidateTable from './components/CandidateTable';
import FilterBar from './components/FilterBar';

function App() {
  const [jobPostings, setJobPostings] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [jobPostingForm, setJobPostingForm] = useState({
    title: '',
    description: '',
    keywords: '',
  });
  const [resumeForm, setResumeForm] = useState({
    file: null,
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    skills: [],
    experience: '',
  });

  useEffect(() => {
    axios.get('/api/job-postings')
      .then(response => {
        setJobPostings(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  useEffect(() => {
    axios.get('/api/resumes')
      .then(response => {
        setResumes(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  useEffect(() => {
    axios.get('/api/candidates')
      .then(response => {
        setCandidates(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  const handleJobPostingFormSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    axios.post('/api/job-postings', jobPostingForm)
      .then(response => {
        setJobPostings([...jobPostings, response.data]);
        setSuccess('Job posting created successfully!');
        setJobPostingForm({
          title: '',
          description: '',
          keywords: '',
        });
      })
      .catch(error => {
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleResumeFormSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    const formData = new FormData();
    formData.append('file', resumeForm.file);
    axios.post('/api/resumes', formData)
      .then(response => {
        setResumes([...resumes, response.data]);
        setSuccess('Resume uploaded successfully!');
        setResumeForm({
          file: null,
        });
      })
      .catch(error => {
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleSearchQueryChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleFiltersChange = (event) => {
    setFilters({
      ...filters,
      [event.target.name]: event.target.value,
    });
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>AI-Powered Resume Analyzer</h1>
      </header>
      <main className="main">
        <nav className="nav">
          <ul>
            <li>
              <button
                className={activeTab === 'dashboard' ? 'active' : ''}
                onClick={() => handleTabChange('dashboard')}
              >
                Dashboard
              </button>
            </li>
            <li>
              <button
                className={activeTab === 'job-postings' ? 'active' : ''}
                onClick={() => handleTabChange('job-postings')}
              >
                Job Postings
              </button>
            </li>
            <li>
              <button
                className={activeTab === 'resume-upload' ? 'active' : ''}
                onClick={() => handleTabChange('resume-upload')}
              >
                Resume Upload
              </button>
            </li>
            <li>
              <button
                className={activeTab === 'resume-analysis' ? 'active' : ''}
                onClick={() => handleTabChange('resume-analysis')}
              >
                Resume Analysis
              </button>
            </li>
            <li>
              <button
                className={activeTab === 'candidate-search' ? 'active' : ''}
                onClick={() => handleTabChange('candidate-search')}
              >
                Candidate Search
              </button>
            </li>
          </ul>
        </nav>
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <JobPostingList jobPostings={jobPostings} />
            <ResumeUploadForm
              resumeForm={resumeForm}
              handleResumeFormSubmit={handleResumeFormSubmit}
              handleResumeFormChange={(event) => setResumeForm({ ...resumeForm, file: event.target.files[0] })}
            />
            <MatchScoreChart />
          </div>
        )}
        {activeTab === 'job-postings' && (
          <div className="job-postings">
            <JobPostingTable jobPostings={jobPostings} />
            <JobPostingForm
              jobPostingForm={jobPostingForm}
              handleJobPostingFormSubmit={handleJobPostingFormSubmit}
              handleJobPostingFormChange={(event) => setJobPostingForm({ ...jobPostingForm, [event.target.name]: event.target.value })}
            />
          </div>
        )}
        {activeTab === 'resume-upload' && (
          <div className="resume-upload">
            <ResumeUploadForm
              resumeForm={resumeForm}
              handleResumeFormSubmit={handleResumeFormSubmit}
              handleResumeFormChange={(event) => setResumeForm({ ...resumeForm, file: event.target.files[0] })}
            />
            <ResumeParser resumes={resumes} />
          </div>
        )}
        {activeTab === 'resume-analysis' && (
          <div className="resume-analysis">
            <ResumeSummary resumes={resumes} />
            <MatchScoreChart />
            <SkillMatrix resumes={resumes} />
          </div>
        )}
        {activeTab === 'candidate-search' && (
          <div className="candidate-search">
            <SearchBar
              searchQuery={searchQuery}
              handleSearchQueryChange={handleSearchQueryChange}
            />
            <CandidateTable candidates={candidates} filters={filters} />
            <FilterBar
              filters={filters}
              handleFiltersChange={handleFiltersChange}
            />
          </div>
        )}
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {success && <p style={{ color: 'green' }}>{success}</p>}
      </main>
    </div>
  );
}

export default App;