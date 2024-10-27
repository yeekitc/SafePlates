import { useState } from 'react'
import axios from 'axios'

const RestaurantSearch = () => {
    const [restaurantSearchTitle, setRestaurantSearchTitle] = useState("");
    const [restaurants, setRestaurants] = useState([]);
    const [loading, setLoading] = useState(false);
    const API_BASE_URL = "http://127.0.0.1:8000"

    const searchRestaurants = async () => {
        setLoading(true);
        try {
          const response = await axios.get(`${API_BASE_URL}/restaurants/search/`, {
            params: { town: "college park, md", name: "QU JAPAN", limit: 10 },
          });
          console.log(response);
          setRestaurants(response.data);
        } catch (error) {
          console.error("Error searching:", error);
        }
        setLoading(false);
      }


    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <h1 className="text-2xl font-bold text-center mb-4">Restaurant Database</h1>
            <div className="mb-4 flex justify-center">
            {/* <input
                type="text"
                value={restaurantSearchTitle}
                onChange={(e) => setRestaurantSearchTitle(e.target.value)}
                placeholder="Search for a restaurant..."
                className="border p-2 rounded-md mr-2"
            /> */}
            <button
                onClick={searchRestaurants}
                className="bg-blue-500 text-white px-4 py-2 rounded-md"
            >
                Search
            </button>
            </div>
            {loading ? (
            <p className="text-center">Loading...</p>
            ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {restaurants.length > 0 ? (
                restaurants.map((restaurant) => (
                    <div key={restaurant.id} className="bg-white p-4 rounded-lg shadow-md">
                    <h2 className="text-xl font-semibold">{restaurant.displayName ? restaurant.displayName.text : "No restaurant display name"}</h2>
                    <p className="text-sm mt-2">
                        {restaurant.formattedAddress || "No address available."}
                    </p>
                    </div>
                ))
                ) : (
                <p className="text-center">No restaurants found.</p>
                )}
            </div>
            )}
        </div>
    )
}

export default RestaurantSearch