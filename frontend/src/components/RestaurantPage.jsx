import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Paper,
  CircularProgress,
  Box
} from '@mui/material';
import { styled } from '@mui/material/styles';

const API_BASE_URL = "http://127.0.0.1:8000";

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

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
    <div className="max-w-screen-xl mx-auto p-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <h2 className="font-bold text-5xl mb-6">
            {restaurant.name || 'No name available'}
          </h2>

          <div className="space-y-8">
            {restaurant.menu && restaurant.menu.length > 0 ? (
              restaurant.menu.map((dish, index) => (
                <Card key={index} className="overflow-hidden">
                  <CardContent>
                    <h3 className="font-bold text-2xl mb-2">
                      {dish.name || 'No dish name available.'}
                    </h3>

                    <div className="flex flex-wrap gap-2 mb-4">
                      Allergy Information: {dish.allergies ? dish.allergies.map((allergy, i) => (
                        <Chip
                          key={i}
                          label={allergy}
                          color="warning"
                          variant="outlined"
                          className="bg-yellow-50"
                        />
                      )) : (
                        <h1>Unavailable</h1>
                      )}

                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                      Dietary Restrictions:{dish.restrictions ? dish.restrictions.map((restriction, i) => (
                        <Chip
                          key={i}
                          label={restriction}
                          color="success"
                          variant="outlined"
                          className="bg-green-50"
                        />
                      )) : (
                        <h1>Unavailable</h1>
                      )}
                    </div>

                    <img
                      src={dish.image_url || 'default-image.jpg'}
                      alt={dish.name || 'Dish'}
                      className="w-full h-48 object-cover rounded-md"
                    />
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent>
                  <Typography>No dishes available</Typography>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        <div className="md:col-span-1 mt-[76px]">
          <Paper elevation={3} className="p-4 sticky top-4">
            <h3 className="font-bold text-2xl mb-4">
              Restaurant Details
            </h3>

            <div className="space-y-4">
              {restaurant.google_data?.address && (
                <div>
                  <h4 className="font-semibold">
                    Address
                  </h4>
                  <h4 className="text-gray-600">
                    {restaurant.google_data.address}
                  </h4>
                </div>
              )}

              {restaurant.google_data?.rating && (
                <div>
                  <h4 className="font-semibold">
                    Rating
                  </h4>
                  <h4 className="text-gray-600">
                    {restaurant.google_data.rating} ⭐
                  </h4>
                </div>
              )}

              {restaurant.google_data?.priceLevel && (
                <div>
                  <h4 className="font-semibold">

                    Price Level
                  </h4>
                  <h4>
                    {'$'.repeat(restaurant.google_data.priceLevel)}
                  </h4>
                </div>
              )}

              {restaurant.google_data?.nationalPhoneNumber && (
                <div>
                  <h4 className="font-semibold">
                    Phone
                  </h4>
                  <h4>
                    {restaurant.google_data.nationalPhoneNumber}
                  </h4>
                </div>
              )}
            </div>
          </Paper>
        </div>
      </div>
    </div>
  );
};

export default RestaurantPage;