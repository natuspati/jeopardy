import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '@/api/client';
import { LobbySchema, LobbyStartedPublicSchema } from '@/features/lobby/interfaces';
import { z } from 'zod';
import { LobbyStateEnum } from '@/shared/enums';

const LobbyView = () => {
  const { id } = useParams<{ id: string }>();
  const [lobby, setLobby] = useState<z.infer<typeof LobbySchema> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLobby = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/api/v1/lobby/${id}`);
        const parsedLobby = LobbySchema.parse(response.data);
        setLobby(parsedLobby);
      } catch (err) {
        console.error('Failed to fetch lobby:', err);
        setError('Failed to load lobby.');
      } finally {
        setLoading(false);
      }
    };

    fetchLobby();
  }, [id]);

  const handleStartLobby = async () => {
    if (!lobby) return;
    try {
      const response = await api.put<z.infer<typeof LobbyStartedPublicSchema>>(
        `/api/v1/lobby/${lobby.id}/start`
      );
      window.location.href = response.data.game_url;
    } catch (err) {
      console.error('Failed to start lobby:', err);
      setError('Failed to start lobby. Please try again.');
    }
  };

  if (loading) {
    return <div className="text-center">Loading lobby...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500">Error: {error}</div>;
  }

  if (!lobby) {
    return <div className="text-center">Lobby not found.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Lobby: {lobby.id}</h1>
      <p>
        <strong>Host:</strong> {lobby.host.username}
      </p>
      <p>
        <strong>State:</strong> {lobby.state}
      </p>
      <p>
        <strong>Created At:</strong> {new Date(lobby.created_at).toLocaleString()}
      </p>

      <h2 className="text-2xl font-semibold mt-6 mb-3">Categories:</h2>
      {lobby.categories.length > 0 ? (
        <div className="space-y-2">
          {lobby.categories.map((category) => (
            <div key={category.id} className="p-3 bg-gray-100 rounded-md shadow-sm">
              <h3 className="text-lg font-semibold">{category.name}</h3>
              <p className="text-sm text-gray-600">Prompts: {category.prompts.length}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>No categories in this lobby.</p>
      )}

      {lobby.state === LobbyStateEnum.CREATED && (
        <button onClick={handleStartLobby} className="btn btn-primary mt-6">
          Start Lobby
        </button>
      )}
    </div>
  );
};

export default LobbyView;
