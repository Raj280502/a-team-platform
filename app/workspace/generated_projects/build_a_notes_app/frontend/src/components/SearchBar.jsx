import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const SearchBar = (props) => {
  const [keyword, setKeyword] = useState('');
  const [skills, setSkills] = useState('');
  const [criteria, setCriteria] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/candidate-search', {
        keyword,
        skills,
        criteria,
      });
      setSearchResults(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-bar" style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <h2>Search Candidates</h2>
      <form onSubmit={handleSearch}>
        <div className="form-group" style={{ marginBottom: '10px' }}>
          <label>Keyword:</label>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Enter keyword"
            style={{ padding: '10px', width: '100%' }}
          />
        </div>
        <div className="form-group" style={{ marginBottom: '10px' }}>
          <label>Skills:</label>
          <input
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="Enter skills"
            style={{ padding: '10px', width: '100%' }}
          />
        </div>
        <div className="form-group" style={{ marginBottom: '10px' }}>
          <label>Criteria:</label>
          <input
            type="text"
            value={criteria}
            onChange={(e) => setCriteria(e.target.value)}
            placeholder="Enter criteria"
            style={{ padding: '10px', width: '100%' }}
          />
        </div>
        <button type="submit" disabled={loading} style={{ padding: '10px 20px', backgroundColor: '#4CAF50', color: '#fff', border: 'none', borderRadius: '5px' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {searchResults.length > 0 && (
        <div className="search-results" style={{ marginTop: '20px' }}>
          <h3>Search Results:</h3>
          <ul>
            {searchResults.map((result, index) => (
              <li key={index}>{result.name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default SearchBar;