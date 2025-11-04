import React, { useState } from 'react';
import { Prompt } from '@/features/category/interfaces';
import settings from '@/settings';

interface PromptItemProps {
  prompt: Prompt;
  isOwner: boolean;
  onMovePrompt: (promptId: number, direction: 'up' | 'down') => void;
  onUpdatePrompt: (promptId: number, question: string, answer: string, score: number) => void;
  onDeletePrompt: (promptId: number) => void;
}

const PromptItem: React.FC<PromptItemProps> = ({
  prompt,
  isOwner,
  onMovePrompt,
  onUpdatePrompt,
  onDeletePrompt,
}) => {
  const [editing, setEditing] = useState(false);
  const [editQuestion, setEditQuestion] = useState(prompt.question);
  const [editAnswer, setEditAnswer] = useState(prompt.answer);
  const [editScore, setEditScore] = useState(prompt.score);

  const shortenedQuestion = prompt.question.slice(0, settings.promptQuestionShowLength);

  const handleSave = () => {
    onUpdatePrompt(prompt.id, editQuestion, editAnswer, editScore);
    setEditing(false);
  };

  const handleCancel = () => {
    setEditing(false);
    setEditQuestion(prompt.question);
    setEditAnswer(prompt.answer);
    setEditScore(prompt.score);
  };

  return (
    <div className="p-4 border rounded-md flex items-center">
      {isOwner && (
        <div className="mr-4 flex items-center">
          <button
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-1 px-2 rounded-full"
            onClick={(e) => {
              e.stopPropagation();
              onMovePrompt(prompt.id, 'up');
            }}
          >
            ↑
          </button>
          <button
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-1 px-2 rounded-full ml-1"
            onClick={(e) => {
              e.stopPropagation();
              onMovePrompt(prompt.id, 'down');
            }}
          >
            ↓
          </button>
        </div>
      )}
      {editing ? (
        <div className="flex-grow">
          <div className="mb-2">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor={`editQuestion-${prompt.id}`}
            >
              Question:
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id={`editQuestion-${prompt.id}`}
              type="text"
              value={editQuestion}
              onChange={(e) => setEditQuestion(e.target.value)}
            />
          </div>
          <div className="mb-2">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor={`editAnswer-${prompt.id}`}
            >
              Answer:
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id={`editAnswer-${prompt.id}`}
              type="text"
              value={editAnswer}
              onChange={(e) => setEditAnswer(e.target.value)}
            />
          </div>
          <div className="mb-2">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor={`editScore-${prompt.id}`}
            >
              Score:
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id={`editScore-${prompt.id}`}
              type="number"
              value={editScore}
              onChange={(e) => setEditScore(Number(e.target.value))}
            />
          </div>
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2"
            onClick={handleSave}
          >
            Save
          </button>
          <button
            className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-2 rounded"
            onClick={handleCancel}
          >
            Cancel
          </button>
        </div>
      ) : (
        <div
          className={`flex-grow flex items-center justify-between ${isOwner ? 'cursor-pointer' : ''}`}
          onClick={() => isOwner && setEditing(true)}
        >
          <p className="flex-grow mr-4">
            {shortenedQuestion}
            {prompt.question.length > settings.promptQuestionShowLength ? '...' : ''}
          </p>
          {isOwner && (
            <div className="flex items-center">
              <p className="mr-4">Score: {prompt.score}</p>
              <button
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-2 rounded"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeletePrompt(prompt.id);
                }}
              >
                Delete
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PromptItem;
