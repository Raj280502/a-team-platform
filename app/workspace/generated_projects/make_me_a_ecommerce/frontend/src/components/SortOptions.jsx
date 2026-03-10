import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SortOptions.css';

const SortOptions = ({ handleSort, products }) => {
  const [sortOptions, setSortOptions] = useState([
    { value: 'price', label: 'Price' },
    { value: 'brand', label: 'Brand' },
    { value: 'rating', label: 'Rating' },
  ]);
  const [selectedSort, setSelectedSort] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');

  const handleSortChange = (e) => {
    setSelectedSort(e.target.value);
  };

  const handleSortOrderChange = (e) => {
    setSortOrder(e.target.value);
  };

  const applySort = () => {
    if (selectedSort) {
      const sortedProducts = products.sort((a, b) => {
        if (selectedSort === 'price') {
          return sortOrder === 'asc' ? a.price - b.price : b.price - a.price;
        } else if (selectedSort === 'brand') {
          return sortOrder === 'asc' ? a.brand.localeCompare(b.brand) : b.brand.localeCompare(a.brand);
        } else if (selectedSort === 'rating') {
          return sortOrder === 'asc' ? a.rating - b.rating : b.rating - a.rating;
        }
      });
      handleSort(sortedProducts);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/products');
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="sort-options">
      <label>Sort by:</label>
      <select value={selectedSort} onChange={handleSortChange}>
        <option value="">Select an option</option>
        {sortOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <label>Sort order:</label>
      <select value={sortOrder} onChange={handleSortOrderChange}>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>
      <button onClick={applySort}>Apply sort</button>
    </div>
  );
};

export default SortOptions;