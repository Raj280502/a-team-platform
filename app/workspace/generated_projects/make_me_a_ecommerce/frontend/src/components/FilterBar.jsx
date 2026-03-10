import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FilterBar.css';

const FilterBar = ({ onFilterChange }) => {
  const [priceRange, setPriceRange] = useState([0, 100]);
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [selectedRatings, setSelectedRatings] = useState([]);
  const [brands, setBrands] = useState([]);
  const [ratings, setRatings] = useState([1, 2, 3, 4, 5]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/products')
      .then(response => {
        const uniqueBrands = [...new Set(response.data.map(product => product.brand))];
        setBrands(uniqueBrands);
      })
      .catch(error => {
        console.error(error);
      });
  }, []);

  const handlePriceChange = (event, newValue) => {
    setPriceRange(newValue);
  };

  const handleBrandChange = (event) => {
    const brand = event.target.value;
    if (selectedBrands.includes(brand)) {
      setSelectedBrands(selectedBrands.filter(b => b !== brand));
    } else {
      setSelectedBrands([...selectedBrands, brand]);
    }
  };

  const handleRatingChange = (event) => {
    const rating = parseInt(event.target.value);
    if (selectedRatings.includes(rating)) {
      setSelectedRatings(selectedRatings.filter(r => r !== rating));
    } else {
      setSelectedRatings([...selectedRatings, rating]);
    }
  };

  const handleApplyFilter = () => {
    onFilterChange({
      priceRange,
      selectedBrands,
      selectedRatings
    });
  };

  return (
    <div className="filter-bar">
      <h2>Filter Products</h2>
      <div className="price-range">
        <label>Price Range:</label>
        <input
          type="range"
          min="0"
          max="100"
          value={priceRange[0]}
          onChange={(event) => handlePriceChange(event, [event.target.value, priceRange[1]])}
          style={{ marginRight: '10px' }}
        />
        <input
          type="range"
          min="0"
          max="100"
          value={priceRange[1]}
          onChange={(event) => handlePriceChange(event, [priceRange[0], event.target.value])}
        />
        <span>${priceRange[0]} - ${priceRange[1]}</span>
      </div>
      <div className="brand-filter">
        <label>Brands:</label>
        {brands.map((brand, index) => (
          <div key={index}>
            <input
              type="checkbox"
              value={brand}
              checked={selectedBrands.includes(brand)}
              onChange={handleBrandChange}
            />
            <span>{brand}</span>
          </div>
        ))}
      </div>
      <div className="rating-filter">
        <label>Ratings:</label>
        {ratings.map((rating, index) => (
          <div key={index}>
            <input
              type="checkbox"
              value={rating}
              checked={selectedRatings.includes(rating)}
              onChange={handleRatingChange}
            />
            <span>{rating} stars</span>
          </div>
        ))}
      </div>
      <button className="apply-filter" onClick={handleApplyFilter}>Apply Filter</button>
    </div>
  );
};

export default FilterBar;