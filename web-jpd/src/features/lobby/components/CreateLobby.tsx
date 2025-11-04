import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/api/client';
import axios from 'axios';
import { CategorySchema, Category } from '@/features/category/interfaces';
import { z } from 'zod';
import settings from '@/settings';
import { useAuth } from '@/features/auth/AuthContext';
import { LobbySchema } from '@/features/lobby/types';

const CreateLobby = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showMineCategories, setShowMineCategories] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isCreatingLobby, setIsCreatingLobby] = useState(false);

  const minCategories = settings.minCategoriesInLobby;
  const maxCategories = settings.maxCategoriesInLobby;

  useEffect(() => {
    const controller = new AbortController();

    const fetchCategories = async () => {
      try {
        const params: { name?: string; owner_id?: string; is_valid: boolean } = {
          name: searchTerm || undefined,
          is_valid: true, // Always add is_valid: true
        };

        if (showMineCategories && user?.id) {
          params.owner_id = String(user.id);
        }

        const response = await api.get('/api/v1/category', {
          params: params,
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
  }, [searchTerm, showMineCategories, user]);

  useEffect(() => {
    if (selectedCategoryIds.length < minCategories) {
      setErrorMessage(`Please select at least ${minCategories} categories.`);
    } else if (selectedCategoryIds.length > maxCategories) {
      setErrorMessage(`You can select at most ${maxCategories} categories.`);
    } else {
      setErrorMessage('');
    }
  }, [selectedCategoryIds, minCategories, maxCategories]);

  const handleCategoryToggle = (categoryId: number) => {
    setSelectedCategoryIds((prev) => {
      if (prev.includes(categoryId)) {
        return prev.filter((id) => id !== categoryId);
      } else {
        return [...prev, categoryId];
      }
    });
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTerm = e.target.value;
    setSearchTerm(newTerm);
    if (newTerm.length > 0 && newTerm.length < 2) {
      setCategories([]);
    }
  };

  const handleToggleMineCategories = () => {
    setShowMineCategories((prev) => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (errorMessage || isCreatingLobby) {
      return;
    }

    setIsCreatingLobby(true);
    try {
      const response = await api.post<LobbySchema>('/api/v1/lobby', {
        category_ids: selectedCategoryIds,
      });
      navigate(`/lobbies/${response.data.id}`);
    } catch (error) {
      console.error('Failed to create lobby:', error);
      setErrorMessage('Failed to create lobby. Please try again.');
    } finally {
      setIsCreatingLobby(false);
    }
  };

  const isFormValid =
    !errorMessage &&
    selectedCategoryIds.length >= minCategories &&
    selectedCategoryIds.length <= maxCategories;

  return (
    <div className="container mx-auto p-4">
      {/* Removed the h1 title */}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <h2 className="text-xl font-semibold mb-2">Select Categories</h2>
          <div className="flex items-center mb-4">
            <input
              type="text"
              placeholder="Search categories by name (2+ characters)..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="flex-grow p-2 border border-gray-300 rounded-md mr-4"
            />
            {user && (
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={showMineCategories}
                  onChange={handleToggleMineCategories}
                  className="form-checkbox h-5 w-5 text-blue-600"
                />
                <span className="text-gray-900">Mine</span>
              </label>
            )}
          </div>

          {errorMessage && <p className="text-red-500 mb-4">{errorMessage}</p>}

          <div className="space-y-2 max-h-60 overflow-y-auto border p-2 rounded-md">
            {categories.length > 0 ? (
              categories.map((category) => (
                <div
                  key={category.id}
                  className={`p-3 rounded-md shadow-sm flex justify-between items-center cursor-pointer
                    ${selectedCategoryIds.includes(category.id) ? 'bg-blue-200' : 'bg-gray-100'}
                    ${!category.is_valid ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                  onClick={() => category.is_valid && handleCategoryToggle(category.id)}
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
                    {!category.is_valid && (
                      <p className="text-red-500 text-sm">
                        Category is not valid (requires {settings.numPromptInCategory} valid
                        prompts).
                      </p>
                    )}
                  </div>
                  <input
                    type="checkbox"
                    checked={selectedCategoryIds.includes(category.id)}
                    onChange={() => category.is_valid && handleCategoryToggle(category.id)}
                    className="form-checkbox h-5 w-5 text-blue-600"
                    disabled={!category.is_valid}
                  />
                </div>
              ))
            ) : (
              <p className="text-gray-600">No categories found.</p>
            )}
          </div>
        </div>

        <button
          type="submit"
          className={`w-full py-2 px-4 rounded-md text-white font-bold focus:outline-none focus:shadow-outline
            ${isFormValid ? 'bg-green-500 hover:bg-green-600' : 'bg-gray-400 cursor-not-allowed'}
            ${isCreatingLobby ? 'opacity-50 cursor-not-allowed' : ''}`}
          disabled={!isFormValid || isCreatingLobby}
        >
          {isCreatingLobby ? 'Creating Lobby...' : 'Create Lobby'}
        </button>
      </form>
    </div>
  );
};

export default CreateLobby;
