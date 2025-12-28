import React from "react";
import ChatWindow from "../components/Chat/ChatWindow";
import ChatInput from "../components/Chat/ChatInput";
import CartSidebar from "../components/Cart/CartSidebar";
import { useSelector } from "react-redux";
import { RootState } from "../store/store";
import { Navigate } from "react-router-dom";

const Home: React.FC = () => {
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const { isCartOpen } = useSelector((state: RootState) => state.chat);

  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="pt-20 min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 flex gap-8">
        {isCartOpen && (
          <div className="w-80 flex-shrink-0">
            <CartSidebar />
          </div>
        )}
        <div className="flex-1">
          <div className="mb-10">
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome to Ecommerce Chatbot
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              Your personal shopping assistant is here to help
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <ChatWindow />
            <ChatInput />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
