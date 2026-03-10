import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TaskHeader = (props) => {
  const [task, setTask] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/tasks/${props.taskId}`);
        setTask(response.data);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };
    fetchTask();
  }, [props.taskId]);

  if (loading) {
    return <div style={{ textAlign: 'center' }}>Loading...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', color: 'red' }}>{error}</div>;
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', borderBottom: '1px solid #ccc' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>{task.title}</h2>
      <div style={{ fontSize: '16px', color: '#666' }}>Due: {new Date(task.dueDate).toLocaleDateString()}</div>
    </div>
  );
};

export default TaskHeader;