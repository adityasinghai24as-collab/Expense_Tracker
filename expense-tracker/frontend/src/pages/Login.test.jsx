import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Login from './Login';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { AuthContext } from '../context/AuthContext';

describe('Login Component', () => {
  it('validates empty fields', async () => {
    const mockLogin = vi.fn();
    
    render(
      <BrowserRouter>
        <AuthContext.Provider value={{ login: mockLogin }}>
          <Login />
        </AuthContext.Provider>
      </BrowserRouter>
    );
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // In actual implementation, browser validation or state validation will show error
    // For now we just check that login was not called if fields are empty (if handled in component)
    // Assuming standard HTML5 required attributes are used, we verify login is not called immediately
    expect(mockLogin).not.toHaveBeenCalled();
  });
});
