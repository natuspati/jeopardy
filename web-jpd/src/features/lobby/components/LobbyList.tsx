import { useState, useEffect, useRef } from 'react';
import api from '@/api/client';
import { Lobby, LobbySchema } from '@/features/lobby/interfaces';
import { z } from 'zod';
import settings from '@/settings';

const LobbyList = () => {
  const [lobbies, setLobbies] = useState<Lobby[]>([]);
  const hasFetched = useRef(false);

  // TODO: make listing lobbies always include started lobbies
  // TODO: add container/component with mine lobbies
  useEffect(() => {
    const fetchLobbies = async () => {
      try {
        const response = await api.get('/api/v1/lobby');
        const parsedLobbies = z.array(LobbySchema).parse(response.data);
        setLobbies(parsedLobbies.slice(0, settings.maxLobbiesToShow));
      } catch (error) {
        console.error('Failed to fetch lobbies:', error);
      }
    };

    if (!hasFetched.current) {
      fetchLobbies();
      hasFetched.current = true;
    }
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-4xl font-extrabold text-gray-900 mb-8 text-left">Active Lobbies</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {lobbies.length > 0 ? (
          lobbies.map((lobby) => (
            <div
              key={lobby.id}
              className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between"
            >
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Lobby #{lobby.id}</h3>
              <p className="text-gray-600 mb-1">
                Host: <span className="font-medium">{lobby.host.username}</span>
              </p>
              <p className="text-gray-600 mb-4">
                Players: <span className="font-medium">0/4</span>
              </p>{' '}
              {/* Placeholder for number of players */}
              <button
                onClick={() => console.log(`Joining lobby ${lobby.id}`)}
                className="mt-auto bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Join Lobby
              </button>
            </div>
          ))
        ) : (
          <p className="text-gray-600 text-lg col-span-full">No active lobbies at the moment.</p>
        )}
      </div>
    </div>
  );
};

export default LobbyList;
