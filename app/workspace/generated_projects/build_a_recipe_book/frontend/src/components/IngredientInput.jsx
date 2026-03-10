import React, { useState } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './IngredientInput.css';

const IngredientInput = ({ handleAddIngredient, recipeId }) => {
  const [ingredient, setIngredient] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (!ingredient) {
        setError('Please enter an ingredient');
        return;
      }
      const response = await axios.post(`/api/recipes/${recipeId}/ingredients`, { name: ingredient });
      handleAddIngredient(response.data);
      setIngredient('');
      setError(null);
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div className="ingredient-input">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={ingredient}
          onChange={(e) => setIngredient(e.target.value)}
          placeholder="Enter ingredient"
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
        />
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" style={{ padding: '10px 20px', fontSize: '16px' }}>Add Ingredient</button>
      </form>
    </div>
  );
};

export default IngredientInput;