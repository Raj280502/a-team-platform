import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EditTaskForm = (props) => {
  const [task, setTask] = useState({
    id: props.taskId,
    title: '',
    description: '',
    category: '',
    priority: '',
    dueDate: ''
  });
  const [categories, setCategories] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/tasks/${props.taskId}`);
        setTask(response.data);
      } catch (error) {
        setError(error.message);
      }
    };

    const fetchCategories = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/categories');
        setCategories(response.data);
      } catch (error) {
        setError(error.message);
      }
    };

    const fetchPriorities = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/priorities');
        setPriorities(response.data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchTask();
    fetchCategories();
    fetchPriorities();
    setIsLoaded(true);
  }, [props.taskId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await axios.put(`http://localhost:5000/api/tasks/${props.taskId}`, task);
      props.onEditTask();
    } catch (error) {
      setError(error.message);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setTask({ ...task, [name]: value });
  };

  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  return (
    <form onSubmit={handleSubmit} style={{ width: '50%', margin: '40px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
      <h2>Edit Task</h2>
      <div>
        <label>Title:</label>
        <input type="text" name="title" value={task.title} onChange={handleInputChange} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }} />
      </div>
      <div>
        <label>Description:</label>
        <textarea name="description" value={task.description} onChange={handleInputChange} style={{ width: '100%', height: '100px', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }} />
      </div>
      <div>
        <label>Category:</label>
        <select name="category" value={task.category} onChange={handleInputChange} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }}>
          <option value="">Select Category</option>
          {categories.map((category) => (
            <option key={category.id} value={category.name}>{category.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Priority:</label>
        <select name="priority" value={task.priority} onChange={handleInputChange} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }}>
          <option value="">Select Priority</option>
          {priorities.map((priority) => (
            <option key={priority.id} value={priority.name}>{priority.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Due Date:</label>
        <input type="date" name="dueDate" value={task.dueDate} onChange={handleInputChange} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0', border: '1px solid #ccc' }} />
      </div>
      <button type="submit" style={{ width: '100%', height: '40px', padding: '10px', margin: '10px 0', border: 'none', borderRadius: '10px', backgroundColor: '#4CAF50', color: '#fff', cursor: 'pointer' }}>Save Changes</button>
    </form>
  );
};

export default EditTaskForm;