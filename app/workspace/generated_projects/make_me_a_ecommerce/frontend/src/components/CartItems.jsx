import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CartItems.css';

const CartItems = ({ cart, handleRemoveItem, handleUpdateQuantity }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const responses = await Promise.all(cart.map(async (item) => {
          const response = await axios.get(`http://localhost:5000/api/products/${item.productId}`);
          return response.data;
        }));
        setProducts(responses);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [cart]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="cart-items">
      {products.map((product, index) => (
        <div key={product.id} className="cart-item">
          <img src={product.image} alt={product.name} className="cart-item-image" />
          <div className="cart-item-info">
            <h2 className="cart-item-name">{product.name}</h2>
            <p className="cart-item-price">${product.price}</p>
            <p className="cart-item-quantity">Quantity: {cart.find((item) => item.productId === product.id).quantity}</p>
            <button className="update-quantity-button" onClick={() => handleUpdateQuantity(product.id, cart.find((item) => item.productId === product.id).quantity + 1)}>+</button>
            <button className="update-quantity-button" onClick={() => handleUpdateQuantity(product.id, cart.find((item) => item.productId === product.id).quantity - 1)}>-</button>
            <button className="remove-item-button" onClick={() => handleRemoveItem(product.id)}>Remove</button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CartItems;