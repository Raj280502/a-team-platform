import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [urgency, setUrgency] = useState('low');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/items');
      setTasks(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error fetching tasks');
      setLoading(false);
    }
  };

  const addTask = async () => {
    try {
      const data = { title, description, dueDate, urgency };
      await axios.post('http://localhost:5000/add', data);
      setSuccessMessage('Task added successfully!');
      setTitle('');
      setDescription('');
      setDueDate('');
      setUrgency('low');
      fetchTasks();
    } catch (err) {
      setError('Error adding task');
    }
  };

  const completeTask = async (id) => {
    try {
      await axios.put(`http://localhost:5000/complete/${id}`);
      setSuccessMessage('Task marked as complete!');
      fetchTasks();
    } catch (err) {
      setError('Error marking task as complete');
    }
  };

  const deleteTask = async (id) => {
    try {
      await axios.delete(`http://localhost:5000/delete/${id}`);
      setSuccessMessage('Task deleted successfully!');
      fetchTasks();
    } catch (err) {
      setError('Error deleting task');
    }
  };

  const setReminder = async (id) => {
    try {
      await axios.put(`http://localhost:5000/set_reminder/${id}`);
      setSuccessMessage('Reminder set!');
    } catch (err) {
      setError('Error setting reminder');
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Task Manager</h1>
      <form style={styles.form}>
        <input

export default App;