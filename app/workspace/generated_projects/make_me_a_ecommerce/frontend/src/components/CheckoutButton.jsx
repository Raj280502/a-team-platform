import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const CheckoutButton = ({ cartId, productId, quantity }) => {
  const [isDisabled, setIsDisabled] = useState(false);
  const [error, setError] = useState(null);

  const handleCheckout = async () => {
    try {
      setIsDisabled(true);
      const response = await axios.post(`http://localhost:5000/api/orders`, {
        cartId,
        productId,
        quantity,
      });
      if (response.status === 201) {
        window.location.href = '/api/orders';
      } else {
        throw new Error('Failed to create order');
      }
    } catch (error) {
      setError(error.message);
      setIsDisabled(false);
    }
  };

  return (
    <div style={{ textAlign: 'center' }}>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button
        className="btn btn-primary"
        style={{ padding: '10px 20px', fontSize: '16px' }}
        disabled={isDisabled}
        onClick={handleCheckout}
      >
        Proceed to Checkout
      </button>
    </div>
  );
};

export default CheckoutButton;