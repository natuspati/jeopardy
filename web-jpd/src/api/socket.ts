import { io, Socket } from 'socket.io-client';

interface CreateSocketOptions {
  url?: string;
  namespace?: string;
  lobbyId?: number;
  accessToken?: string;
  query?: { [key: string]: string | number };
}

export function createSocket({
  url,
  namespace = 'game',
  lobbyId,
  accessToken,
  query = {},
}: CreateSocketOptions): Socket {
  const socketUrl = url || `http://localhost:8000/${namespace}`;

  const finalQuery = { ...query };
  if (lobbyId !== undefined) {
    finalQuery.id = String(lobbyId);
  }

  const options: {
    path: string;
    transports: string[];
    query: { [key: string]: string | number };
    auth?: { token: string };
  } = {
    path: '/ws',
    transports: ['websocket'],
    query: finalQuery,
  };

  if (accessToken) {
    options.auth = { token: accessToken };
  }

  return io(socketUrl, options);
}
