import { io } from 'socket.io-client';

const socket = io(import.meta.env.VITE_WS_URL || 'http://localhost:8000');

export default socket;
