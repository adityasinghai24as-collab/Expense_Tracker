import React, { useState, useEffect, useRef } from 'react';
import { expensesApi, categoriesApi } from '../services/api';
import CategoryManager from '../components/CategoryManager';
import { detectCategory } from '../services/categoryDetector';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../context/ToastContext';

const AddExpense = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    category_id: '',
  });
  const [detectedCategory, setDetectedCategory] = useState(null);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const detectionTimeout = useRef(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await categoriesApi.getAll();
      setCategories(response.data);
    } catch (err) {
      console.error('Failed to fetch categories', err);
    }
  };

  // Auto-detect category whenever the description changes (debounced by 300ms)
  const handleDescriptionChange = (e) => {
    const value = e.target.value;
    setFormData((prev) => ({ ...prev, description: value }));

    clearTimeout(detectionTimeout.current);
    detectionTimeout.current = setTimeout(() => {
      const result = detectCategory(value, categories);
      if (result.categoryId) {
        setDetectedCategory(result);
        // Only auto-fill if user hasn't manually selected a category
        setFormData((prev) =>
          prev.category_id === '' ? { ...prev, category_id: result.categoryId } : prev
        );
      } else {
        setDetectedCategory(null);
      }
    }, 300);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear auto-detected suggestion when user manually overrides category
    if (name === 'category_id') {
      setDetectedCategory(null);
    }
  };

  const handleCategoryAdded = (newCategory) => {
    setCategories((prev) => [...prev, newCategory]);
    setFormData((prev) => ({ ...prev, category_id: newCategory.id }));
    setDetectedCategory(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      const payload = {
        amount: parseFloat(formData.amount),
        description: formData.description,
        category_id: formData.category_id ? parseInt(formData.category_id, 10) : null,
      };

      await expensesApi.create(payload);
      toast.success('Expense added successfully!');
      navigate('/expenses');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add expense');
      toast.error('Failed to add expense');
      setIsSubmitting(false);
    }
  };

  // Resolve the selected category object for display
  const selectedCategory = categories.find(
    (c) => c.id === parseInt(formData.category_id, 10)
  );

  return (
    <div className="min-h-screen bg-transparent">
      <main className="py-10">
        <div className="mx-auto max-w-3xl sm:px-6 lg:px-8">
          <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
            <div className="p-6 bg-white border-b border-gray-200">
              <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight mb-6">
                Add New Expense
              </h2>

              {error && (
                <div className="mb-4 rounded-md bg-red-50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">{error}</h3>
                    </div>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Amount */}
                <div>
                  <label htmlFor="amount" className="block text-sm font-medium leading-6 text-gray-900">
                    Amount ($)
                  </label>
                  <div className="mt-2">
                    <input
                      id="amount"
                      name="amount"
                      type="number"
                      step="0.01"
                      required
                      value={formData.amount}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                {/* Description — drives category auto-detection */}
                <div>
                  <label htmlFor="description" className="block text-sm font-medium leading-6 text-gray-900">
                    Description
                  </label>
                  <div className="mt-2">
                    <input
                      id="description"
                      name="description"
                      type="text"
                      required
                      value={formData.description}
                      onChange={handleDescriptionChange}
                      className="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                      placeholder="e.g. Lunch at Cafe, Uber to airport…"
                    />
                  </div>
                  {/* Auto-detected badge */}
                  {detectedCategory && (
                    <p className="mt-1.5 flex items-center gap-1.5 text-xs text-indigo-600 font-medium">
                      <span>✨ Auto-detected:</span>
                      <span
                        className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold text-white"
                        style={{ backgroundColor: detectedCategory.color }}
                      >
                        {detectedCategory.icon} {detectedCategory.categoryName}
                      </span>
                    </p>
                  )}
                </div>

                {/* Category selector */}
                <div>
                  <label htmlFor="category_id" className="block text-sm font-medium leading-6 text-gray-900">
                    Category
                    <span className="ml-1 text-xs font-normal text-gray-400">(auto-filled from description)</span>
                  </label>
                  <div className="mt-2 flex items-center gap-3">
                    {/* Visual icon preview */}
                    {selectedCategory && (
                      <span
                        className="flex-shrink-0 flex items-center justify-center w-9 h-9 rounded-full text-lg"
                        style={{ backgroundColor: selectedCategory.color + '20', border: `2px solid ${selectedCategory.color}` }}
                        title={selectedCategory.name}
                      >
                        {selectedCategory.icon}
                      </span>
                    )}
                    <select
                      id="category_id"
                      name="category_id"
                      value={formData.category_id}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-2 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-white"
                    >
                      <option value="">Select a category…</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.icon} {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mt-3">
                    <CategoryManager onCategoryAdded={handleCategoryAdded} />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-x-3 pt-5 border-t border-gray-900/10">
                  <button
                    type="button"
                    onClick={() => navigate('/expenses')}
                    className="text-sm font-semibold leading-6 text-gray-900"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
                  >
                    {isSubmitting ? 'Saving…' : 'Save Expense'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AddExpense;
