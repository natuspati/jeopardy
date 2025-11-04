import { createBrowserRouter } from 'react-router-dom';
import App from '@/App';
import Home from '@/features/lobby/components/Home';
import Login from '@/features/auth/components/Login';
import CategoryHome from '@/features/category/components/CategoryHome';
import CreateCategory from '@/features/category/components/CreateCategory';
import EditCategory from '@/features/category/components/EditCategory';
import ProtectedRoute from '@/features/auth/ProtectedRoute';
import CreateLobby from '@/features/lobby/components/CreateLobby';
import LobbyView from '@/features/lobby/components/LobbyView';
import Game from '@/features/game/components/Game';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      { path: '/login', element: <Login /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: '/categories', element: <CategoryHome /> },
          { path: '/categories/create', element: <CreateCategory /> },
          { path: '/categories/:id', element: <EditCategory /> },
          { path: '/lobbies/create', element: <CreateLobby /> },
          { path: '/lobbies/:id', element: <LobbyView /> },
          { path: '/game/:id', element: <Game /> },
        ],
      },
    ],
  },
]);
