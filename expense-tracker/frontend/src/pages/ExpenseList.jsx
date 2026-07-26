import React, { useState, useEffect } from 'react';
import { expensesApi, categoriesApi } from '../services/api';
import { Link, useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';

const ExpenseList = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filterCategory, setFilterCategory] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [expenseToDelete, setExpenseToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchExpenses();
  }, [filterCategory]);

  const fetchCategories = async () => {
    try {
      const res = await categoriesApi.getAll();
      setCategories(res.data);
    } catch (err) {
      console.error('Failed to load categories', err);
    }
  };

  const fetchExpenses = async () => {
    setIsLoading(true);
    try {
      const res = await expensesApi.getAll(0, 50, filterCategory || null);
      setExpenses(res.data);
    } catch (err) {
      setError('Failed to fetch expenses');
    } finally {
      setIsLoading(false);
    }
  };

  const requestDelete = (id) => {
    setExpenseToDelete(id);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!expenseToDelete) return;
    setIsDeleting(true);
    try {
      await expensesApi.delete(expenseToDelete);
      setExpenses((prev) => prev.filter((exp) => exp.id !== expenseToDelete));
      setShowDeleteModal(false);
      setExpenseToDelete(null);
      toast.success('Expense deleted successfully');
    } catch (err) {
      toast.error('Failed to delete expense');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent">
      
      <main className="py-10">
        <div className="mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="sm:flex sm:items-center">
            <div className="sm:flex-auto">
              <h1 className="text-2xl font-semibold leading-6 text-gray-900">Transactions</h1>
              <p className="mt-2 text-sm text-gray-700">
                A list of all your recorded expenses.
              </p>
            </div>
            <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex items-center gap-4">
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              
              <Link
                to="/add"
                className="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Add expense
              </Link>
            </div>
          </div>
          
          <div className="mt-8 flow-root">
            <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Date</th>
                        <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Description</th>
                        <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                        <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Amount</th>
                        <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {isLoading ? (
                        <tr>
                          <td colSpan="5" className="py-4 text-center text-sm text-gray-500">Loading expenses...</td>
                        </tr>
                      ) : expenses.length === 0 ? (
                        <tr>
                          <td colSpan="5" className="py-4 text-center text-sm text-gray-500">No expenses found.</td>
                        </tr>
                      ) : (
                        expenses.map((expense) => (
                          <tr key={expense.id}>
                            <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 sm:pl-6">
                              {new Date(expense.created_at).toLocaleDateString()}
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{expense.description}</td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                              <span
                                className="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset"
                                style={{
                                  backgroundColor: expense.category?.color ? `${expense.category.color}20` : '#f3f4f6',
                                  color: expense.category?.color || '#374151',
                                  borderColor: expense.category?.color ? `${expense.category.color}40` : '#d1d5db'
                                }}
                              >
                                {expense.category?.icon && <span className="mr-1">{expense.category.icon}</span>}
                                {expense.category?.name || 'Uncategorized'}
                              </span>
                            </td>
                            <td className="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">
                              ${expense.amount.toFixed(2)}
                            </td>
                            <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                              <button
                                onClick={() => navigate(`/edit/${expense.id}`)}
                                className="text-indigo-600 hover:text-indigo-900 mr-4"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => requestDelete(expense.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Custom Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">

            {/* Background overlay */}
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity backdrop-blur-sm" aria-hidden="true" onClick={() => setShowDeleteModal(false)}></div>

            <span className="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>

            {/* Modal panel */}
            <div className="inline-block transform overflow-hidden rounded-xl bg-white text-left align-bottom shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:align-middle">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Delete Expense</h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Are you sure you want to delete this expense? This action cannot be undone.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button
                  type="button"
                  disabled={isDeleting}
                  onClick={confirmDelete}
                  className="inline-flex w-full justify-center rounded-lg border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 transition-colors"
                >
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </button>
                <button
                  type="button"
                  disabled={isDeleting}
                  onClick={() => setShowDeleteModal(false)}
                  className="mt-3 inline-flex w-full justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ExpenseList;
