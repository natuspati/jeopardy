import { useState } from 'react';
import { Outlet, Link } from 'react-router-dom';

import '@/App.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <nav>
        <Link to="/">Home</Link> | <Link to="/game">Game</Link>
      </nav>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>count is {count}</button>
      </div>
      <Outlet />
    </>
  );
}

export default App;
