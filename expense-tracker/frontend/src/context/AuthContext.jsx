// Task 15 - Auth Context and Token Management (Completed)
import React, { createContext, useState, useEffect, useCallback } from 'react';
import api, { setAccessToken } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Helper to update both React state and the Axios interceptor
  const setToken = useCallback((newToken) => {
    setTokenState(newToken);
    setAccessToken(newToken);
  }, []);

  // On app load, try to refresh the token using the HttpOnly cookie
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Attempt to get a new access token
        const response = await api.post('/auth/refresh');
        const newAccessToken = response.data.access_token;
        setToken(newAccessToken);

        // Fetch user profile
        const userResponse = await api.get('/auth/me');
        setUser(userResponse.data);
      } catch (error) {
        // Expected if the user has never logged in or the refresh token expired
        console.log("No valid session found during initialization.");
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, [setToken]);

  const login = async (username_or_email, password) => {
    try {
      const response = await api.post('/auth/login', { username_or_email, password });
      const newAccessToken = response.data.access_token;
      setToken(newAccessToken);

      // Fetch user profile immediately after login
      const userResponse = await api.get('/auth/me');
      setUser(userResponse.data);
      
      // Redirect to dashboard or home after successful login
      navigate('/');
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "Login failed" 
      };
    }
  };

  const register = async (userData) => {
    try {
      await api.post('/auth/register', userData);
      // Backend now sends an OTP. We do not auto-login here.
      return { success: true };
    } catch (error) {
      console.error("Registration failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "Registration failed" 
      };
    }
  };

  const verifyOtp = async (email, otpCode) => {
    try {
      const response = await api.post('/auth/verify-otp', { email, otp_code: otpCode });
      const newAccessToken = response.data.access_token;
      setToken(newAccessToken);

      // Fetch user profile immediately after login
      const userResponse = await api.get('/auth/me');
      setUser(userResponse.data);
      
      // Redirect to dashboard or home after successful login
      navigate('/');
      return { success: true };
    } catch (error) {
      console.error("OTP verification failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "OTP verification failed" 
      };
    }
  };

  const resendOtp = async (email) => {
    try {
      const response = await api.post('/auth/resend-otp', { email });
      return { success: true, message: response.data.message };
    } catch (error) {
      console.error("OTP resend failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "Failed to resend OTP" 
      };
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      // Always clear state and redirect even if the server request fails
      setToken(null);
      setUser(null);
      navigate('/login');
    }
  };

  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/users/me', userData);
      setUser(response.data);
      return { success: true };
    } catch (error) {
      console.error("Profile update failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "Update failed" 
      };
    }
  };

  const deleteAccount = async () => {
    try {
      await api.delete('/users/me');
      setToken(null);
      setUser(null);
      navigate('/login');
      return { success: true };
    } catch (error) {
      console.error("Account deletion failed:", error);
      return { 
        success: false, 
        message: error.response?.data?.detail || "Deletion failed" 
      };
    }
  };

  const value = {
    user,
    accessToken: token,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    register,
    verifyOtp,
    resendOtp,
    updateProfile,
    deleteAccount
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
