import { Link } from 'react-router-dom';
import CategoryList from './CategoryList';

const CategoryHome = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-extrabold text-gray-900 text-left">Categories</h1>
        <Link
          to="/categories/create"
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Create Category
        </Link>
      </div>
      <CategoryList />
    </div>
  );
};

export default CategoryHome;
