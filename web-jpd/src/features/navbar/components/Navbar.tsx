import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/features/auth/AuthContext';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 bg-white shadow-md z-10">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold text-gray-800">
            <Link to="/" className="hover:text-indigo-600">
              Jeopardy
            </Link>
          </div>
          <div className="flex space-x-6 items-center">
            <Link to="/" className="text-gray-600 hover:text-indigo-600">
              Home
            </Link>
            {isAuthenticated && (
              <Link to="/categories" className="text-gray-600 hover:text-indigo-600">
                Categories
              </Link>
            )}
            {isAuthenticated ? (
              <div
                className="relative"
                onMouseEnter={() => setIsDropdownOpen(true)}
                onMouseLeave={() => setIsDropdownOpen(false)}
              >
                <button className="text-gray-600 hover:text-indigo-600 focus:outline-none">
                  {user?.username}
                </button>
                {isDropdownOpen && (
                  <div className="absolute left-1/2 -translate-x-1/2 top-full w-max bg-white rounded-md shadow-lg py-1 z-20">
                    <button
                      onClick={logout}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link to="/login" className="text-gray-600 hover:text-indigo-600">
                Login
              </Link>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;
