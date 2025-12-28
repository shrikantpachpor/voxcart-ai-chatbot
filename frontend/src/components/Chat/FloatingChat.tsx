// src/components/Chat/FloatingChat.tsx
import React, { useRef, useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";
import { toggleChat } from "../../store/slices/chatSlice";
import { FaCommentDots, FaTimes } from "react-icons/fa";
import ScrollButtons from "./ScrollButtons";

const FloatingChat: React.FC = () => {
  const { isChatOpen } = useSelector((state: RootState) => state.chat);
  const dispatch = useDispatch();
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const [maxHeight, setMaxHeight] = useState("70vh");

  useEffect(() => {
    const calculateMaxHeight = () => {
      const viewportHeight = window.innerHeight;
      const topOffset = 100; // Space from top of viewport
      const calculatedHeight = viewportHeight - topOffset;
      setMaxHeight(`${calculatedHeight}px`);
    };

    calculateMaxHeight();
    window.addEventListener("resize", calculateMaxHeight);
    return () => window.removeEventListener("resize", calculateMaxHeight);
  }, []);

  if (!isChatOpen)
    return (
      <button
        onClick={() => dispatch(toggleChat())}
        className="fixed bottom-8 right-8 bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600 transition-all animate-bounce"
        aria-label="Open chat"
      >
        <FaCommentDots className="w-6 h-6" />
      </button>
    );

  return (
    <div
      className="fixed bottom-8 right-8 w-96 bg-white rounded-xl shadow-xl flex flex-col transition-all duration-300"
      style={{ maxHeight, zIndex: 1000 }}
    >
      <div className="bg-blue-500 text-white p-4 rounded-t-xl flex justify-between items-center">
        <h2 className="font-semibold">Shopping Assistant</h2>
        <button
          onClick={() => dispatch(toggleChat())}
          className="hover:text-gray-200 text-xl"
          aria-label="Close chat"
        >
          <FaTimes />
        </button>
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto chat-window" ref={chatWindowRef}>
          <ChatWindow />
        </div>
        <ScrollButtons containerRef={chatWindowRef} />
        <ChatInput />
      </div>
    </div>
  );
};

export default FloatingChat;
