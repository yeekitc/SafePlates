import React, { useState, useEffect } from 'react';
import axios from 'axios';
import HomePage from './HomePage';
import AuthPage from './AuthPage';
import MovieSearch from './MovieSearch';
import RestaurantSearch from './RestaurantSearch';

const API_BASE_URL = "http://127.0.0.1:8000";

const App = () => {
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentView, setCurrentView] = useState('home');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData(token);
    }
  }, []);

  const fetchUserData = async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/protected-route/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
      localStorage.removeItem('token');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCurrentView('home');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800 cursor-pointer" onClick={() => setCurrentView('home')}>
          MovieDB
        </h1>
        <div className="space-x-2">
          <button
            onClick={() => setCurrentView('search')}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Search Movies
          </button>
          <button
            onClick={() => setCurrentView('restaurant')}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Search Restaurants
          </button>
          {user ? (
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Login/Register
            </button>
          )}
        </div>
      </header>

      <main>
        {currentView === 'home' && <HomePage user={user} />}
        {currentView === 'search' && <MovieSearch />}
        {currentView === 'restaurant' && <RestaurantSearch />}
      </main>

      {showAuthModal && (
        <AuthPage
          onLogin={(token) => fetchUserData(token)}
          onClose={() => setShowAuthModal(false)}
        />
      )}
    </div>
  );
};

export default App;