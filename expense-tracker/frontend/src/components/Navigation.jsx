import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Navigation = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = React.useRef(null);
  const navigate = useNavigate();

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          <div className="flex flex-shrink-0 items-center cursor-pointer" onClick={() => navigate('/')}>
            <h1 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              ExpenseTracker
            </h1>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:space-x-8 flex-1 pl-8">
            <Link
              to="/"
              className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
            >
              Dashboard
            </Link>
            <Link
              to="/expenses"
              className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
            >
              Transactions
            </Link>
          </div>
          
          <div className="flex items-center">
            {/* User Profile Dropdown */}
            <div 
              className="relative ml-3"
              ref={dropdownRef}
            >
              <button 
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center max-w-xs rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-md transition-transform hover:scale-105">
                  {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
              </button>

              {/* Dropdown Menu - shows on click */}
              {isOpen && (
                <div className="absolute right-0 z-10 mt-1 w-56 origin-top-right rounded-xl bg-white py-1 shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none transition-all duration-200 ease-in-out">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-semibold text-gray-900 truncate">{user?.full_name || user?.username}</p>
                    <p className="text-xs text-gray-500 truncate mt-1">{user?.email}</p>
                  </div>
                  <Link
                    to="/profile"
                    onClick={() => setIsOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                  >
                    Your Profile
                  </Link>
                  <button
                    onClick={logout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
