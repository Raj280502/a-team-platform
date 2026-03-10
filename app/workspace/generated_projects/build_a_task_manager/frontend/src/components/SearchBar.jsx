import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SearchBar.css';

const SearchBar = (props) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.get('http://localhost:5000/api/tasks/search', {
        params: { query: searchTerm }
      });
      setSearchResults(response.data);
    } catch (error) {
      setError(error.message);
    }
  };

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="Search tasks by title, description, or category"
          className="search-input"
        />
        <button type="submit" className="search-button">Search</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      {searchResults.length > 0 && (
        <ul className="search-results">
          {searchResults.map((task) => (
            <li key={task.id}>
              <h3>{task.title}</h3>
              <p>{task.description}</p>
              <p>Category: {task.category}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchBar;