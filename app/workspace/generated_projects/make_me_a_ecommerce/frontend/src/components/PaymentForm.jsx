import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PaymentForm.css';

const PaymentForm = ({ cartId, orderId, userId, handlePaymentSuccess }) => {
  const [cardNumber, setCardNumber] = useState('');
  const [expirationDate, setExpirationDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('credit');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCardNumberChange = (e) => {
    setCardNumber(e.target.value);
  };

  const handleExpirationDateChange = (e) => {
    setExpirationDate(e.target.value);
  };

  const handleCvvChange = (e) => {
    setCvv(e.target.value);
  };

  const handlePaymentMethodChange = (e) => {
    setPaymentMethod(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`http://localhost:5000/api/orders/${orderId}/payment`, {
        cartId,
        paymentMethod,
        cardNumber,
        expirationDate,
        cvv,
      });
      if (response.status === 200) {
        handlePaymentSuccess();
      } else {
        throw new Error('Payment failed');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="payment-form">
      <h2>Payment Information</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Card Number:</label>
          <input
            type="text"
            value={cardNumber}
            onChange={handleCardNumberChange}
            placeholder="1234-1234-1234-1234"
            style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
          />
        </div>
        <div className="form-group">
          <label>Expiration Date:</label>
          <input
            type="text"
            value={expirationDate}
            onChange={handleExpirationDateChange}
            placeholder="MM/YY"
            style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
          />
        </div>
        <div className="form-group">
          <label>CVV:</label>
          <input
            type="text"
            value={cvv}
            onChange={handleCvvChange}
            placeholder="123"
            style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
          />
        </div>
        <div className="form-group">
          <label>Payment Method:</label>
          <select value={paymentMethod} onChange={handlePaymentMethodChange}>
            <option value="credit">Credit Card</option>
            <option value="paypal">PayPal</option>
          </select>
        </div>
        {error && <div style={{ color: 'red' }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ padding: '10px', backgroundColor: '#4CAF50', color: '#fff' }}>
          {loading ? 'Processing...' : 'Make Payment'}
        </button>
      </form>
    </div>
  );
};

export default PaymentForm;