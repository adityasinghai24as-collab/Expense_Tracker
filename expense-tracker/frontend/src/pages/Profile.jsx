import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import { useToast } from '../context/ToastContext';

const Profile = () => {
  const { user, updateProfile, deleteAccount } = useAuth();
  const toast = useToast();

  const [formData, setFormData] = useState({
    full_name: '',
    username: ''
  });

  const [isEditing, setIsEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        username: user.username || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    if (user) {
      setFormData({
        full_name: user.full_name || '',
        username: user.username || ''
      });
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setIsUpdating(true);

    const result = await updateProfile(formData);

    if (result.success) {
      toast.success('Profile updated successfully!');
      setIsEditing(false);
    } else {
      toast.error(result.message);
    }

    setIsUpdating(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    const result = await deleteAccount();
    if (!result.success) {
      toast.error(result.message);
      setShowDeleteModal(false);
      setIsDeleting(false);
    }
  };


  return (
    <div className="min-h-screen bg-transparent">

      <main className="mx-auto max-w-3xl py-10 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-10 text-white flex items-center space-x-6">
            <div className="h-24 w-24 rounded-full bg-white/20 flex items-center justify-center text-4xl font-bold backdrop-blur-sm border-2 border-white/40 shadow-inner">
              {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <h1 className="text-3xl font-bold">{user?.full_name || user?.username}</h1>
              <p className="text-blue-100 mt-1">{user?.email}</p>
            </div>
          </div>

            <div className="p-8">
              <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-800">Personal Information</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
                >
                  <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                  </svg>
                  Edit Profile
                </button>
              )}
            </div>

            <form onSubmit={handleUpdate} className="space-y-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">Full Name</label>
                  <input
                    type="text"
                    name="full_name"
                    id="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={`mt-1 block w-full rounded-lg shadow-sm sm:text-sm px-4 py-2 border transition-colors ${isEditing
                        ? 'border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white'
                        : 'border-transparent bg-gray-50 text-gray-800 cursor-default font-medium'
                      }`}
                  />
                </div>
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-500">Username</label>
                  <input
                    type="text"
                    name="username"
                    id="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    disabled={!isEditing}
                    className={`mt-1 block w-full rounded-lg shadow-sm sm:text-sm px-4 py-2 border transition-colors ${isEditing
                        ? 'border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white'
                        : 'border-transparent bg-gray-50 text-gray-800 cursor-default font-medium'
                      }`}
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block text-sm font-medium text-gray-500">Email Address (Read Only)</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="mt-1 block w-full rounded-lg border-transparent bg-gray-50 text-gray-800 font-medium shadow-sm sm:text-sm px-4 py-2 border cursor-not-allowed"
                  />
                </div>
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    disabled={isUpdating}
                    className="inline-flex justify-center rounded-lg border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isUpdating}
                    className="inline-flex justify-center rounded-lg border border-transparent bg-blue-600 py-2 px-6 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
                  >
                    {isUpdating ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              )}
            </form>


            {/* Danger Zone */}
            <div className="mt-12 pt-8 border-t border-red-100">
              <h3 className="text-lg font-medium text-red-600">Danger Zone</h3>
              <p className="mt-1 text-sm text-gray-500">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowDeleteModal(true)}
                  className="inline-flex justify-center rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-600 shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
                >
                  Delete Account
                </button>
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
                    <h3 className="text-lg font-medium leading-6 text-gray-900">Delete Account</h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Are you absolutely sure you want to delete your account? All of your data, including expenses and categories, will be permanently removed. This action cannot be undone.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button
                  type="button"
                  disabled={isDeleting}
                  onClick={handleDelete}
                  className="inline-flex w-full justify-center rounded-lg border border-transparent bg-red-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 transition-colors"
                >
                  {isDeleting ? 'Deleting...' : 'Yes, Delete Account'}
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

export default Profile;
