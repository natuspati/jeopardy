import React, { useState } from 'react';

interface AddPromptFormProps {
  onAddPrompt: (question: string, answer: string, score: number) => void;
  onCancel: () => void;
}

const AddPromptForm: React.FC<AddPromptFormProps> = ({ onAddPrompt, onCancel }) => {
  const [newQuestion, setNewQuestion] = useState('');
  const [newAnswer, setNewAnswer] = useState('');
  const [newScore, setNewScore] = useState(100);

  const handleSubmit = () => {
    onAddPrompt(newQuestion, newAnswer, newScore);
  };

  return (
    <div className="mb-4 p-4 border rounded-md">
      <h3 className="text-lg font-semibold mb-2">Add New Prompt</h3>
      <div className="mb-2">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newQuestion">
          Question:
        </label>
        <input
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="newQuestion"
          type="text"
          placeholder="Enter question"
          value={newQuestion}
          onChange={(e) => setNewQuestion(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newAnswer">
          Answer:
        </label>
        <input
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="newAnswer"
          type="text"
          placeholder="Enter answer"
          value={newAnswer}
          onChange={(e) => setNewAnswer(e.target.value)}
        />
      </div>
      <div className="mb-2">
        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="newScore">
          Score:
        </label>
        <input
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          id="newScore"
          type="number"
          placeholder="Enter score"
          value={newScore}
          onChange={(e) => setNewScore(Number(e.target.value))}
        />
      </div>
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mr-2"
        onClick={handleSubmit}
      >
        Create Prompt
      </button>
      <button
        className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        onClick={onCancel}
      >
        Cancel
      </button>
    </div>
  );
};

export default AddPromptForm;
