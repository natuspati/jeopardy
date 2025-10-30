import { Outlet, Link } from 'react-router-dom';

import '@/App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="sticky top-0 bg-white shadow-md z-10">
        <nav className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-gray-800">
              <Link to="/" className="hover:text-indigo-600">Jeopardy</Link>
            </div>
            <div className="flex space-x-6">
              <Link to="/" className="text-gray-600 hover:text-indigo-600">Home</Link>
              <Link to="/game" className="text-gray-600 hover:text-indigo-600">Game</Link>
              <Link to="/socket-test" className="text-gray-600 hover:text-indigo-600">Socket Test</Link>
            </div>
          </div>
        </nav>
      </header>
      <main className="container mx-auto px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}

export default App;
