import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const Sidebar = ({ onToggle }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const handleToggle = () => {
    const newState = !isCollapsed;
    setIsCollapsed(newState);
    if (onToggle) {
      onToggle(newState);
    }
  };
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: '📊' },
    { name: 'Transactions', path: '/expenses', icon: '💳' },
    { name: 'Add Expense', path: '/add', icon: '➕' },
  ];

  const bottomItems = [
    { name: 'Profile', path: '/profile', icon: '👤' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <div 
      className={`fixed top-0 left-0 h-screen bg-white shadow-lg border-r border-gray-100 flex flex-col transition-all duration-300 z-50 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Top Header & Hamburger */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-100">
        {!isCollapsed && (
          <h1 
            className="text-xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 cursor-pointer truncate"
            onClick={() => navigate('/')}
          >
            ExpenseTracker
          </h1>
        )}
        <button
          onClick={handleToggle}
          className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 mx-auto"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Main Nav Items */}
      <nav className="flex-1 px-3 py-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center px-3 py-3 rounded-xl transition-colors group relative ${
                isActive 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              } ${isCollapsed ? 'justify-center' : ''}`}
              title={isCollapsed ? item.name : ''}
            >
              <span className={`text-xl ${!isCollapsed && 'mr-4'}`}>{item.icon}</span>
              {!isCollapsed && (
                <span className={`font-medium ${isActive ? 'text-blue-700' : 'text-gray-700'}`}>
                  {item.name}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Profile / Settings / Logout */}
      <div className="p-3 border-t border-gray-100 space-y-2">
        {bottomItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center px-3 py-3 rounded-xl transition-colors group relative ${
                isActive 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              } ${isCollapsed ? 'justify-center' : ''}`}
              title={isCollapsed ? item.name : ''}
            >
              <span className={`text-xl ${!isCollapsed && 'mr-4'}`}>{item.icon}</span>
              {!isCollapsed && (
                <span className={`font-medium ${isActive ? 'text-blue-700' : 'text-gray-700'}`}>
                  {item.name}
                </span>
              )}
            </Link>
          );
        })}

        <button
          onClick={logout}
          className={`w-full flex items-center px-3 py-3 rounded-xl text-red-600 hover:bg-red-50 transition-colors group relative ${
            isCollapsed ? 'justify-center' : ''
          }`}
          title={isCollapsed ? 'Sign Out' : ''}
        >
          <span className={`text-xl ${!isCollapsed && 'mr-4'}`}>🚪</span>
          {!isCollapsed && <span className="font-medium">Sign Out</span>}
        </button>
        
        {/* User preview snippet if expanded */}
        {!isCollapsed && user && (
          <div className="mt-4 px-3 py-2 bg-gray-50 rounded-xl flex items-center">
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shrink-0">
              {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="ml-3 overflow-hidden">
              <p className="text-sm font-semibold text-gray-900 truncate">{user?.full_name || user?.username}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
