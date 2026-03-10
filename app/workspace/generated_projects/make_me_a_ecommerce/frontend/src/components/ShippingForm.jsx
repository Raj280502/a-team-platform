import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ShippingForm.css';

const ShippingForm = ({ userId, cartId, onSubmit }) => {
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [zip, setZip] = useState('');
  const [country, setCountry] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/orders', {
        userId,
        cartId,
        shippingAddress: {
          name,
          address,
          city,
          state,
          zip,
          country,
        },
      });
      onSubmit(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="shipping-form">
      <h2>Shipping Information</h2>
      <div className="form-group">
        <label>Name:</label>
        <input
          type="text"
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Full Name"
          required
          className="form-control"
        />
      </div>
      <div className="form-group">
        <label>Address:</label>
        <input
          type="text"
          value={address}
          onChange={(event) => setAddress(event.target.value)}
          placeholder="Street Address"
          required
          className="form-control"
        />
      </div>
      <div className="form-group">
        <label>City:</label>
        <input
          type="text"
          value={city}
          onChange={(event) => setCity(event.target.value)}
          placeholder="City"
          required
          className="form-control"
        />
      </div>
      <div className="form-group">
        <label>State:</label>
        <input
          type="text"
          value={state}
          onChange={(event) => setState(event.target.value)}
          placeholder="State"
          required
          className="form-control"
        />
      </div>
      <div className="form-group">
        <label>Zip:</label>
        <input
          type="text"
          value={zip}
          onChange={(event) => setZip(event.target.value)}
          placeholder="Zip Code"
          required
          className="form-control"
        />
      </div>
      <div className="form-group">
        <label>Country:</label>
        <input
          type="text"
          value={country}
          onChange={(event) => setCountry(event.target.value)}
          placeholder="Country"
          required
          className="form-control"
        />
      </div>
      {error && <div className="error-message">{error}</div>}
      <button type="submit" disabled={loading} className="btn-submit">
        {loading ? 'Loading...' : 'Submit'}
      </button>
    </form>
  );
};

export default ShippingForm;