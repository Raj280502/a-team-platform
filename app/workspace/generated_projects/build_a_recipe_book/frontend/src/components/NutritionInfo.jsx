import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './NutritionInfo.css';

const NutritionInfo = ({ recipeId }) => {
  const [nutritionInfo, setNutritionInfo] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchNutritionInfo = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/recipes/${recipeId}/nutrition`);
        setNutritionInfo(response.data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };
    fetchNutritionInfo();
  }, [recipeId]);

  if (loading) {
    return <div className="nutrition-info-loading">Loading...</div>;
  }

  if (error) {
    return <div className="nutrition-info-error">Error: {error}</div>;
  }

  return (
    <div className="nutrition-info">
      <h2>Nutrition Information</h2>
      <ul>
        <li>
          <span>Calories:</span>
          <span>{nutritionInfo.calories}</span>
        </li>
        <li>
          <span>Protein:</span>
          <span>{nutritionInfo.protein}g</span>
        </li>
        <li>
          <span>Fat:</span>
          <span>{nutritionInfo.fat}g</span>
        </li>
        <li>
          <span>Carbohydrates:</span>
          <span>{nutritionInfo.carbohydrates}g</span>
        </li>
      </ul>
    </div>
  );
};

export default NutritionInfo;