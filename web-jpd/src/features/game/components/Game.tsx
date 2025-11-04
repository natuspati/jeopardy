import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { createSocket } from '@/api/socket';
import { useAuth } from '@/features/auth/AuthContext';
import { GameSchema, GameEventSchema, GamePayloadSchema } from '@/features/game/interfaces';

// TODO: fix everything here
const Game = () => {
  const { id } = useParams<{ id: string }>();
  const { accessToken } = useAuth();
  const [game, setGame] = useState<GameSchema | null>(null);
  const [socketConnected, setSocketConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id || !accessToken) {
      setError('Lobby ID or access token missing.');
      return;
    }

    const lobbyId = parseInt(id, 10);
    if (isNaN(lobbyId)) {
      setError('Invalid Lobby ID.');
      return;
    }

    const socket = createSocket({
      namespace: 'game',
      lobbyId: lobbyId,
      accessToken: accessToken,
    });

    socket.on('connect', () => {
      console.log('Socket connected!');
      setSocketConnected(true);
      setError(null);
    });

    socket.on('disconnect', () => {
      console.log('Socket disconnected.');
      setSocketConnected(false);
    });

    socket.on('error', (err: any) => {
      console.error('Socket error:', err);
      setError(err.message || 'An unknown socket error occurred.');
    });

    socket.on('game.state', (data: GamePayloadSchema) => {
      console.log('Game state received:', data);
      setGame(data.game);
    });

    socket.on('game.event', (data: GameEventSchema) => {
      console.log('Game event received:', data);
      // Handle specific game events here if needed
    });

    return () => {
      socket.disconnect();
    };
  }, [id, accessToken]);

  if (error) {
    return <div className="text-center text-red-500">Error: {error}</div>;
  }

  if (!socketConnected) {
    return <div className="text-center">Connecting to game...</div>;
  }

  if (!game) {
    return <div className="text-center">Waiting for game data...</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Game Lobby: {game.id}</h1>
      <p>
        <strong>Game State:</strong> {game.state}
      </p>
      <p>
        <strong>Lead:</strong> {game.lead.username} ({game.lead.state})
      </p>

      <h2 className="text-2xl font-semibold mt-6 mb-3">Players:</h2>
      {game.players.length > 0 ? (
        <div className="space-y-2">
          {game.players.map((player) => (
            <div key={player.id} className="p-3 bg-gray-100 rounded-md shadow-sm">
              <h3 className="text-lg font-semibold">{player.username}</h3>
              <p className="text-sm text-gray-600">
                Score: {player.score} | State: {player.state}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p>No players in this game.</p>
      )}

      <h2 className="text-2xl font-semibold mt-6 mb-3">Categories:</h2>
      {game.categories.length > 0 ? (
        <div className="space-y-2">
          {game.categories.map((category) => (
            <div key={category.id} className="p-3 bg-gray-100 rounded-md shadow-sm">
              <h3 className="text-lg font-semibold">{category.name}</h3>
              <p className="text-sm text-gray-600">Prompts: {category.prompts.length}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>No categories in this game.</p>
      )}
    </div>
  );
};

export default Game;
