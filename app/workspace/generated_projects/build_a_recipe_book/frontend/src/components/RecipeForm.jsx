import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './RecipeForm.css';

const RecipeForm = (props) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [ingredients, setIngredients] = useState('');
  const [instructions, setInstructions] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/api/recipes', {
        title,
        description,
        ingredients,
        instructions,
      });
      setSuccess('Recipe added successfully!');
      setTitle('');
      setDescription('');
      setIngredients('');
      setInstructions('');
    } catch (error) {
      setError('Failed to add recipe. Please try again.');
    }
  };

  return (
    <div className="recipe-form-container">
      <h2>Add New Recipe</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
      <form onSubmit={handleSubmit}>
        <label>Title:</label>
        <input
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Enter recipe title"
          required
        />
        <br />
        <label>Description:</label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Enter recipe description"
          required
        />
        <br />
        <label>Ingredients:</label>
        <textarea
          value={ingredients}
          onChange={(event) => setIngredients(event.target.value)}
          placeholder="Enter recipe ingredients"
          required
        />
        <br />
        <label>Instructions:</label>
        <textarea
          value={instructions}
          onChange={(event) => setInstructions(event.target.value)}
          placeholder="Enter recipe instructions"
          required
        />
        <br />
        <button type="submit">Add Recipe</button>
      </form>
    </div>
  );
};

export default RecipeForm;