import { createBrowserRouter } from 'react-router-dom';
import App from '@/App';
import Home from '@/pages/Home';
import Game from '@/pages/Game';
import SocketTest from '@/pages/SocketTest';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      { path: '/game', element: <Game /> },
      { path: '/socket-test', element: <SocketTest /> },
    ],
  },
]);
