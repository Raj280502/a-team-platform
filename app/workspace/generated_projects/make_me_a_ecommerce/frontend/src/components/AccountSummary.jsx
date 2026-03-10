import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AccountSummary.css';

const AccountSummary = ({ userId }) => {
  const [accountInfo, setAccountInfo] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchAccountInfo = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/customers/${userId}`);
        setAccountInfo(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAccountInfo();
  }, [userId]);

  if (isLoading) {
    return <div className="account-summary-loading">Loading...</div>;
  }

  if (error) {
    return <div className="account-summary-error">Error: {error}</div>;
  }

  return (
    <div className="account-summary">
      <h2>Account Summary</h2>
      <p>Name: {accountInfo.name}</p>
      <p>Email: {accountInfo.email}</p>
      <p>Order Count: {accountInfo.orderCount}</p>
      <p>Total Spend: ${accountInfo.totalSpend}</p>
    </div>
  );
};

export default AccountSummary;