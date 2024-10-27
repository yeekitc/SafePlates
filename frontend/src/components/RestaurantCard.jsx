import React from 'react';
import placeholderImg from '../assets/restaurant-placeholder.jpg'
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = "http://13.58.201.35:8000";

const RestaurantCard = ({ restaurant }) => {
  const navigate = useNavigate();

  const handleClick = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/restaurants/${restaurant.id}`);
      console.log('Restaurant details:', response.data);
      navigate(`/restaurants/${response.data.id}`);
    } catch (error) {
      console.error('There was an error fetching the restaurant details:', error);
      // Add this restaurant to the database and then call GET again
      const newRestaurantJson = {
        name: restaurant.displayName.text,
        google_data: {
          place_id: restaurant.placeId,
          address: restaurant.formattedAddress,
          rating: restaurant.rating,
          priceLevel: restaurant.priceLevel,
          nationalPhoneNumber: restaurant.nationalPhoneNumber,
          reviews: restaurant.reviews
        },
        menu: []
      };
      try {
        const response = await axios.post(`${API_BASE_URL}/restaurants/`, newRestaurantJson);
        console.log('New restaurant added:', response.data);
      } catch (error) {
        console.error('There was an error adding the restaurant:', error);
      }

    }
  };

  return (
    <div onClick={handleClick} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <div className="h-56 w-full">
        <a href="#">
          <img
            className="mx-auto h-full"
            src={restaurant.imageUrl || placeholderImg}
            alt={restaurant.displayName.text || 'Restaurant'}
          />
          <img
            className="mx-auto hidden h-full"
            src={restaurant.imageUrlDark || 'default-image-dark.jpg'}
            alt={restaurant.displayName.text || 'Restaurant'}
          />
        </a>
      </div>
      <div className="pt-6">
        <h3 className="text-lg font-semibold leading-tight text-gray-900 hover:underline">
          {restaurant.displayName.text || 'No restaurant display name'}
        </h3>
        <p className="text-sm mt-2 text-gray-500">
          {restaurant.formattedAddress || 'No address available.'}
        </p>
      </div>
    </div>
  );
};

export default RestaurantCard;