import React, { useState, useEffect, useRef } from 'react';
import { createSocket } from '@/api/socket';

const SocketTest = () => {
  const [status, setStatus] = useState('Connecting...');
  const [messages, setMessages] = useState<string[]>([]);
  const [messageInput, setMessageInput] = useState('');

  const socketRef = useRef<ReturnType<typeof createSocket>>();

  useEffect(() => {
    socketRef.current = createSocket("game", { lobby_id: "123" });
    const socket = socketRef.current;

    const onConnect = () => setStatus(`Connected! SID: ${socket.id}`);
    const onDisconnect = () => setStatus('Disconnected');
    const onConnectionResponse = (data: unknown) =>
      setMessages((prev) => [...prev, `Connection response: ${JSON.stringify(data)}`]);
    const onMessageResponse = (data: unknown) =>
      setMessages((prev) => [...prev, `Message response: ${JSON.stringify(data)}`]);

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('connection_response', onConnectionResponse);
    socket.on('message_response', onMessageResponse);

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('connection_response', onConnectionResponse);
    socket.on('message_response', onMessageResponse);

    return () => {
      socket.disconnect();
    };
  }, []);

  const sendMessage = () => {
    if (messageInput.trim()) {
      socketRef.current?.emit('message', {
        text: messageInput,
        timestamp: Date.now(),
      });
      setMessageInput('');
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Socket.IO Test</h1>
      <div className="mb-4">
        <span className="font-semibold">Status: </span>
        <span className={`${status.startsWith('Connected') ? 'text-green-600' : 'text-red-600'}`}>
          {status}
        </span>
      </div>
      <div className="flex space-x-2 mb-4">
        <input
          type="text"
          value={messageInput}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMessageInput(e.target.value)}
          onKeyUp={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && sendMessage()}
          className="flex-grow border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="Type a message..."
        />
        <button
          onClick={sendMessage}
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Send
        </button>
      </div>
      <div className="bg-gray-50 p-4 rounded-md h-64 overflow-y-auto border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Messages</h2>
        {messages.length > 0 ? (
          messages.map((msg: string, index: number) => (
            <p key={index} className="text-gray-600 text-sm mb-1 font-mono">{msg}</p>
          ))
        ) : (
          <p className="text-gray-500">No messages yet.</p>
        )}
      </div>
    </div>
  );
};

export default SocketTest;
