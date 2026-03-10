import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TaskDescription = (props) => {
  const [task, setTask] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/tasks/${props.taskId}`);
        setTask(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
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
    <div className="task-description">
      <h2>{task.title}</h2>
      <p>{task.description}</p>
      <p>Category: {task.category}</p>
      <p>Priority: {task.priority}</p>
      <p>Due Date: {task.dueDate}</p>
    </div>
  );
};

export default TaskDescription;