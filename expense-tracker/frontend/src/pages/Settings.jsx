import React, { useState } from 'react';
import useAuth from '../hooks/useAuth';
import { useToast } from '../context/ToastContext';

const Settings = () => {
  const { user, updateProfile } = useAuth();
  const toast = useToast();
  const [isUpdating, setIsUpdating] = useState(false);

  const getPlanDetails = () => {
    switch (user?.role) {
      case 'admin':
        return { name: 'Administrator', desc: 'Full system access' };
      case 'pro':
        return { name: 'Pro Plan', desc: 'Premium features enabled' };
      default:
        return { name: 'Standard User', desc: 'Basic features only' };
    }
  };

  const plan = getPlanDetails();

  return (
    <div className="min-h-screen bg-transparent">
      <main className="mx-auto max-w-3xl py-10 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          
          <div className="bg-gradient-to-r from-gray-700 to-gray-900 px-8 py-8 text-white">
            <h1 className="text-3xl font-bold">Settings & Plan</h1>
            <p className="text-gray-300 mt-1">Manage your application preferences and view your current plan</p>
          </div>

          <div className="p-8">
            <div className="mb-10 p-6 bg-blue-50 border border-blue-100 rounded-xl flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-blue-900">Current Plan: {plan.name}</h3>
                <p className="text-sm text-blue-700 mt-1">{plan.desc}</p>
              </div>
              {user?.role === 'user' && (
                <button
                  disabled
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium opacity-50 cursor-not-allowed"
                >
                  Upgrade to Pro
                </button>
              )}
            </div>

            <h3 className="text-xl font-semibold text-gray-800 mb-6">Application Features</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Enable Data Export</h4>
                  <p className="text-sm text-gray-500">Allow exporting your transaction data to CSV (Pro Feature)</p>
                </div>
                <div>
                  {user?.features_enabled?.data_export ? (
                    <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Enabled</span>
                  ) : (
                    <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Locked</span>
                  )}
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Enable Receipt Scanning</h4>
                  <p className="text-sm text-gray-500">Use AI to scan and automatically categorize receipts (Pro Feature)</p>
                </div>
                <div>
                  {user?.features_enabled?.receipt_scanning ? (
                    <span className="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Enabled</span>
                  ) : (
                    <span className="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Locked</span>
                  )}
                </div>
              </div>
            </div>
            
          </div>
        </div>
      </main>
    </div>
  );
};

export default Settings;
