import React, { useState } from 'react';
import axios from 'axios';
import RestaurantCard from './RestaurantCard';

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
    <div className="max-w-screen-xl mx-auto p-4">
      <h1 className="text-5xl text-center font-bold mb-4">SafePlate</h1>
      <h2 className="text-3xl text-center font-bold mb-4">Safe and yummy options for everyone.</h2>
      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 items-center justify-center p-4 rounded-md">
        <div className="flex flex-col items-center sm:items-start">
          <label className="block text-gray-700">Town</label>
          <input
            type="text"
            value={town}
            onChange={(e) => setTown(e.target.value)}
            className="w-72 p-2 border border-gray-300 rounded"
            placeholder="Pittsburgh, PA"
          />
        </div>
        <div className="flex flex-col items-center sm:items-start">
          <label className="block text-gray-700">Restaurant</label>
          <input
            type="text"
            value={restaurant}
            onChange={(e) => setRestaurant(e.target.value)}
            className="w-72 p-2 border border-gray-300 rounded"
            placeholder="Chipotle"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-2 bg-yorange text-white rounded"
        >
          Search
        </button>
      </form>
      {error && <p className="text-red-500 text-center">{error}</p>}
      {restaurants.length > 0 && (
        <div>
          <h2 className="text-2xl text-center font-semibold mb-4">Restaurants Found</h2>
          <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {restaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Search;