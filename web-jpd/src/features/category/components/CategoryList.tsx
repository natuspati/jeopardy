import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '@/api/client';
import axios from 'axios';
import { CategorySchema, Category } from '@/features/category/interfaces';
import { z } from 'zod';
import settings from '@/settings';
import { useAuth } from '@/features/auth/AuthContext';
import ConfirmationModal from '@/components/ConfirmationModal';

const CategoryList = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useAuth();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchCategories = async () => {
      try {
        const response = await api.get('/api/v1/category', {
          params: { name: searchTerm || undefined },
          signal: controller.signal,
        });
        const parsedCategories = z.array(CategorySchema).parse(response.data);
        setCategories(parsedCategories.slice(0, settings.maxCategoriesToShow));
      } catch (error) {
        if (axios.isCancel(error)) {
          console.log('Request canceled:', error.message);
        } else {
          console.error('Failed to fetch categories:', error);
        }
      }
    };

    if (searchTerm.length === 0 || searchTerm.length >= 2) {
      fetchCategories();
    }

    return () => {
      controller.abort();
    };
  }, [searchTerm]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTerm = e.target.value;
    setSearchTerm(newTerm);
    if (newTerm.length > 0 && newTerm.length < 2) {
      setCategories([]);
    }
  };

  const confirmDeleteCategory = (category: Category) => {
    setCategoryToDelete(category);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (categoryToDelete === null) return;
    try {
      await api.delete(`/api/v1/category/${categoryToDelete.id}`);
      setCategories((prevCategories) =>
        prevCategories.filter((cat) => cat.id !== categoryToDelete.id)
      );
      setShowDeleteModal(false);
      setCategoryToDelete(null);
    } catch (error) {
      console.error('Failed to delete category:', error);
      alert('Failed to delete category.');
      setShowDeleteModal(false);
      setCategoryToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setCategoryToDelete(null);
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Search categories by name (2+ characters)..."
        value={searchTerm}
        onChange={handleSearchChange}
        className="w-full p-2 border border-gray-300 rounded-md mb-4"
      />
      <div className="space-y-4">
        {categories.length > 0 ? (
          categories.map((category) => (
            <Link
              to={`/categories/${category.id}`}
              key={category.id}
              className={`p-4 rounded-md shadow-sm flex justify-between items-center cursor-pointer ${category.is_valid ? 'bg-green-100' : 'bg-red-100'}`}
            >
              <div>
                <h3 className="text-lg font-semibold">
                  {category.name}
                  <span className="text-sm text-gray-600 font-normal ml-4">
                    Owner: {category.owner.username}
                  </span>
                  <span className="text-sm text-gray-600 font-normal ml-4">
                    Prompts: {category.prompts.length}
                  </span>
                </h3>
              </div>
              {user && user.id === category.owner.id && (
                <button
                  className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-3 rounded"
                  onClick={(e) => {
                    e.preventDefault(); // Prevent navigation
                    confirmDeleteCategory(category);
                  }}
                >
                  Delete
                </button>
              )}
            </Link>
          ))
        ) : (
          <p className="text-gray-600">No categories found.</p>
        )}
      </div>
      <ConfirmationModal
        isOpen={showDeleteModal}
        message={`Are you sure you want to delete the category "${categoryToDelete?.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
};

export default CategoryList;
