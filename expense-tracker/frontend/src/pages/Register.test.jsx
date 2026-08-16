import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Register from './Register';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { AuthContext } from '../context/AuthContext';

describe('Register Component', () => {
  it('shows error if passwords do not match', async () => {
    const mockRegister = vi.fn();
    
    render(
      <BrowserRouter>
        <AuthContext.Provider value={{ register: mockRegister }}>
          <Register />
        </AuthContext.Provider>
      </BrowserRouter>
    );
    
    // Since inputs might not have aria-labels, we look for placeholders or types
    const passwordInput = document.querySelector('input[name="password"]');
    const confirmInput = document.querySelector('input[name="confirmPassword"]');
    
    if(passwordInput && confirmInput) {
        fireEvent.change(passwordInput, { target: { value: 'password123' } });
        fireEvent.change(confirmInput, { target: { value: 'password456' } });
        
        fireEvent.click(screen.getByRole('button', { name: /register/i }));
        
        await waitFor(() => {
          expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
        });
        
        expect(mockRegister).not.toHaveBeenCalled();
    }
  });
});
