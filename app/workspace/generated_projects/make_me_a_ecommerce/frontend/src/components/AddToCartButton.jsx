import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AddToCartButton = ({ productId, userId, quantity = 1 }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [added, setAdded] = useState(false);

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:5000/api/cart`, {
        userId,
        productId,
        quantity,
      });
      if (response.status === 201) {
        setAdded(true);
      } else {
        throw new Error('Failed to add to cart');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
      {loading ? (
        <button className="btn btn-primary" disabled>Loading...</button>
      ) : added ? (
        <button className="btn btn-success" disabled>Added to Cart</button>
      ) : (
        <button className="btn btn-primary" onClick={handleAddToCart}>
          Add to Cart
        </button>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default AddToCartButton;