// Task 26 - Build the Core Pages (Completed)
import React, { useState, useEffect } from 'react';
import { expensesApi } from '../services/api';
import { useFeatureFlag } from '../context/FeatureFlagContext';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [expenses, setExpenses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Feature Flags
  const canScanReceipts = useFeatureFlag('receipt_scanning');
  const canExportData = useFeatureFlag('data_export');

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      const res = await expensesApi.getAll(0, 100); // Fetch up to 100 recent for dashboard stats
      setExpenses(res.data);
    } catch (err) {
      console.error('Failed to load expenses for dashboard', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Compute stats
  const totalExpenses = expenses.reduce((acc, exp) => acc + exp.amount, 0);
  
  // Group by category
  const expensesByCategory = expenses.reduce((acc, exp) => {
    const catName = exp.category?.name || 'Uncategorized';
    const catColor = exp.category?.color || '#9ca3af'; // default gray
    const catIcon = exp.category?.icon || '';
    
    if (!acc[catName]) {
      acc[catName] = { amount: 0, color: catColor, icon: catIcon };
    }
    acc[catName].amount += exp.amount;
    return acc;
  }, {});

  const categoryArray = Object.entries(expensesByCategory).map(([name, data]) => ({
    name,
    amount: data.amount,
    color: data.color,
    icon: data.icon,
    percentage: totalExpenses > 0 ? (data.amount / totalExpenses) * 100 : 0
  })).sort((a, b) => b.amount - a.amount);

  const recentTransactions = expenses.slice(0, 5); // top 5

  return (
    <div className="min-h-screen bg-transparent">
      <main className="py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          
          <div className="sm:flex sm:items-center sm:justify-between mb-8">
            <h1 className="text-3xl font-bold leading-tight tracking-tight text-gray-900">Dashboard</h1>
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <button 
                disabled={!canExportData}
                className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                title={!canExportData ? "Feature disabled. Upgrade required." : "Export to CSV"}
              >
                Export Data {!canExportData && '🔒'}
              </button>
              <button 
                disabled={!canScanReceipts}
                className="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                title={!canScanReceipts ? "Feature disabled. Upgrade required." : "Scan a receipt"}
              >
                Scan Receipt {!canScanReceipts && '🔒'}
              </button>
              <Link
                to="/add"
                className="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Add Expense
              </Link>
            </div>
          </div>

          {isLoading ? (
            <p className="text-gray-500">Loading dashboard...</p>
          ) : (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              
              {/* Total Card */}
              <div className="overflow-hidden rounded-lg bg-white shadow">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <span className="text-3xl">💰</span>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="truncate text-sm font-medium text-gray-500">Total Expenses</dt>
                        <dd>
                          <div className="text-3xl font-semibold text-gray-900">${totalExpenses.toFixed(2)}</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              {/* Breakdown Card */}
              <div className="lg:col-span-2 overflow-hidden rounded-lg bg-white shadow">
                <div className="p-5">
                  <h3 className="text-base font-semibold leading-6 text-gray-900 mb-4">Category Breakdown</h3>
                  
                  {categoryArray.length === 0 ? (
                    <p className="text-sm text-gray-500">No expenses yet.</p>
                  ) : (
                    <div className="space-y-4">
                      {categoryArray.map(cat => (
                        <div key={cat.name}>
                          <div className="flex items-center justify-between text-sm mb-1">
                            <span className="font-medium text-gray-700">
                              {cat.icon && <span className="mr-1">{cat.icon}</span>}
                              {cat.name}
                            </span>
                            <span className="text-gray-500">${cat.amount.toFixed(2)} ({cat.percentage.toFixed(1)}%)</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div 
                              className="h-2.5 rounded-full" 
                              style={{ width: `${cat.percentage}%`, backgroundColor: cat.color }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Recent Transactions Table */}
              <div className="lg:col-span-3 overflow-hidden rounded-lg bg-white shadow">
                <div className="p-5 border-b border-gray-200 sm:flex sm:items-center sm:justify-between">
                  <h3 className="text-base font-semibold leading-6 text-gray-900">Recent Transactions</h3>
                  <Link to="/expenses" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">
                    View all
                  </Link>
                </div>
                <ul className="divide-y divide-gray-200">
                  {recentTransactions.length === 0 ? (
                    <li className="px-5 py-4 text-sm text-gray-500">No transactions to show.</li>
                  ) : (
                    recentTransactions.map((expense) => (
                      <li key={expense.id} className="px-5 py-4 flex justify-between items-center hover:bg-gray-50">
                        <div className="flex flex-col">
                          <span className="text-sm font-medium text-gray-900">{expense.description}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(expense.created_at).toLocaleDateString()} &middot; {expense.category?.icon && <span className="mr-1">{expense.category.icon}</span>}{expense.category?.name || 'Uncategorized'}
                          </span>
                        </div>
                        <span className="text-sm font-semibold text-gray-900">${expense.amount.toFixed(2)}</span>
                      </li>
                    ))
                  )}
                </ul>
              </div>

            </div>
          )}

        </div>
      </main>
    </div>
  );
};

export default Dashboard;
