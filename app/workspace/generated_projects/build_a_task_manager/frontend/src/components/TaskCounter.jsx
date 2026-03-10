import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TaskCounter = () => {
  const [totalTasks, setTotalTasks] = useState(0);
  const [completedTasks, setCompletedTasks] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTaskCount = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/tasks/count');
        setTotalTasks(response.data.total);
        setCompletedTasks(response.data.completed);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTaskCount();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <div>
        <h3>Total Tasks: {totalTasks}</h3>
      </div>
      <div>
        <h3>Completed Tasks: {completedTasks}</h3>
      </div>
    </div>
  );
};

export default TaskCounter;