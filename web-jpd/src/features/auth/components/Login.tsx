import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/api/client';
import { z } from 'zod';
import { UserRegisterSchema, TokenSchema } from '@/features/auth/interfaces';
import { useAuth } from '@/features/auth/AuthContext';
import axios from 'axios';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async () => {
    try {
      const response = await api.post(
        '/api/v1/user/token',
        new URLSearchParams({
          username,
          password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const parsedToken = TokenSchema.parse(response.data);
      login(parsedToken.access_token);
      navigate('/');
    } catch (error: unknown) {
      if (error instanceof z.ZodError) {
        setError(error.errors.map((e) => e.message).join(', '));
      } else if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Invalid username or password');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  const handleRegister = async () => {
    try {
      UserRegisterSchema.parse({ username, password });
      await api.post('/api/v1/user', {
        username,
        password,
      });
      handleLogin();
    } catch (error: unknown) {
      if (error instanceof z.ZodError) {
        setError(error.errors.map((e) => e.message).join(', '));
      } else if (axios.isAxiosError(error) && error.response) {
        setError(error.response.data.detail || 'Registration failed');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div>
      <h2>Login or Register</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="w-full p-2 border border-gray-300 rounded-md mb-2"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-2 border border-gray-300 rounded-md mb-4"
      />
      <button
        onClick={handleLogin}
        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded mr-2"
      >
        Login
      </button>
      <button
        onClick={handleRegister}
        className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
      >
        Register
      </button>
      {error && <p className="text-red-500 mt-4">{error}</p>}
    </div>
  );
};

export default Login;
