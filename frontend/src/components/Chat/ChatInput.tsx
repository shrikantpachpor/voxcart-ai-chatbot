import React, { useState, KeyboardEvent } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addMessage, setLoading, toggleCart } from "../../store/slices/chatSlice";
import { chatApi } from "../../services/api";
import { RootState } from "../../store/store";
import LoadingSpinner from "../LoadingSpinner";

const ChatInput: React.FC = () => {
  const [input, setInput] = useState("");
  const dispatch = useDispatch();
  const { isLoading } = useSelector((state: RootState) => state.chat);

  const handleSend = async () => {
    if (!input.trim()) return;

    dispatch(
      addMessage({
        sender: "user",
        content: input,
        type: "text",
        timestamp: Date.now(),
      }),
    );

    dispatch(setLoading(true));

    try {
      // Handle cart view command
      if (input.toLowerCase().includes("show me my cart") || 
          input.toLowerCase().includes("view cart")) {
        dispatch(toggleCart());
        return;
      }

      const response = await chatApi.sendMessage(input);
      dispatch(
        addMessage({
          sender: "bot",
          content: response.data.response,
          type: "text",
          timestamp: Date.now(),
        }),
      );
    } catch (error) {
      dispatch(
        addMessage({
          sender: "bot",
          content: "Sorry, something went wrong.",
          type: "text",
          timestamp: Date.now(),
        }),
      );
    } finally {
      dispatch(setLoading(false));
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t p-4 bg-white">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="Type your message..."
          disabled={isLoading}
          rows={3}
          style={{ minHeight: "3rem", maxHeight: "15rem" }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed self-end"
        >
          {isLoading ? <LoadingSpinner /> : "Send"}
        </button>
      </div>
    </div>
  );
};

export default ChatInput;