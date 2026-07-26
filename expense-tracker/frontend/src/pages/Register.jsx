// Task 16 - Login and Register Pages (Completed)
import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import OtpInput from '../components/OtpInput';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isOtpSent, setIsOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [resendTimer, setResendTimer] = useState(60);
  const { register, verifyOtp, resendOtp, isAuthenticated } = useAuth();

  useEffect(() => {
    let interval;
    if (isOtpSent && resendTimer > 0) {
      interval = setInterval(() => {
        setResendTimer((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isOtpSent, resendTimer]);

  // If already authenticated, redirect to dashboard
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    // Basic frontend validation for password length
    if (formData.password.length < 12) {
      setError('Password must be at least 12 characters long.');
      setIsSubmitting(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      setIsSubmitting(false);
      return;
    }

    const { confirmPassword, ...registerData } = formData;
    const result = await register(registerData);
    if (!result.success) {
      // Backend error string often comes as an array of objects if it's Pydantic validation
      if (Array.isArray(result.message)) {
        setError(result.message.map(msg => msg.msg).join(', '));
      } else {
        setError(result.message);
      }
      setIsSubmitting(false);
    } else {
      setIsOtpSent(true);
      setResendTimer(60);
      setIsSubmitting(false);
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    if (otpCode.length !== 6) {
      setError('Please enter the full 6-digit verification code.');
      setIsSubmitting(false);
      return;
    }
    
    const result = await verifyOtp(formData.email, otpCode);
    if (!result.success) {
      setError(result.message);
      setIsSubmitting(false);
    }
  };

  const handleResendOtp = async () => {
    setError('');
    setIsSubmitting(true);
    
    const result = await resendOtp(formData.email);
    if (result.success) {
      setResendTimer(60);
    } else {
      setError(result.message);
    }
    setIsSubmitting(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-lg">
        <div>
          <h2 className="mt-2 text-center text-3xl font-extrabold text-gray-900">
            Create an account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Start tracking your expenses today
          </p>
        </div>
        
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}

        {!isOtpSent ? (
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                placeholder="johndoe123"
                value={formData.username}
                onChange={handleChange}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="email">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="full_name">
                Full Name (Optional)
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                autoComplete="name"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                placeholder="John Doe"
                value={formData.full_name}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                placeholder="Must be at least 12 characters"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:text-sm"
                placeholder="Must match password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`group relative flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                isSubmitting ? 'cursor-not-allowed opacity-75' : ''
              }`}
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>
        </form>
        ) : (
          <form className="mt-8 space-y-6" onSubmit={handleOtpSubmit}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="otpCode">
                  Verification Code (Sent to {formData.email})
                </label>
                <div className="mt-4 flex justify-center">
                  <OtpInput length={6} value={otpCode} onChange={setOtpCode} />
                </div>
              </div>
            </div>
            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className={`group relative flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                  isSubmitting ? 'cursor-not-allowed opacity-75' : ''
                }`}
              >
                {isSubmitting ? 'Verifying...' : 'Verify OTP'}
              </button>
            </div>
            
            <div className="mt-4 text-center">
              <button
                type="button"
                disabled={resendTimer > 0 || isSubmitting}
                onClick={handleResendOtp}
                className={`text-sm font-medium ${
                  resendTimer > 0 
                    ? 'text-gray-400 cursor-not-allowed' 
                    : 'text-blue-600 hover:text-blue-500'
                }`}
              >
                {resendTimer > 0 ? `Resend OTP in ${resendTimer}s` : 'Resend OTP'}
              </button>
            </div>
          </form>
        )}

        <div className="text-center text-sm">
          <span className="text-gray-600">Already have an account? </span>
          <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
