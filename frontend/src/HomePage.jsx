import React from 'react';
import SearchBar from './SearchBar';

const HomePage = ({ user }) => {
  return (
    <div className="max-w-4xl mx-auto mt-20 px-4">
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-gray-800 mb-4">
          {user ? `Welcome back, ${user.message.split(',')[1].split('!')[0].trim()}!` : 'Welcome, Guest!'}
        </h2>
        <p className="text-gray-600 text-lg mb-8">Discover your next favorite movie</p>
        <SearchBar />
      </div>
    </div>
  );
};

export default HomePage;