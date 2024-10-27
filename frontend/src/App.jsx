import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NavBar from './components/NavBar';

const API_BASE_URL = "http://127.0.0.1:8000";

const App = () => {
  const [user, setUser] = useState(null);

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

  return (
    <main>
      <NavBar />
      {user ? (
        <h1>{`Welcome back, ${user.message.split(',')[1].split('!')[0].trim()}!`}</h1>
      ) : (
        <h1>Welcome, Guest!</h1>
      )}
    </main>
  );
};

export default App;