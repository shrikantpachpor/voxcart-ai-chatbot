// src/components/Chat/ChatWindow.tsx
import React, { useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import ChatBubble from "./ChatBubble";
import { RootState } from "../../store/store";
import LoadingSpinner from "../LoadingSpinner";

const ChatWindow: React.FC = () => {
  const { messages, isLoading } = useSelector((state: RootState) => state.chat);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="p-4">
      {messages.map((message, index) => (
        <ChatBubble
          key={index}
          sender={message.sender}
          content={message.content}
          type={message.type}
        />
      ))}
      {isLoading && (
        <div className="flex justify-center p-4">
          <LoadingSpinner />
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
