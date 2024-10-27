import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

const Search = () => {
  const [town, setTown] = useState('');
  const [restaurant, setRestaurant] = useState('');
  const [restaurants, setRestaurants] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!town || !restaurant) {
      setError('Both fields are required');
      return;
    }
    setError('');

    try {
        const response = await axios.get(`${API_BASE_URL}/restaurants/search/`, {
        params: {
            town: town,
            name: restaurant,
            limit: 10
        }
    });

      if (response.data.length > 0) {
        setRestaurants(response.data);
      } else {
        setRestaurants([]);
        setError('No restaurants found');
      }
    } catch (error) {
      console.error('There was an error searching for restaurants:', error);
      setError('There was an error searching for restaurants');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Search for Restaurants</h1>
      <form onSubmit={handleSearch} className="mb-4">
        <div className="mb-2">
          <label className="block text-gray-700">Town</label>
          <input
            type="text"
            value={town}
            onChange={(e) => setTown(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Enter town name"
          />
        </div>
        <div className="mb-2">
          <label className="block text-gray-700">Restaurant</label>
          <input
            type="text"
            value={restaurant}
            onChange={(e) => setRestaurant(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Enter restaurant name"
          />
        </div>
        {error && <p className="text-red-500">{error}</p>}
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Search
        </button>
      </form>
      {restaurants.length > 0 && (
        <div>
          <h2 className="text-2xl font-semibold mb-4">Restaurants Found</h2>
          <ul>
            {restaurants.map((restaurant, index) => (
              <li key={index} className="mb-2 p-4 border border-gray-300 rounded">
                <h3 className="text-xl font-semibold">{restaurant.displayName ? restaurant.displayName.text : "NO NAME"}</h3>
                <p>{restaurant.formattedAddress}</p>
                <p>{restaurant.nationalPhoneNumber}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Search;