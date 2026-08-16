import React from 'react';
import { render, screen } from '@testing-library/react';
import { FeatureFlagProvider, useFeatureFlag } from './FeatureFlagContext';
import { describe, it, expect, vi } from 'vitest';
import useAuth from '../hooks/useAuth';

vi.mock('../hooks/useAuth');

const TestComponent = ({ flag }) => {
  const isEnabled = useFeatureFlag(flag);
  return <div data-testid="flag-status">{isEnabled ? 'enabled' : 'disabled'}</div>;
};

describe('FeatureFlagContext', () => {
  it('returns default false for unknown flags', () => {
    useAuth.mockReturnValue({ user: null });
    
    render(
      <FeatureFlagProvider>
        <TestComponent flag="unknown_flag" />
      </FeatureFlagProvider>
    );
    
    expect(screen.getByTestId('flag-status')).toHaveTextContent('disabled');
  });

  it('merges user specific flags', () => {
    useAuth.mockReturnValue({ 
      user: { features_enabled: { 'new_dashboard': true, 'data_export': true } } 
    });
    
    render(
      <FeatureFlagProvider>
        <TestComponent flag="new_dashboard" />
        <TestComponent flag="receipt_scanning" />
      </FeatureFlagProvider>
    );
    
    const statuses = screen.getAllByTestId('flag-status');
    expect(statuses[0]).toHaveTextContent('enabled'); // new_dashboard
    expect(statuses[1]).toHaveTextContent('disabled'); // receipt_scanning default is false
  });
});
