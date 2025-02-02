import React from 'react';
import { Link } from "react-router-dom";
import logo from '../assets/safeplates.svg';
import toast from 'react-hot-toast';

export default function NavBar() {
    const [isLoggedIn, setIsLoggedIn] = React.useState(false);

    React.useEffect(() => {
        const token = localStorage.getItem('token');
        setIsLoggedIn(!!token);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        toast.success("Successfully logged out");
        window.location.reload(); 
    };

    return (
        <nav>
            <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
                <Link to="/" className="flex items-center space-x-1 rtl:space-x-reverse">
                    <img src={logo} className="h-8" alt="SafePlates logo" />
                    <span className="self-center text-2xl font-semibold whitespace-nowrap">SafePlates</span>
                </Link>
                <button
                    data-collapse-toggle="navbar-default"
                    type="button"
                    className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
                    aria-controls="navbar-default"
                    aria-expanded="false"
                >
                    <span className="sr-only">Open main menu</span>
                    <svg
                        className="w-5 h-5"
                        aria-hidden="true"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 17 14"
                    >
                        <path
                            stroke="currentColor"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M1 1h15M1 7h15M1 13h15"
                        />
                    </svg>
                </button>
                <div className="hidden w-full md:block md:w-auto" id="navbar-default">
                    <ul className="flex flex-col md:flex-row md:space-x-4">
                        {isLoggedIn ? (
                            <>
                                <li>
                                    <Link to="/add-review" className="block py-2 px-3 md:p-0 hover:text-orange-500">
                                        Add Review
                                    </Link>
                                </li>
                                <li>
                                    <button
                                        onClick={handleLogout}
                                        className="block py-2 px-3 md:p-0 hover:text-orange-500"
                                    >
                                        Logout
                                    </button>
                                </li>
                            </>
                        ) : (
                            <>
                                <li>
                                    <Link to="/login" className="block py-2 px-3 md:p-0 hover:text-orange-500">
                                        Login
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/register" className="block py-2 px-3 md:p-0 hover:text-orange-500">
                                        Register
                                    </Link>
                                </li>
                            </>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
}