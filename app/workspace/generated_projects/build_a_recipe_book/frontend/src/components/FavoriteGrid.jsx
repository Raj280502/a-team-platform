import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './FavoriteGrid.css';

const FavoriteGrid = ({ userId }) => {
  const [favoriteRecipes, setFavoriteRecipes] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFavoriteRecipes = async () => {
      try {
        const response = await axios.get(`/api/recipes/favorites`, {
          params: { userId },
        });
        setFavoriteRecipes(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchFavoriteRecipes();
  }, [userId]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="favorite-grid">
      {favoriteRecipes.map((recipe) => (
        <div key={recipe.id} className="recipe-card">
          <img src={recipe.image} alt={recipe.name} className="recipe-image" />
          <h2 className="recipe-name">{recipe.name}</h2>
          <p className="recipe-description">{recipe.description}</p>
        </div>
      ))}
    </div>
  );
};

export default FavoriteGrid;