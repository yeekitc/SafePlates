import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const API_BASE_URL = "http://127.0.0.1:8000";

const DishPage = () => {
  const { dishId } = useParams();
  const [dish, setDish] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loadingDish, setLoadingDish] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(true);

  useEffect(() => {
    fetchDishData();
  }, [dishId]);

  useEffect(() => {
    if (dish) {
      fetchReviews();
    }
  }, [dish]);

  const fetchDishData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dishes/${dishId}`);
      setDish(response.data);
    } catch (error) {
      console.error('Error fetching dish data:', error);
    } finally {
      setLoadingDish(false);
    }
  };

  const fetchReviews = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/dish/${dishId}`);
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

  return (
    <div>
      <h1>Dish Page</h1>
      {loadingDish ? (
        <p>Loading dish data...</p>
      ) : dish ? (
        <div>
          <h2>{dish.name}</h2>
          {dish.image_url && <img src={dish.image_url} alt={dish.name} />}
          <p>Allergies: {dish.allergies.join(', ')}</p>
          <p>Restrictions: {dish.restrictions.join(', ')}</p>
        </div>
      ) : (
        <p>Dish not found.</p>
      )}

      <h2>Reviews</h2>
      {loadingReviews ? (
        <p>Loading reviews...</p>
      ) : reviews.length > 0 ? (
        reviews.map((review) => (
          <div key={review.id} style={{ border: '1px solid black', marginBottom: '1em', padding: '1em' }}>
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
