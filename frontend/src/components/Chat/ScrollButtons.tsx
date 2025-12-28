// src/components/Chat/ScrollButtons.tsx
import React, { RefObject } from "react";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

interface ScrollButtonsProps {
  containerRef: RefObject<HTMLDivElement>;
}

const ScrollButtons: React.FC<ScrollButtonsProps> = ({ containerRef }) => {
  const scrollToTop = () => {
    containerRef.current?.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  };

  return (
    <div className="absolute right-4 bottom-16 space-y-2">
      <button
        onClick={scrollToTop}
        className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
        aria-label="Scroll to top"
      >
        <FaArrowUp className="w-4 h-4" />
      </button>
      <button
        onClick={scrollToBottom}
        className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
        aria-label="Scroll to bottom"
      >
        <FaArrowDown className="w-4 h-4" />
      </button>
    </div>
  );
};

export default ScrollButtons;
