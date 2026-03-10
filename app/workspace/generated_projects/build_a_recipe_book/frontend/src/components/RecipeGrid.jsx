import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './RecipeGrid.css';

const RecipeGrid = ({ searchQuery }) => {
  const [recipes, setRecipes] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecipes = async () => {
      setLoading(true);
      try {
        let url = '/api/recipes';
        if (searchQuery) {
          url = `/api/recipes/search?q=${searchQuery}`;
        }
        const response = await axios.get(url);
        setRecipes(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRecipes();
  }, [searchQuery]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="recipe-grid">
      {recipes.map((recipe) => (
        <div key={recipe.id} className="recipe-card">
          <h2 className="recipe-title">{recipe.title}</h2>
          <img src={recipe.image} alt={recipe.title} className="recipe-image" />
          <p className="recipe-description">{recipe.description}</p>
          <button className="favorite-button">Favorite</button>
        </div>
      ))}
    </div>
  );
};

export default RecipeGrid;