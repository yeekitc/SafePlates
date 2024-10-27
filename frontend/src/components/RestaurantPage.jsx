import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const API_BASE_URL = "http://13.58.201.35:8000";

const RestaurantPage = () => {
  const { id } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRestaurant = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/restaurants/id/${id}`);
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
      <h1 className="text-3xl font-bold mb-4">{restaurant.name || 'No name available'}</h1>
      <div className="mb-4">
        <h2 className="text-2xl font-semibold">Details</h2>
        <p><strong>Address:</strong> {restaurant.google_data?.address || 'No address available'}</p>
        <p><strong>Rating:</strong> {restaurant.google_data?.rating || 'No rating available'}</p>
        <p><strong>Price Level:</strong> {restaurant.google_data?.priceLevel || 'No price level available'}</p>
        <p><strong>Phone:</strong> {restaurant.google_data?.nationalPhoneNumber || 'No phone number available'}</p>
      </div>
      <div>
        <h2 className="text-2xl font-semibold">Menu</h2>
        {restaurant.menu && restaurant.menu.length > 0 ? (
          <ul>
            {restaurant.menu.map((dish, index) => (
              <li key={index} className="mb-2">
                <h3 className="text-xl font-semibold">{dish.name || 'No name available'}</h3>
                <img src={dish.image_url || 'default-image.jpg'} alt={dish.name || 'Dish'} className="w-32 h-32 object-cover" />
                <p><strong>Allergies:</strong> {dish.allergies ? dish.allergies.join(', ') : 'No allergies information available'}</p>
                <p><strong>Restrictions:</strong> {dish.restrictions ? dish.restrictions.join(', ') : 'No restrictions information available'}</p>
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