import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UpdateQuantityButton = ({ productId, quantity, cartId, updateCart }) => {
  const [newQuantity, setNewQuantity] = useState(quantity);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpdateQuantity = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.patch(`http://localhost:5000/api/cart/${cartId}`, {
        productId: productId,
        quantity: newQuantity,
      });
      updateCart(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIncrement = () => {
    setNewQuantity(newQuantity + 1);
  };

  const handleDecrement = () => {
    if (newQuantity > 1) {
      setNewQuantity(newQuantity - 1);
    }
  };

  return (
    <div className="update-quantity-button">
      <button
        style={{
          marginRight: '10px',
          padding: '5px 10px',
          border: 'none',
          borderRadius: '5px',
          backgroundColor: '#4CAF50',
          color: '#fff',
          cursor: 'pointer',
        }}
        onClick={handleDecrement}
      >
        -
      </button>
      <input
        type="number"
        value={newQuantity}
        onChange={(e) => setNewQuantity(parseInt(e.target.value))}
        style={{
          width: '50px',
          padding: '5px',
          border: '1px solid #ccc',
          borderRadius: '5px',
        }}
      />
      <button
        style={{
          marginLeft: '10px',
          padding: '5px 10px',
          border: 'none',
          borderRadius: '5px',
          backgroundColor: '#4CAF50',
          color: '#fff',
          cursor: 'pointer',
        }}
        onClick={handleIncrement}
      >
        +
      </button>
      <button
        style={{
          marginLeft: '20px',
          padding: '5px 10px',
          border: 'none',
          borderRadius: '5px',
          backgroundColor: '#4CAF50',
          color: '#fff',
          cursor: 'pointer',
        }}
        onClick={handleUpdateQuantity}
        disabled={isLoading}
      >
        {isLoading ? 'Updating...' : 'Update Quantity'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default UpdateQuantityButton;