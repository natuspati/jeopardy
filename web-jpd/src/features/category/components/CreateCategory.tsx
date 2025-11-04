import { useState } from 'react';
import { z } from 'zod';
import api from '@/api/client';
import {
  CategorySchema,
  Category,
  CategoryCreateSchema,
  PromptCreateSchema,
  BaseCategorySchema as BackendBaseCategorySchema,
} from '@/features/category/interfaces';
import { PromptTypeEnum, PromptType } from '@/shared/enums';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const CreateCategory = () => {
  const [categoryName, setCategoryName] = useState('');
  const [createdCategory, setCreatedCategory] = useState<Category | null>(null);
  const [promptData, setPromptData] = useState({
    question: '',
    question_type: PromptTypeEnum.TEXT as PromptType,
    answer: '',
    answer_type: PromptTypeEnum.TEXT as PromptType,
    score: 100,
    order: 1,
  });
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleCreateCategory = async () => {
    try {
      const validatedData = CategoryCreateSchema.parse({ name: categoryName });
      const response = await api.post('/api/v1/category', validatedData);
      const baseCategory = BackendBaseCategorySchema.parse(response.data);
      const fullCategoryResponse = await api.get(`/api/v1/category/${baseCategory.id}`);
      const newCategory = CategorySchema.parse(fullCategoryResponse.data);
      setCreatedCategory(newCategory);
      setError(null);
      navigate(`/categories/${newCategory.id}`);
    } catch (err: unknown) {
      if (err instanceof z.ZodError) {
        setError(err.errors.map((e) => e.message).join(', '));
      } else if (axios.isAxiosError(err) && err.response) {
        setError(err.response.data.detail || 'Failed to create category');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  const handleCreatePrompt = async () => {
    if (!createdCategory) return;
    try {
      const validatedPrompt = PromptCreateSchema.parse(promptData);
      await api.post(`/api/v1/category/${createdCategory.id}/prompt`, validatedPrompt);
      const response = await api.get(`/api/v1/category/${createdCategory.id}`);
      const updatedCategory = CategorySchema.parse(response.data);
      setCreatedCategory(updatedCategory);
      setPromptData((prev) => ({
        ...prev,
        order: prev.order + 1,
        question: '',
        answer: '',
        score: 100,
      }));
      setError(null);
    } catch (err: unknown) {
      if (err instanceof z.ZodError) {
        setError(err.errors.map((e) => e.message).join(', '));
      } else if (axios.isAxiosError(err) && err.response) {
        setError(err.response.data.detail || 'Failed to create prompt');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {!createdCategory ? (
        <div>
          <h2 className="text-2xl font-bold mb-4">Create a New Category</h2>
          <input
            type="text"
            value={categoryName}
            onChange={(e) => setCategoryName(e.target.value)}
            placeholder="Enter category name"
            className="w-full p-2 border border-gray-300 rounded-md mb-4"
          />
          <button
            onClick={handleCreateCategory}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
          >
            Create
          </button>
        </div>
      ) : (
        <div>
          <h2 className="text-2xl font-bold mb-2">Category: {createdCategory.name}</h2>
          <div
            className={`p-2 rounded-md mb-4 ${createdCategory.is_valid ? 'bg-green-200 text-green-800' : 'bg-gray-200 text-gray-800'}`}
          >
            Status: {createdCategory.is_valid ? 'Complete' : 'Not Complete'}
          </div>
          <h3 className="text-xl font-bold mb-4">Add Prompt {promptData.order}</h3>
          <div className="space-y-4">
            <input
              type="text"
              value={promptData.question}
              onChange={(e) => setPromptData((p) => ({ ...p, question: e.target.value }))}
              placeholder="Question"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
            <select
              value={promptData.question_type}
              onChange={(e) =>
                setPromptData((p) => ({ ...p, question_type: e.target.value as PromptType }))
              }
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {Object.values(PromptTypeEnum).map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <input
              type="text"
              value={promptData.answer}
              onChange={(e) => setPromptData((p) => ({ ...p, answer: e.target.value }))}
              placeholder="Answer"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
            <select
              value={promptData.answer_type}
              onChange={(e) =>
                setPromptData((p) => ({ ...p, answer_type: e.target.value as PromptType }))
              }
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              {Object.values(PromptTypeEnum).map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <input
              type="number"
              value={promptData.score}
              onChange={(e) =>
                setPromptData((p) => ({ ...p, score: parseInt(e.target.value) || 0 }))
              }
              placeholder="Score"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
            <button
              onClick={handleCreatePrompt}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
            >
              Add Prompt
            </button>
          </div>
        </div>
      )}
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default CreateCategory;
