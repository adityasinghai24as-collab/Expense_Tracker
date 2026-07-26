import React, { createContext, useContext } from 'react';
import useAuth from '../hooks/useAuth';

export const FeatureFlagContext = createContext({});

export const FeatureFlagProvider = ({ children }) => {
  const { user } = useAuth();
  
  // Combine defaults with user specific flags if any
  const defaultFlags = {
    receipt_scanning: false,
    data_export: false
  };

  const features = {
    ...defaultFlags,
    ...(user?.features_enabled || {})
  };

  return (
    <FeatureFlagContext.Provider value={features}>
      {children}
    </FeatureFlagContext.Provider>
  );
};

export const useFeatureFlag = (flagName) => {
  const features = useContext(FeatureFlagContext);
  return features[flagName] || false;
};
