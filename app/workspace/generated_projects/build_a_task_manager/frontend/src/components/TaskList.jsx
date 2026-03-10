import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TaskList.css';

const TaskList = ({ categoryId, priorityId }) => {
  const [tasks, setTasks] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/api/tasks');
        setTasks(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, []);

  useEffect(() => {
    const filtered = tasks.filter((task) => {
      const categoryMatch = categoryId ? task.categoryId === categoryId : true;
      const priorityMatch = priorityId ? task.priorityId === priorityId : true;
      const searchMatch = task.name.toLowerCase().includes(searchTerm.toLowerCase());
      return categoryMatch && priorityMatch && searchMatch;
    });
    setFilteredTasks(filtered);
  }, [tasks, categoryId, priorityId, searchTerm]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleComplete = async (taskId) => {
    try {
      await axios.patch(`http://localhost:5000/api/tasks/${taskId}/complete`);
      setTasks((prevTasks) =>
        prevTasks.map((task) => (task.id === taskId ? { ...task, completed: true } : task))
      );
    } catch (error) {
      setError(error.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="task-list">
      <input
        type="search"
        value={searchTerm}
        onChange={handleSearch}
        placeholder="Search tasks"
        className="search-input"
      />
      <ul>
        {filteredTasks.map((task) => (
          <li key={task.id}>
            <span
              style={{
                textDecoration: task.completed ? 'line-through' : 'none',
              }}
            >
              {task.name}
            </span>
            <button onClick={() => handleComplete(task.id)}>Complete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TaskList;