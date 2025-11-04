import { io, Socket } from 'socket.io-client';

export function createSocket(namespace: string, query = {}): Socket {
  return io(`http://localhost:8000/${namespace}`, {
    path: '/ws',
    transports: ['websocket'],
    query,
  });
}
