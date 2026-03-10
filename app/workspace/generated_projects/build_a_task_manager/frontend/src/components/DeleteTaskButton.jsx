import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DeleteTaskButton = ({ taskId, handleDeleteTask }) => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await axios.delete(`http://localhost:5000/api/tasks/${taskId}`);
      handleDeleteTask(taskId);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      style={{
        backgroundColor: 'red',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
      }}
      onClick={handleDelete}
      disabled={isLoading}
    >
      {isLoading ? 'Deleting...' : 'Delete Task'}
      {error && <span style={{ color: 'red' }}>{error}</span>}
    </button>
  );
};

export default DeleteTaskButton;