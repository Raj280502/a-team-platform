import React, { useState, useEffect } from 'react';
// [auto-removed] import axios from 'axios';  -- file not found
import './App.css';
import FavoriteGrid from './components/FavoriteGrid';
import FilterBar from './components/FilterBar';
import RecipeForm from './components/RecipeForm';
import RecipeGrid from './components/RecipeGrid';
import SearchBar from './components/SearchBar';

function App() {
  const [title, setTitle] = useState('');
  const [ingredients, setIngredients] = useState('');
  const [instructions, setInstructions] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [activeTab, setActiveTab] = useState('home');
  const [favorites, setFavorites] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    axios.get('/api/recipes')
      .then(response => {
        setRecipes(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  }, []);

  const handleAddRecipe = (event) => {
    event.preventDefault();
    setLoading(true);
    axios.post('/api/recipes', {
      title,
      ingredients,
      instructions
    })
      .then(response => {
        setRecipes([...recipes, response.data]);
        setTitle('');
        setIngredients('');
        setInstructions('');
        setSuccess('Recipe added successfully!');
        setLoading(false);
      })
      .catch(error => {
        setError(error.message);
        setLoading(false);
      });
  };

  const handleSearch = (event) => {
    event.preventDefault();
    axios.get('/api/recipes/search', {
      params: {
        query: searchQuery
      }
    })
      .then(response => {
        setRecipes(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  };

  const handleFilter = (filter) => {
    setActiveFilter(filter);
    axios.get('/api/recipes', {
      params: {
        filter
      }
    })
      .then(response => {
        setRecipes(response.data);
      })
      .catch(error => {
        setError(error.message);
      });
  };

  const handleFavorite = (recipeId) => {
    axios.post(`/api/recipes/${recipeId}/favorite`)
      .then(response => {
        setFavorites([...favorites, response.data]);
      })
      .catch(error => {
        setError(error.message);
      });
  };

  const handleRemoveFromFavorites = (recipeId) => {
    axios.delete(`/api/recipes/${recipeId}/favorite`)
      .then(response => {
        setFavorites(favorites.filter((favorite) => favorite.id !== recipeId));
      })
      .catch(error => {
        setError(error.message);
      });
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Recipe App</h1>
        <nav>
          <ul>
            <li><a href="#" onClick={() => setActiveTab('home')}>Home</a></li>
            <li><a href="#" onClick={() => setActiveTab('add-recipe')}>Add Recipe</a></li>
            <li><a href="#" onClick={() => setActiveTab('favorites')}>Favorites</a></li>
          </ul>
        </nav>
      </header>
      {activeTab === 'home' && (
        <div className="home-page">
          <SearchBar
            searchQuery={searchQuery}
            handleSearch={handleSearch}
            setSearchQuery={setSearchQuery}
          />
          <FilterBar
            activeFilter={activeFilter}
            handleFilter={handleFilter}
          />
          <RecipeGrid
            recipes={recipes}
            handleFavorite={handleFavorite}
          />
        </div>
      )}
      {activeTab === 'add-recipe' && (
        <div className="add-recipe-page">
          <RecipeForm
            title={title}
            ingredients={ingredients}
            instructions={instructions}
            handleAddRecipe={handleAddRecipe}
            setTitle={setTitle}
            setIngredients={setIngredients}
            setInstructions={setInstructions}
          />
        </div>
      )}
      {activeTab === 'favorites' && (
        <div className="favorites-page">
          <FavoriteGrid
            favorites={favorites}
            handleRemoveFromFavorites={handleRemoveFromFavorites}
          />
        </div>
      )}
      {loading && (
        <div className="loading-overlay">
          <p>Loading...</p>
        </div>
      )}
      {error && (
        <div className="error-message">
          <p style={{ color: 'red' }}>{error}</p>
        </div>
      )}
      {success && (
        <div className="success-message">
          <p style={{ color: 'green' }}>{success}</p>
        </div>
      )}
    </div>
  );
}

export default App;