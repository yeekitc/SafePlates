
import React, { useState } from 'react';
import { 
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

const SearchBar = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [town, setTown] = useState('');
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    console.log("handleSearch");
    setLoading(true);
    // e.preventDefault();
    if (!searchQuery.trim()) {
      console.warn("Search query is empty. Please enter a search term.");
      return;
    }
    try {
      console.log("Searching for restaurants...");
      const response = await axios.get(`${API_BASE_URL}/restaurants/search/`, {
        params: { town: town, name: searchQuery, limit: 10 },
      });
      console.log(response);
      setRestaurants(response.data);
      
    } catch (error) {
      console.error("Error searching:", error);
    }
    setLoading(false);
  };

  return (
    <div>
    <form onSubmit={handleSearch} style={{ width: '100%', maxWidth: '600px', margin: '20px auto' }}>
      <TextField
        fullWidth
        value={town}
        onChange={(e) => setTown(e.target.value)}
        placeholder="Enter town"
        variant="outlined"
        style={{ 
          backgroundColor: 'white',
          borderRadius: '8px',
          marginBottom: '10px'
        }}
      />
      <TextField
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search for a restaurant"
        variant="outlined"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon style={{ color: 'grey' }} size={20} />
            </InputAdornment>
          ),
        }}
        style={{ 
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}
      />
    </form>
    {/* <button
      onClick={handleSearch}
      className="bg-blue-500 text-white px-4 py-2 rounded-md"
    >
      Search
    </button> */}
    {loading ? (
      <p className="text-center">Loading...</p>
      ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {restaurants.length > 0 ? (
          restaurants.map((restaurant) => (
              <div key={restaurant.id} className="bg-white p-4 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold">{restaurant.displayName ? restaurant.displayName.text : "No restaurant display name"}</h2>
              <p className="text-sm mt-2">
                  {restaurant.formattedAddress || "No address available."}
              </p>
              </div>
          ))
          ) : (
          <p className="text-center">No restaurants found.</p>
          )}
      </div>
      )}
      </div>
  );
};

export default SearchBar;
