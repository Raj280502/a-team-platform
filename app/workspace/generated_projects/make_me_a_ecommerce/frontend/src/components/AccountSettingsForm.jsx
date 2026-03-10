import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AccountSettingsForm.css';

const AccountSettingsForm = ({ userId, token }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const userData = response.data;
        setUsername(userData.username);
        setEmail(userData.email);
      } catch (error) {
        setError(error.message);
      }
    };
    fetchUser();
  }, [userId, token]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      const response = await axios.patch(`http://localhost:5000/api/users/${userId}`, {
        username,
        email,
        password,
      }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSuccess('Account settings updated successfully');
      setError(null);
    } catch (error) {
      setError(error.message);
      setSuccess(null);
    }
  };

  return (
    <div className="account-settings-form">
      <h2>Account Settings</h2>
      {error && <p className="error-message">{error}</p>}
      {success && <p className="success-message">{success}</p>}
      <form onSubmit={handleSubmit}>
        <label>Username:</label>
        <input type="text" value={username} onChange={(event) => setUsername(event.target.value)} />
        <br />
        <label>Email:</label>
        <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        <br />
        <label>Password:</label>
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        <br />
        <label>Confirm Password:</label>
        <input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
        <br />
        <button type="submit">Update Account Settings</button>
      </form>
    </div>
  );
};

export default AccountSettingsForm;