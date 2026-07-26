import React, { useState, useEffect } from 'react';
import { expensesApi, categoriesApi } from '../services/api';
import CategoryManager from '../components/CategoryManager';
import { useNavigate, useParams } from 'react-router-dom';
import { useToast } from '../context/ToastContext';

const EditExpense = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    category_id: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, [id]);

  const fetchInitialData = async () => {
    setIsLoading(true);
    try {
      const [categoriesRes, expenseRes] = await Promise.all([
        categoriesApi.getAll(),
        expensesApi.getById(id)
      ]);
      
      setCategories(categoriesRes.data);
      
      const exp = expenseRes.data;
      setFormData({
        amount: exp.amount,
        description: exp.description,
        category_id: exp.category_id || '',
      });
    } catch (err) {
      setError('Failed to load expense data.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCategoryAdded = (newCategory) => {
    setCategories((prev) => [...prev, newCategory]);
    setFormData((prev) => ({ ...prev, category_id: newCategory.id }));
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

      await expensesApi.update(id, payload);
      toast.success('Expense updated successfully!');
      navigate('/expenses'); // Redirect to expenses list on success
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update expense');
      toast.error('Failed to update expense');
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent">
      <main className="py-10">
        <div className="mx-auto max-w-3xl sm:px-6 lg:px-8">
          <div className="bg-white overflow-hidden shadow-sm sm:rounded-lg">
            <div className="p-6 bg-white border-b border-gray-200">
              <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight mb-6">
                Edit Expense
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
                    />
                  </div>
                </div>

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
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="category_id" className="block text-sm font-medium leading-6 text-gray-900">
                    Category
                  </label>
                  <div className="mt-2">
                    <select
                      id="category_id"
                      name="category_id"
                      value={formData.category_id}
                      onChange={handleChange}
                      className="block w-full rounded-md border-0 py-2 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-white"
                    >
                      <option value="">Select a category...</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="mt-3">
                    <CategoryManager onCategoryAdded={handleCategoryAdded} />
                  </div>
                </div>

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
                    {isSubmitting ? 'Saving...' : 'Update Expense'}
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

export default EditExpense;
