import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get('http://localhost:5000/items');
      setTasks(response.data);
    } catch (err) {
      setError('Failed to fetch tasks');
    }
  };

  const addTask = async () => {
    if (!title || !description || !dueDate) {
      setError('All fields are required');
      return;
    }
    try {
      await axios.post('http://localhost:5000/add', {
        title,
        description,
        dueDate
      });
      setSuccess('Task added successfully');
      setTitle('');
      setDescription('');
      setDueDate('');
      fetchTasks();
    } catch (err) {
      setError('Failed to add task');
    }
  };

  const markComplete = async (taskId) => {
    try {
      await axios.put(`http://localhost:5000/mark_complete/${taskId}`);
      setSuccess('Task marked as complete');
      fetchTasks();
    } catch (err) {
      setError('Failed to mark task as complete');
    }
  };

  const deleteCompleted = async () => {
    try {
      await axios.delete('http://localhost:5000/delete_completed');
      setSuccess('Completed tasks deleted');
      fetchTasks();
    } catch (err) {
      setError('Failed to delete completed tasks');
    }
  };

  const setReminder = async (taskId) => {
    try {
      await axios.put(`http://localhost:5000/set_reminder/${taskId}`);
      setSuccess('Reminder set for task');
      fetchTasks();
    } catch (err) {
      setError('Failed to set reminder for task');
    }
  };

  const handleFilter = (e) => {
    const filterValue = e.target.value;
    const filteredTasks = tasks.filter(task => {
      if (filterValue === 'all') return true;
      if (filterValue

export default App;