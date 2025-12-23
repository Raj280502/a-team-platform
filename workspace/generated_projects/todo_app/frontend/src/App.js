import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    const response = await axios.get('http://localhost:5000/tasks');
    setTasks(response.data);
  };

  const addTask = async () => {
    if (newTask.trim()) {
      const task = { id: Date.now(), text: newTask, completed: false };
      await axios.post('http://localhost:5000/tasks', task);
      setTasks([...tasks, task]);
      setNewTask('');
    }
  };

  const toggleTask = async (id) => {
    const task = tasks.find(t => t.id === id);
    const updatedTask = { ...task, completed: !task.completed };
    await axios.put(`http://localhost:5000/tasks/${id}`, updatedTask);
    setTasks(tasks.map(t => t.id === id ? updatedTask : t));
  };

  const deleteTask = async (id) => {
    await axios.delete(`http://localhost:5000/tasks/${id}`);
    setTasks(tasks.filter(t => t.id !== id));
  };

  return (
    <div>
      <h1>Todo App</h1>
      <input
        type="text"
        value={newTask}
        onChange={(e) => setNewTask(e.target.value)}
        placeholder="Add a new task"
      />
      <button onClick={addTask}>Add Task</button>
      <ul>
        {tasks.map(task => (
          <li key={task.id}>
            <span style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
              {task.text}
            </span>
            <button onClick={() => toggleTask(task.id)}>Toggle</button>
            <button onClick={() => deleteTask(task.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default App;