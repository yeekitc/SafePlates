import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import axios from 'axios';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import AddReview from './components/AddReview';
import NavBar from './components/NavBar';
import Search from './components/Search';
import toast, { Toaster } from 'react-hot-toast';

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
    <>
      <Toaster
        position="top-center"
        reverseOrder={true}
      />
      <Router>
        <main className="bg-beige min-h-screen">
          <NavBar />
          <Routes>
            <Route path="/" element={<Search user={user} />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/add-review" element={<AddReview />} />
          </Routes>
        </main>
      </Router>
    </>
  );
};

export default App;