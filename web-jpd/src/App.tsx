import { Outlet } from 'react-router-dom';
import Navbar from '@/features/navbar/components/Navbar';

import '@/App.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navbar />
      <main className="container mx-auto px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}

export default App;
