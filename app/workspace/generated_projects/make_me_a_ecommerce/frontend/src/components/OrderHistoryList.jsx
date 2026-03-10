import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './OrderHistoryList.css';

const OrderHistoryList = ({ userId }) => {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/orders?userId=${userId}`);
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
    return <div className="order-history-list-loading">Loading...</div>;
  }

  if (error) {
    return <div className="order-history-list-error">{error}</div>;
  }

  return (
    <div className="order-history-list">
      <h2>Order History</h2>
      {orders.length === 0 ? (
        <p>No orders found.</p>
      ) : (
        <ul>
          {orders.map((order) => (
            <li key={order.id}>
              <div className="order-summary">
                <p>Order ID: {order.id}</p>
                <p>Order Date: {order.date}</p>
                <p>Total: ${order.total}</p>
                <p>Status: {order.status}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OrderHistoryList;