import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const API_BASE_URL = "http://127.0.0.1:8000";

const DishPage = () => {
  const { id } = useParams();
  const [dish, setDish] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loadingDish, setLoadingDish] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(true);

  useEffect(() => {
    const fetchDishData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/dishes/${id}`);
        console.log(response)
        setDish(response.data);
      } catch (error) {
        console.error('Error fetching dish data:', error);
      } finally {
        setLoadingDish(false);
      }
    };

    if (id) {
      fetchDishData();
    }
  }, [id]);

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/reviews/dish/${id}`);
        const reviewsData = response.data;

        // For each review, call /check_safety/ endpoint
        const reviewsWithSafety = await Promise.all(reviewsData.map(async (review) => {
          const comment = review.comment;
          const tag_list = [...(review.allergies || []), ...(review.restrictions || [])];

          try {
            const safetyResponse = await axios.post(`${API_BASE_URL}/check_safety/`, {
              comment: comment,
              tag_list: tag_list
            });

            const safe_categories = safetyResponse.data.safe_categories;

            return {
              ...review,
              safe_categories: safe_categories
            };

          } catch (error) {
            console.error('Error checking safety for review:', error);
            return {
              ...review,
              safe_categories: []
            };
          }
        }));

        setReviews(reviewsWithSafety);
      } catch (error) {
        console.error('Error fetching reviews:', error);
      } finally {
        setLoadingReviews(false);
      }
    };

    if (dish) {
      fetchReviews();
    }
  }, [dish]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Dish Page</h1>
      {loadingDish ? (
        <p>Loading dish data...</p>
      ) : dish ? (
        <div>
          <h2 className="text-2xl font-semibold">{dish.name}</h2>
          {dish.image_url && <img src={dish.image_url} alt={dish.name} className="w-32 h-32 object-cover" />}
          <p><strong>Allergies:</strong> {dish.allergies ? dish.allergies.join(', ') : 'No allergies information available'}</p>
          <p><strong>Restrictions:</strong> {dish.restrictions ? dish.restrictions.join(', ') : 'No restrictions information available'}</p>
        </div>
      ) : (
        <p>Dish not found.</p>
      )}

      <h2 className="text-2xl font-semibold mt-8">Reviews</h2>
      {loadingReviews ? (
        <p>Loading reviews...</p>
      ) : reviews.length > 0 ? (
        reviews.map((review) => (
          <div key={review.id} className="border border-gray-300 p-4 mb-4 rounded">
            <p><strong>Comment:</strong> {review.comment}</p>
            <p><strong>Safe Categories:</strong> {review.safe_categories.join(', ')}</p>
          </div>
        ))
      ) : (
        <p>No reviews found.</p>
      )}
    </div>
  );
};

export default DishPage;