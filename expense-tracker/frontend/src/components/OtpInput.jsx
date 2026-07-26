import React, { useState, useRef, useEffect } from 'react';

const OtpInput = ({ length = 6, value = '', onChange }) => {
  const [otp, setOtp] = useState(new Array(length).fill(''));
  const inputRefs = useRef([]);

  useEffect(() => {
    // If value prop changes externally (e.g., reset), sync it
    if (value === '') {
      setOtp(new Array(length).fill(''));
    } else if (value && value.length <= length) {
      const newOtp = value.split('').concat(new Array(length - value.length).fill(''));
      setOtp(newOtp);
    }
  }, [value, length]);

  const handleChange = (e, index) => {
    const val = e.target.value;
    if (isNaN(val)) return;

    const newOtp = [...otp];
    // Allow only the last entered character if multiple are somehow typed
    newOtp[index] = val.substring(val.length - 1);
    setOtp(newOtp);

    const otpString = newOtp.join('');
    onChange(otpString);

    // Focus next input
    if (val && index < length - 1 && inputRefs.current[index + 1]) {
      inputRefs.current[index + 1].focus();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      const newOtp = [...otp];

      if (otp[index]) {
        // Clear current input
        newOtp[index] = '';
        setOtp(newOtp);
        onChange(newOtp.join(''));
      } else if (index > 0) {
        // Move to previous and clear it
        newOtp[index - 1] = '';
        setOtp(newOtp);
        onChange(newOtp.join(''));
        if (inputRefs.current[index - 1]) {
          inputRefs.current[index - 1].focus();
        }
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      e.preventDefault();
      inputRefs.current[index - 1].focus();
    } else if (e.key === 'ArrowRight' && index < length - 1) {
      e.preventDefault();
      inputRefs.current[index + 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text/plain').slice(0, length).replace(/\D/g, '');
    if (!pastedData) return;

    const newOtp = [...otp];
    let focusIndex = 0;

    for (let i = 0; i < length; i++) {
      if (i < pastedData.length) {
        newOtp[i] = pastedData[i];
        focusIndex = i;
      }
    }

    setOtp(newOtp);
    onChange(newOtp.join(''));

    // Focus the next empty input, or the last one if full
    if (focusIndex < length - 1) {
      inputRefs.current[focusIndex + 1].focus();
    } else {
      inputRefs.current[length - 1].focus();
    }
  };

  return (
    <div className="flex justify-between gap-2 sm:gap-3">
      {otp.map((data, index) => (
        <input
          key={index}
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength="1"
          ref={(el) => (inputRefs.current[index] = el)}
          value={data}
          onChange={(e) => handleChange(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onPaste={handlePaste}
          className="w-10 h-12 sm:w-12 sm:h-14 text-center text-xl sm:text-2xl font-bold text-gray-900 bg-white border-2 border-gray-300 rounded-lg shadow-sm focus:border-blue-600 focus:ring-2 focus:ring-blue-600 focus:outline-none transition-all duration-200"
        />
      ))}
    </div>
  );
};

export default OtpInput;
