import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OrderHistory.css';

const OrderHistory = ({ userId }) => {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/orders?customerId=${userId}`);
        setOrders(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [userId]);

  if (loading) {
    return <div className="order-history-loading">Loading...</div>;
  }

  if (error) {
    return <div className="order-history-error">Error: {error}</div>;
  }

  return (
    <div className="order-history">
      <h2>Order History</h2>
      {orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        <ul>
          {orders.map((order) => (
            <li key={order.id}>
              <div className="order-summary">
                <h3>Order {order.id}</h3>
                <p>Date: {order.date}</p>
                <p>Total: ${order.total}</p>
                <p>Status: {order.status}</p>
              </div>
              <ul className="order-items">
                {order.items.map((item) => (
                  <li key={item.id}>
                    <div className="order-item">
                      <p>Product: {item.productName}</p>
                      <p>Quantity: {item.quantity}</p>
                      <p>Price: ${item.price}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OrderHistory;