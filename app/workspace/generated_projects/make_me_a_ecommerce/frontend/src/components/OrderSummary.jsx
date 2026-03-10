import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OrderSummary.css';

const OrderSummary = ({ orderId }) => {
  const [order, setOrder] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchOrder = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/orders/${orderId}`);
        setOrder(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchOrder();
  }, [orderId]);

  if (isLoading) {
    return <div className="order-summary">Loading...</div>;
  }

  if (error) {
    return <div className="order-summary">Error: {error}</div>;
  }

  return (
    <div className="order-summary">
      <h2>Order Summary</h2>
      <p>Order ID: {order.id}</p>
      <p>Order Date: {order.date}</p>
      <p>Total: ${order.total}</p>
      <h3>Products:</h3>
      <ul>
        {order.products && order.products.map((product) => (
          <li key={product.id}>
            <span>{product.name}</span>
            <span> x {product.quantity}</span>
            <span> = ${product.price * product.quantity}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default OrderSummary;