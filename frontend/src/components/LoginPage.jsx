import React from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const API_BASE_URL = "http://127.0.0.1:8000";

export default function LoginPage() {
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [isLoggedIn, setIsLoggedIn] = React.useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${API_BASE_URL}/login`, { email, password });
            localStorage.setItem('token', response.data.access_token);
            setIsLoggedIn(true); // Update the state to reflect the login status
            navigate('/');
            toast.success('Login successful');
        } catch (error) {
            console.error('Login error:', error);
            toast.error('Invalid credentials');
        }
    };

    return (
        <div className="min-h-screen flex mt-52 justify-center py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="text-center text-3xl font-extrabold text-gray-900">
                        Sign in to your account
                    </h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="rounded-md shadow-sm space-y-4">
                        <div>
                            <label htmlFor="email" className="sr-only">Email address</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-orange-500 focus:border-yorange focus:z-10 sm:text-sm"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-yorange focus:border-yorange focus:z-10 sm:text-sm"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>
                    <div>
                        <button
                            type="submit"
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-yorange hover:bg-yorange focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yorange"
                        >
                            Sign in
                        </button>
                    </div>
                </form>
                {isLoggedIn && <p className="text-green-500 text-center mt-4">You are logged in!</p>}
            </div>
        </div>
    );
}