import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { toggleCart } from "../../store/slices/chatSlice";
import { FaShoppingCart } from "react-icons/fa";

const Navbar: React.FC = () => {
  const { cart } = useSelector((state: RootState) => state.chat);
  const dispatch = useDispatch();

  return (
    <nav className="bg-white shadow-md fixed w-full z-10">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="text-xl font-bold">Ecommerce Chat</div>
          <button
            onClick={() => dispatch(toggleCart())}
            className="relative p-2 hover:bg-gray-100 rounded-full"
          >
            <FaShoppingCart className="w-6 h-6" />
            {cart.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full text-xs w-5 h-5 flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </button>
        </div>
      </div>
    </nav>
  );
};
