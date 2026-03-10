import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './InstructionSteps.css';

const InstructionSteps = ({ recipeId }) => {
  const [steps, setSteps] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSteps = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/recipes/${recipeId}`);
        setSteps(response.data.instructions);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSteps();
  }, [recipeId]);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="instruction-steps">
      <h2>Instructions</h2>
      {steps.map((step, index) => (
        <div key={index} className="step">
          <h3>Step {index + 1}</h3>
          <p>{step}</p>
        </div>
      ))}
    </div>
  );
};

export default InstructionSteps;