import React from 'react';
import placeholderImg from '../assets/restaurant-placeholder.jpg'

const RestaurantCard = ({ restaurant }) => {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
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