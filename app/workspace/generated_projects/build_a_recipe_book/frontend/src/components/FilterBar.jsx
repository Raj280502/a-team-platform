import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './FilterBar.css';

const FilterBar = (props) => {
  const [query, setQuery] = useState('');
  const [diet, setDiet] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [error, setError] = useState(null);
  const [recipes, setRecipes] = useState([]);

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleDietChange = (event) => {
    setDiet(event.target.value);
  };

  const handleCuisineChange = (event) => {
    setCuisine(event.target.value);
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.get('/api/recipes/search', {
        params: {
          query: query,
          diet: diet,
          cuisine: cuisine
        }
      });
      setRecipes(response.data);
      setError(null);
    } catch (error) {
      setError(error.message);
      setRecipes([]);
    }
  };

  return (
    <div className="filter-bar">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={handleQueryChange}
          placeholder="Search recipes"
          className="query-input"
        />
        <select value={diet} onChange={handleDietChange} className="diet-select">
          <option value="">Diet</option>
          <option value="vegetarian">Vegetarian</option>
          <option value="gluten-free">Gluten-free</option>
          <option value="dairy-free">Dairy-free</option>
        </select>
        <select value={cuisine} onChange={handleCuisineChange} className="cuisine-select">
          <option value="">Cuisine</option>
          <option value="italian">Italian</option>
          <option value="mexican">Mexican</option>
          <option value="indian">Indian</option>
        </select>
        <button type="submit" className="search-button">Search</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      {recipes.length > 0 && (
        <ul className="recipes-list">
          {recipes.map((recipe) => (
            <li key={recipe.id} className="recipe-item">
              <h2 className="recipe-title">{recipe.title}</h2>
              <p className="recipe-description">{recipe.description}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default FilterBar;