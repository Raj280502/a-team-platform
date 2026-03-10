import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './IngredientList.css';

const IngredientList = ({ recipeId }) => {
  const [ingredients, setIngredients] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchIngredients = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/recipes/${recipeId}`);
        setIngredients(response.data.ingredients);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchIngredients();
  }, [recipeId]);

  if (loading) {
    return <div className="loading">Loading ingredients...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="ingredient-list">
      <h2>Ingredients:</h2>
      <ul>
        {ingredients.map((ingredient, index) => (
          <li key={index}>{ingredient}</li>
        ))}
      </ul>
    </div>
  );
};

export default IngredientList;