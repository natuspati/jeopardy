import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { z } from 'zod';
import api from '@/api/client';
import { CategorySchema, Category, Prompt } from '@/features/category/interfaces';
import { useAuth } from '@/features/auth/AuthContext';
import axios from 'axios';
import settings from '@/settings';
import AddPromptForm from './AddPromptForm';
import PromptItem from './PromptItem';

const EditCategory = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [category, setCategory] = useState<Category | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [showAddPrompt, setShowAddPrompt] = useState(false);

  useEffect(() => {
    const fetchCategory = async () => {
      try {
        const response = await api.get(`/api/v1/category/${id}`);
        const parsedCategory = CategorySchema.parse(response.data);
        setCategory(parsedCategory);
        setPrompts(parsedCategory.prompts);
      } catch (err: unknown) {
        if (err instanceof z.ZodError) {
          setError(err.errors.map((e) => e.message).join(', '));
        } else if (axios.isAxiosError(err) && err.response) {
          setError(err.response.data.detail || 'Failed to fetch category');
        } else {
          setError('An unexpected error occurred.');
        }
      }
    };

    if (id) {
      fetchCategory();
    }
  }, [id]);

  const isOwner = Boolean(user && category && user.id === category.owner.id);

  if (!category) {
    return <div>Loading...</div>;
  }

  const canAddPrompt = prompts.length < settings.numPromptInCategory;
  const isAddPromptButtonDisabled = !canAddPrompt || category.is_valid;

  const handleAddPromptClick = () => {
    setShowAddPrompt(true);
  };

  const handleCreatePrompt = async (question: string, answer: string, score: number) => {
    if (!id) return;
    try {
      const newPrompt = {
        question: question,
        answer: answer,
        score: score,
        order: prompts.length + 1,
        question_type: 'text',
        answer_type: 'text',
      };
      await api.post(`/api/v1/category/${id}/prompt`, newPrompt);
      const response = await api.get(`/api/v1/category/${id}`);
      const parsedCategory = CategorySchema.parse(response.data);
      setCategory(parsedCategory);
      setPrompts(parsedCategory.prompts);
      setShowAddPrompt(false);
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Failed to create prompt');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  const handleUpdatePrompt = async (
    promptId: number,
    question: string,
    answer: string,
    score: number
  ) => {
    if (!id) return;
    try {
      const updatedPrompt = {
        question: question,
        answer: answer,
        score: score,
      };
      await api.patch(`/api/v1/category/${id}/prompt/${promptId}`, updatedPrompt);
      const response = await api.get(`/api/v1/category/${id}`);
      const parsedCategory = CategorySchema.parse(response.data);
      setCategory(parsedCategory);
      setPrompts(parsedCategory.prompts);
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Failed to update prompt');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  const handleDeletePrompt = async (promptId: number) => {
    if (!id) return;
    try {
      await api.delete(`/api/v1/category/${id}/prompt/${promptId}`);
      const response = await api.get(`/api/v1/category/${id}`);
      const parsedCategory = CategorySchema.parse(response.data);
      setCategory(parsedCategory);
      setPrompts(parsedCategory.prompts);
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Failed to delete prompt');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  const handleMovePrompt = async (promptId: number, direction: 'up' | 'down') => {
    if (!id) return;

    const currentPromptIndex = prompts.findIndex((p) => p.id === promptId);
    if (currentPromptIndex === -1) return;

    const newPrompts = [...prompts];
    const promptToMove = newPrompts[currentPromptIndex];

    let targetIndex = -1;
    if (direction === 'up') {
      targetIndex = currentPromptIndex - 1;
    } else {
      targetIndex = currentPromptIndex + 1;
    }

    if (targetIndex < 0 || targetIndex >= newPrompts.length) return;

    const promptToSwap = newPrompts[targetIndex];

    const newOrderPromptToMove = promptToSwap.order;
    const newOrderPromptToSwap = promptToMove.order;

    promptToMove.order = newOrderPromptToMove;
    promptToSwap.order = newOrderPromptToSwap;

    newPrompts.sort((a, b) => a.order - b.order);

    setPrompts(newPrompts);

    try {
      const updatedPromptOrders = newPrompts.map((p) => ({
        id: p.id,
        order: p.order,
      }));
      await api.patch(`/api/v1/category/${id}`, { prompts: updatedPromptOrders });
      const response = await api.get(`/api/v1/category/${id}`);
      const parsedCategory = CategorySchema.parse(response.data);
      setCategory(parsedCategory);
      setPrompts(parsedCategory.prompts);
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Failed to update prompt order');
      } else {
        setError('An unexpected error occurred.');
      }
      const response = await api.get(`/api/v1/category/${id}`);
      const parsedCategory = CategorySchema.parse(response.data);
      setCategory(parsedCategory);
      setPrompts(parsedCategory.prompts);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-4">
        <h2 className="text-2xl font-bold mr-2">{category.name}</h2>
        <div
          className={`p-2 rounded-md text-sm mr-2 ${category.is_valid ? 'bg-green-200 text-green-800' : 'bg-gray-200 text-gray-800'}`}
        >
          {category.is_valid ? 'Complete' : 'Incomplete'}
        </div>
        {isOwner && (
          <button
            className={`py-1 px-3 rounded-full text-white font-bold ${isAddPromptButtonDisabled ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-500 hover:bg-green-600'}`}
            disabled={isAddPromptButtonDisabled}
            onClick={handleAddPromptClick}
          >
            +
          </button>
        )}
      </div>

      {showAddPrompt && (
        <AddPromptForm onAddPrompt={handleCreatePrompt} onCancel={() => setShowAddPrompt(false)} />
      )}

      <div className="space-y-4">
        {prompts
          .sort((a, b) => a.order - b.order)
          .map((prompt) => (
            <PromptItem
              key={prompt.id}
              prompt={prompt}
              isOwner={isOwner}
              onMovePrompt={handleMovePrompt}
              onUpdatePrompt={handleUpdatePrompt}
              onDeletePrompt={handleDeletePrompt}
            />
          ))}
      </div>

      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default EditCategory;
