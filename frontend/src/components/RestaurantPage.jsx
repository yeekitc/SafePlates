import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const API_BASE_URL = "http://127.0.0.1:8000";

const RestaurantPage = () => {
  const { id } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRestaurant = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/restaurants/${id}`);
        setRestaurant(response.data);
      } catch (error) {
        console.error('There was an error fetching the restaurant details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRestaurant();
  }, [id]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!restaurant) {
    return <div>Restaurant not found</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{restaurant.name}</h1>
      <div className="mb-4">
        <h2 className="text-2xl font-semibold">Details</h2>
        <p><strong>Address:</strong> {restaurant.google_data.address}</p>
        <p><strong>Rating:</strong> {restaurant.google_data.rating}</p>
        <p><strong>Price Level:</strong> {restaurant.google_data.priceLevel}</p>
        <p><strong>Phone:</strong> {restaurant.google_data.nationalPhoneNumber}</p>
      </div>
      <div>
        <h2 className="text-2xl font-semibold">Menu</h2>
        {restaurant.menu.length > 0 ? (
          <ul>
            {restaurant.menu.map((dish, index) => (
              <li key={index} className="mb-2">
                <h3 className="text-xl font-semibold">{dish.name}</h3>
                <img src={dish.image_url} alt={dish.name} className="w-32 h-32 object-cover" />
                <p><strong>Allergies:</strong> {dish.allergies.join(', ')}</p>
                <p><strong>Restrictions:</strong> {dish.restrictions.join(', ')}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No dishes available</p>
        )}
      </div>
    </div>
  );
};

export default RestaurantPage;