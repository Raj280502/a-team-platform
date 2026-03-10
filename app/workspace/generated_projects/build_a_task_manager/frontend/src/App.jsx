import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [newTask, setNewTask] = useState(false);
  const [editTask, setEditTask] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:5000/api/tasks')
      .then(response => {
        setTasks(response.data);
      })
      .catch(error => {
        setError(error.message);
      });

    axios.get('http://localhost:5000/api/categories')
      .then(response => {
        setCategories(response.data);
      })
      .catch(error => {
        setError(error.message);
      });

    axios.get('http://localhost:5000/api/priorities')
      .then(response => {
        setPriorities(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  const handleCreateTask = (event) => {
    event.preventDefault();
    setLoading(true);
    axios.post('http://localhost:5000/api/tasks', {
      title,
      description,
      category,
      priority,
      dueDate
    })
      .then(response => {
        setTasks([...tasks, response.data]);
        setTitle('');
        setDescription('');
        setCategory('');
        setPriority('');
        setDueDate('');
        setSuccess('Task created successfully!');
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleUpdateTask = (event, id) => {
    event.preventDefault();
    setLoading(true);
    axios.put(`http://localhost:5000/api/tasks/${id}`, {
      title,
      description,
      category,
      priority,
      dueDate
    })
      .then(response => {
        setTasks(tasks.map(task => task.id === id ? response.data : task));
        setTitle('');
        setDescription('');
        setCategory('');
        setPriority('');
        setDueDate('');
        setSuccess('Task updated successfully!');
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleDeleteTask = (id) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setLoading(true);
      axios.delete(`http://localhost:5000/api/tasks/${id}`)
        .then(response => {
          setTasks(tasks.filter(task => task.id !== id));
          setSuccess('Task deleted successfully!');
          setLoading(false);
        })
        .catch(error => {
          setError(error.message);
          setLoading(false);
        });
    }
  };

  const handleCompleteTask = (id) => {
    setLoading(true);
    axios.put(`http://localhost:5000/api/tasks/${id}/complete`)
      .then(response => {
        setTasks(tasks.map(task => task.id === id ? response.data : task));
        setSuccess('Task marked as completed!');
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleSearch = (event) => {
    event.preventDefault();
    setLoading(true);
    axios.get(`http://localhost:5000/api/tasks/search?q=${searchQuery}`)
      .then(response => {
        setTasks(response.data);
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Task Manager</h1>
      </header>
      <main className="main">
        <div className="container">
          <div className="filter-bar">
            <select value={activeFilter} onChange={(event) => setActiveFilter(event.target.value)}>
              <option value="all">All</option>
              {categories.map(category => (
                <option key={category.id} value={category.name}>{category.name}</option>
              ))}
            </select>
            <select value={activeFilter} onChange={(event) => setActiveFilter(event.target.value)}>
              <option value="all">All</option>
              {priorities.map(priority => (
                <option key={priority.id} value={priority.name}>{priority.name}</option>
              ))}
            </select>
          </div>
          <div className="search-bar">
            <form onSubmit={handleSearch}>
              <input type="search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search tasks" />
              <button type="submit">Search</button>
            </form>
          </div>
          <div className="task-list">
            {tasks.filter(task => {
              if (activeFilter === 'all') return true;
              if (task.category === activeFilter) return true;
              if (task.priority === activeFilter) return true;
              return false;
            }).map(task => (
              <div key={task.id} className="task-card">
                <h2>{task.title}</h2>
                <p>{task.description}</p>
                <p>Category: {task.category}</p>
                <p>Priority: {task.priority}</p>
                <p>Due Date: {task.dueDate}</p>
                <button onClick={() => handleCompleteTask(task.id)}>Complete</button>
                <button onClick={() => setEditTask(task)}>Edit</button>
                <button onClick={() => handleDeleteTask(task.id)}>Delete</button>
              </div>
            ))}
          </div>
          {newTask && (
            <div className="new-task-form">
              <form onSubmit={handleCreateTask}>
                <label>
                  Title:
                  <input type="text" value={title} onChange={(event) => setTitle(event.target.value)} />
                </label>
                <label>
                  Description:
                  <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
                </label>
                <label>
                  Category:
                  <select value={category} onChange={(event) => setCategory(event.target.value)}>
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.name}>{category.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Priority:
                  <select value={priority} onChange={(event) => setPriority(event.target.value)}>
                    <option value="">Select a priority</option>
                    {priorities.map(priority => (
                      <option key={priority.id} value={priority.name}>{priority.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Due Date:
                  <input type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} />
                </label>
                <button type="submit">Create Task</button>
              </form>
            </div>
          )}
          {editTask && (
            <div className="edit-task-form">
              <form onSubmit={(event) => handleUpdateTask(event, editTask.id)}>
                <label>
                  Title:
                  <input type="text" value={title} onChange={(event) => setTitle(event.target.value)} />
                </label>
                <label>
                  Description:
                  <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
                </label>
                <label>
                  Category:
                  <select value={category} onChange={(event) => setCategory(event.target.value)}>
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.name}>{category.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Priority:
                  <select value={priority} onChange={(event) => setPriority(event.target.value)}>
                    <option value="">Select a priority</option>
                    {priorities.map(priority => (
                      <option key={priority.id} value={priority.name}>{priority.name}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Due Date:
                  <input type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} />
                </label>
                <button type="submit">Update Task</button>
              </form>
            </div>
          )}
          {loading && (
            <div className="loading">
              <p>Loading...</p>
            </div>
          )}
          {error && (
            <div className="error">
              <p style={{ color: 'red' }}>{error}</p>
            </div>
          )}
          {success && (
            <div className="success">
              <p style={{ color: 'green' }}>{success}</p>
            </div>
          )}
        </div>
      </main>
      <footer className="footer">
        <p>&copy; 2024 Task Manager</p>
      </footer>
    </div>
  );
}

export default App;