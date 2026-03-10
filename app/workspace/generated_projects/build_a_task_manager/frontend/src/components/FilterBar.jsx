import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FilterBar.css';

const FilterBar = ({ onFilterChange }) => {
  const [categories, setCategories] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPriority, setSelectedPriority] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
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

    fetchCategories();
    fetchPriorities();
  }, []);

  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
    onFilterChange({ category: event.target.value, priority: selectedPriority, dueDate: dueDate });
  };

  const handlePriorityChange = (event) => {
    setSelectedPriority(event.target.value);
    onFilterChange({ category: selectedCategory, priority: event.target.value, dueDate: dueDate });
  };

  const handleDueDateChange = (event) => {
    setDueDate(event.target.value);
    onFilterChange({ category: selectedCategory, priority: selectedPriority, dueDate: event.target.value });
  };

  return (
    <div className="filter-bar">
      <div className="filter-category">
        <label>Category:</label>
        <select value={selectedCategory} onChange={handleCategoryChange}>
          <option value="">All</option>
          {categories.map((category) => (
            <option key={category.id} value={category.name}>
              {category.name}
            </option>
          ))}
        </select>
      </div>
      <div className="filter-priority">
        <label>Priority:</label>
        <select value={selectedPriority} onChange={handlePriorityChange}>
          <option value="">All</option>
          {priorities.map((priority) => (
            <option key={priority.id} value={priority.name}>
              {priority.name}
            </option>
          ))}
        </select>
      </div>
      <div className="filter-due-date">
        <label>Due Date:</label>
        <input type="date" value={dueDate} onChange={handleDueDateChange} />
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default FilterBar;