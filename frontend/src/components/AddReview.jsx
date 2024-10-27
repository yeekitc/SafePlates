import { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Paper,
    Container,
    CircularProgress,
    Alert,
    Snackbar,
    Autocomplete
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

function AddReview() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [restaurants, setRestaurants] = useState([]);
    const [selectedRestaurant, setSelectedRestaurant] = useState(null);
    const [formData, setFormData] = useState({
        dish: '',
        image: null,
        restrictions: '',
        comment: ''
    });

    const axiosWithAuth = axios.create({
        baseURL: API_BASE_URL,
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    });

    // Search restaurants when user types
    useEffect(() => {
        const searchRestaurants = async () => {
            if (searchTerm.length < 2) {
                setRestaurants([]);
                return;
            }

            try {
                const response = await axiosWithAuth.get('/restaurants/search-db/', {
                    params: {
                        name: searchTerm,
                        limit: 5
                    }
                });
                setRestaurants(response.data);
            } catch (err) {
                console.error('Error searching restaurants:', err);
            }
        };

        const timeoutId = setTimeout(searchRestaurants, 500);
        return () => clearTimeout(timeoutId);
    }, [searchTerm]);

    const handleInputChange = (e) => {
        const { name, value, files } = e.target;
        if (name === 'image' && files) {
            setFormData(prev => ({
                ...prev,
                image: files[0]
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedRestaurant) {
            setError('Please select a restaurant');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Please login to submit a review');
            }

            let restaurantId = null;
            
            // 1. Check if restaurant exists and get/create it
            const restaurantResponse = await axiosWithAuth.get(`/restaurants/id/${selectedRestaurant.id}`);
            if (restaurantResponse.data) {
                restaurantId = restaurantResponse.data.id;
            } 
            // else {
            //     // Create restaurant if it doesn't exist
            //     const newRestaurantResponse = await axiosWithAuth.post('/restaurants/', {
            //         google_data: selectedRestaurant
            //     });
            //     restaurantId = newRestaurantResponse.data.id;
            // }

            // 2. Check if dish exists
            const dishResponse = await axiosWithAuth.get(`/dishes/search/`, {
                params: {
                    name: formData.dish,
                    restaurant_id: restaurantId
                }
            });

            console.log("dish", dishResponse);
            console.log("restaurant", restaurantResponse);

            let dishId;
            
            // 3. If dish doesn't exist, create it
            if (!dishResponse.data) {
                // Handle image upload first if there's an image
                let imageUrl = '';
                if (formData.image) {
                    const formDataImg = new FormData();
                    formDataImg.append('file', formData.image);  // Changed 'image' to 'file'
                    
                    const imageResponse = await axiosWithAuth.post('/upload', formDataImg, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    imageUrl = imageResponse.data.url;
                }

                const dishCreateResponse = await axiosWithAuth.post('/dishes/', {
                    name: formData.dish,
                    image_url: imageUrl,
                    restaurant_id: restaurantId,
                    restrictions: formData.restrictions.split(',').map(r => r.trim()),
                    reviews: []
                });

                dishId = dishCreateResponse.data.id;
            } else {
                dishId = dishResponse.data.id;
            }

            // 4. Create the review
            await axiosWithAuth.post('/reviews/', {
                dish_id: dishId,
                restaurant_id: restaurantId,
                restrictions: formData.restrictions.split(',').map(r => r.trim()),
                comment: formData.comment
            });

            setSuccess(true);
            setTimeout(() => {
                navigate(`/restaurants/${selectedRestaurant.id}`);
            }, 2000);

        } catch (err) {
            console.error('Error submitting review:', err);
            setError(err.response?.data?.detail || err.message || 'Failed to submit review');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="md">
            <Box sx={{ py: 4 }}>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
                    <Typography variant="h3" component="h1" sx={{ mr: 2 }}>
                        Add Review
                    </Typography>
                </Box>

                {/* Form */}
                <Paper sx={{ p: 4 }}>
                    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                        {/* Restaurant Search */}
                        <Autocomplete
                            fullWidth
                            options={restaurants}
                            getOptionLabel={(option) => option.name || ''}                            
                            onChange={(_, newValue) => setSelectedRestaurant(newValue)}
                            onInputChange={(_, newInputValue) => setSearchTerm(newInputValue)}
                            renderInput={(params) => (
                                <TextField
                                    {...params}
                                    label="Search Restaurant"
                                    required
                                    placeholder="Start typing restaurant name..."
                                />
                            )}
                            renderOption={(props, option) => (
                                <Box component="li" {...props}>
                                    <Box>
                                        <Typography variant="body1">
                                            {option.name}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            {option.google_data?.address}
                                        </Typography>
                                    </Box>
                                </Box>
                            )}
                        />

                        {/* Dish Name */}
                        <TextField
                            required
                            fullWidth
                            name="dish"
                            label="Dish"
                            placeholder="Input a dish!"
                            variant="outlined"
                            value={formData.dish}
                            onChange={handleInputChange}
                        />

                        {/* Image Upload */}
                        <TextField
                            fullWidth
                            type="file"
                            name="image"
                            label="Image of the Dish"
                            InputLabelProps={{ shrink: true }}
                            variant="outlined"
                            onChange={handleInputChange}
                        />

                        {/* Dietary Restrictions */}
                        <TextField
                            fullWidth
                            name="restrictions"
                            label="NOT Friendly to..."
                            placeholder="All the dietary restrictions that this dish works with!"
                            variant="outlined"
                            multiline
                            rows={2}
                            value={formData.restrictions}
                            onChange={handleInputChange}
                        />

                        {/* Comments */}
                        <TextField
                            required
                            fullWidth
                            name="comment"
                            label="Comments"
                            placeholder="How was your experience? Let us know!"
                            variant="outlined"
                            multiline
                            rows={4}
                            value={formData.comment}
                            onChange={handleInputChange}
                        />

                        <Button
                            type="submit"
                            variant="contained"
                            disabled={loading}
                            sx={{
                                backgroundColor: '#F3B829',
                                color: 'black',
                                '&:hover': {
                                    backgroundColor: '#d69f23'
                                }
                            }}
                        >
                            {loading ? <CircularProgress size={24} /> : 'Add Review'}
                        </Button>
                    </Box>
                </Paper>
            </Box>

            <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError('')}>
                <Alert severity="error" onClose={() => setError('')}>
                    {error}
                </Alert>
            </Snackbar>

            <Snackbar open={success} autoHideDuration={6000} onClose={() => setSuccess(false)}>
                <Alert severity="success" onClose={() => setSuccess(false)}>
                    Review submitted successfully!
                </Alert>
            </Snackbar>
        </Container>
    );
}

export default AddReview;