import React, { useState } from 'react';
import axios from 'axios';

const NewTaskForm = ({ categories, priorities, onTaskCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [priorityId, setPriorityId] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost:5000/api/tasks', {
        title,
        description,
        categoryId,
        priorityId,
        dueDate,
      });
      onTaskCreated(response.data);
      setTitle('');
      setDescription('');
      setCategoryId('');
      setPriorityId('');
      setDueDate('');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '500px', margin: '40px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)' }}>
      <h2>Create New Task</h2>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <div>
        <label>Title:</label>
        <input type="text" value={title} onChange={(event) => setTitle(event.target.value)} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0' }} />
      </div>
      <div>
        <label>Description:</label>
        <textarea value={description} onChange={(event) => setDescription(event.target.value)} style={{ width: '100%', height: '100px', padding: '10px', margin: '10px 0' }} />
      </div>
      <div>
        <label>Category:</label>
        <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0' }}>
          <option value="">Select Category</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>{category.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Priority:</label>
        <select value={priorityId} onChange={(event) => setPriorityId(event.target.value)} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0' }}>
          <option value="">Select Priority</option>
          {priorities.map((priority) => (
            <option key={priority.id} value={priority.id}>{priority.name}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Due Date:</label>
        <input type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} style={{ width: '100%', height: '30px', padding: '10px', margin: '10px 0' }} />
      </div>
      <button type="submit" style={{ width: '100%', height: '40px', backgroundColor: '#4CAF50', color: '#fff', padding: '10px', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Create Task</button>
    </form>
  );
};

export default NewTaskForm;