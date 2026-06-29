import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { toggleCart } from "../../store/slices/chatSlice";
import { FaShoppingCart } from "react-icons/fa";
import { Link, useNavigate } from "react-router-dom";
import { logout } from "../../store/slices/authSlice";
import { resetChatState } from "../../store/slices/chatSlice";

const Navbar: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isLoggedIn, user } = useSelector((state: RootState) => state.auth);
  const { cart = []} = useSelector((state: RootState) => state.chat);

  const handleLogout = () => {
    dispatch(logout());
    dispatch(resetChatState());
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md p-4 fixed w-full top-0 z-50">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-blue-600">
          Voxbot
        </Link>
        <div className="flex items-center gap-6">
          {isLoggedIn && (
            <>
              <button
                onClick={() => dispatch(toggleCart())}
                className="relative p-2 hover:bg-gray-100 rounded-full transition-colors"
                aria-label="Shopping cart"
              >
                <FaShoppingCart className="w-6 h-6 text-gray-700" />
                {cart?.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full text-xs w-5 h-5 flex items-center justify-center">
                    {cart.length}
                  </span>
                )}
              </button>
              <div className="flex items-center gap-4">
                <span className="text-gray-700 font-medium">
                  Hi, {user?.username}
                </span>
                <Link
                    to="/profile"
                    className="text-gray-700 hover:text-blue-600 font-medium"
                  >
                    Profile
                  </Link>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-blue-600 font-medium"
                >
                  Logout
                </button>
              </div>
            </>
          )}
          {!isLoggedIn && (
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
