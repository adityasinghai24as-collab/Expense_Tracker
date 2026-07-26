import React, { useState } from 'react';
import { categoriesApi } from '../services/api';
import { getIconForCategory } from '../services/categoryDetector';

const CategoryManager = ({ onCategoryAdded }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState('');
  const [color, setColor] = useState('#3B82F6');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Derive icon automatically as the user types the name
  const autoIcon = getIconForCategory(name).icon;
  const autoColor = getIconForCategory(name).color;

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    setError('');

    // Use auto-detected icon and color; allow user to override color via color picker
    const resolvedIcon = autoIcon;
    const resolvedColor = color !== '#3B82F6' ? color : autoColor;

    try {
      const response = await categoriesApi.create({ name, color: resolvedColor, icon: resolvedIcon });
      onCategoryAdded(response.data);
      setIsOpen(false);
      setName('');
      setColor('#3B82F6');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create category');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="text-sm text-indigo-600 hover:text-indigo-500 font-medium"
      >
        + Add New Category
      </button>
    );
  }

  return (
    <div className="mt-2 p-4 bg-gray-50 border border-gray-200 rounded-md">
      <h4 className="text-sm font-medium text-gray-900 mb-3">New Category</h4>
      {error && <p className="text-sm text-red-600 mb-2">{error}</p>}

      <div className="flex items-center gap-2">
        {/* Auto icon preview */}
        <span
          className="flex-shrink-0 flex items-center justify-center w-9 h-9 rounded-full text-lg border-2"
          style={{ backgroundColor: (color !== '#3B82F6' ? color : autoColor) + '20', borderColor: color !== '#3B82F6' ? color : autoColor }}
          title="Auto-assigned icon"
        >
          {autoIcon}
        </span>

        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Category Name (e.g. Food, Travel)"
          className="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(e); }}
          required
        />

        {/* Optional: color override */}
        <input
          type="color"
          value={color !== '#3B82F6' ? color : autoColor}
          onChange={(e) => setColor(e.target.value)}
          className="h-9 w-10 p-0 border-0 rounded-md cursor-pointer"
          title="Override category color"
        />

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
        >
          {isSubmitting ? 'Saving…' : 'Save'}
        </button>
        <button
          type="button"
          onClick={() => setIsOpen(false)}
          className="text-sm font-semibold text-gray-900 px-2"
        >
          Cancel
        </button>
      </div>

      {name && (
        <p className="mt-2 text-xs text-gray-500">
          Icon auto-assigned: <span className="font-medium">{autoIcon}</span>. You can change the color above.
        </p>
      )}
    </div>
  );
};

export default CategoryManager;
