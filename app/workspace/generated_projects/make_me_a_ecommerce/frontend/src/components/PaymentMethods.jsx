import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PaymentMethods.css';

const PaymentMethods = ({ customerId }) => {
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchPaymentMethods = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/customers/${customerId}/payment-methods`);
        setPaymentMethods(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPaymentMethods();
  }, [customerId]);

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="payment-methods">
      <h2>Saved Payment Methods</h2>
      <ul>
        {paymentMethods.map((method, index) => (
          <li key={index}>
            <span>{method.cardType}</span>
            <span>{method.cardNumber}</span>
            <span>{method.expirationDate}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PaymentMethods;