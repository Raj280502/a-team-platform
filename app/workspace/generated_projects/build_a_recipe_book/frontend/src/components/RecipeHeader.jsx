import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './RecipeHeader.css';

const RecipeHeader = (props) => {
  const [recipe, setRecipe] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const response = await axios.get(`/api/recipes/${props.recipeId}`);
        setRecipe(response.data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };
    fetchRecipe();
  }, [props.recipeId]);

  if (loading) {
    return <div className="recipe-header" style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div className="recipe-header" style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div className="recipe-header">
      <h1>{recipe.title}</h1>
      <img src={recipe.image} alt={recipe.title} style={{ width: '100%', height: '200px', objectFit: 'cover' }} />
    </div>
  );
};

export default RecipeHeader;