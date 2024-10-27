import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

const MovieSearch = () => {
  const [movies, setMovies] = useState([]);
  const [searchTitle, setSearchTitle] = useState("");
  const [loading, setLoading] = useState(false);

  const searchMovies = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/movies/search/`, {
        params: { title: searchTitle, limit: 10 },
      });
      setMovies(response.data);
    } catch (error) {
      console.error("Error searching:", error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8 flex justify-center">
        <input
          type="text"
          value={searchTitle}
          onChange={(e) => setSearchTitle(e.target.value)}
          placeholder="Search for a movie..."
          className="border p-2 rounded-md mr-2 w-full max-w-md"
        />
        <button
          onClick={searchMovies}
          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          Search
        </button>
      </div>

      {loading ? (
        <p className="text-center">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {movies.length > 0 ? (
            movies.map((movie) => (
              <div key={movie.id} className="bg-white p-4 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold">{movie.title}</h2>
                <p className="text-sm text-gray-600">Year: {movie.year || "N/A"}</p>
                <p className="text-sm mt-2">{movie.plot || "No plot available."}</p>
                {movie.cast && movie.cast.length > 0 && (
                  <p className="text-sm mt-2">
                    <strong>Cast:</strong> {movie.cast.join(", ")}
                  </p>
                )}
              </div>
            ))
          ) : (
            <p className="text-center col-span-3">No movies found.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default MovieSearch;