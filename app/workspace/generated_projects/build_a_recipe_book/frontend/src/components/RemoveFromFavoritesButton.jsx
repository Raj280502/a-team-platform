import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found

const RemoveFromFavoritesButton = ({ recipeId, handleRemoveFromFavorites }) => {
  const [isRemoving, setIsRemoving] = useState(false);
  const [error, setError] = useState(null);

  const removeFromFavorites = async () => {
    setIsRemoving(true);
    try {
      await axios.delete(`/api/recipes/${recipeId}/favorite`);
      handleRemoveFromFavorites();
    } catch (error) {
      setError(error.message);
    } finally {
      setIsRemoving(false);
    }
  };

  return (
    <button
      className="remove-from-favorites-button"
      style={{
        backgroundColor: '#ff0000',
        color: '#ffffff',
        border: 'none',
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
      }}
      onClick={removeFromFavorites}
      disabled={isRemoving}
    >
      {isRemoving ? 'Removing...' : 'Remove from Favorites'}
      {error && <span style={{ color: '#ff0000' }}>{error}</span>}
    </button>
  );
};

export default RemoveFromFavoritesButton;