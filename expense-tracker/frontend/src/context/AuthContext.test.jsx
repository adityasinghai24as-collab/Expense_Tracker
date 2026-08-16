import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthContext, AuthProvider } from './AuthContext';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../services/api';

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  setAccessToken: vi.fn(),
}));

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const TestComponent = () => {
    const auth = React.useContext(AuthContext);
    if (auth.isLoading) return <div>Loading...</div>;
    return (
      <div>
        <div data-testid="auth-status">{auth.isAuthenticated ? 'Logged In' : 'Logged Out'}</div>
        <div data-testid="user-email">{auth.user?.email}</div>
      </div>
    );
  };

  it('attempts to refresh token on mount and sets user on success', async () => {
    api.post.mockResolvedValueOnce({ data: { access_token: 'fake-token' } });
    api.get.mockResolvedValueOnce({ data: { email: 'test@example.com' } });

    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Logged In');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    expect(api.post).toHaveBeenCalledWith('/auth/refresh');
    expect(api.get).toHaveBeenCalledWith('/auth/me');
  });

  it('handles refresh failure gracefully (stays logged out)', async () => {
    api.post.mockRejectedValueOnce(new Error('Unauthorized'));

    render(
      <BrowserRouter>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Logged Out');
    });

    expect(api.post).toHaveBeenCalledWith('/auth/refresh');
    expect(api.get).not.toHaveBeenCalled();
  });
});
