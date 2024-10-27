
import React, { useState } from 'react';
import { 
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from 'lucide-react';

const SearchBar = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // You can change this to any search engine
      // Google: https://www.google.com/search?q=
      // Bing: https://www.bing.com/search?q=
      // DuckDuckGo: https://duckduckgo.com/?q=
      window.location.href = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ width: '100%', maxWidth: '600px', margin: '20px auto' }}>
      <TextField
        fullWidth
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search the web"
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
  );
};

export default SearchBar;
