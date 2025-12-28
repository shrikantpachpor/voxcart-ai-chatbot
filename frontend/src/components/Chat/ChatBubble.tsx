import React from "react";
import DOMPurify from "dompurify";
import { Product } from "../../store/slices/chatSlice";
import { useDispatch } from "react-redux";
import { toggleCart, toggleProfileModal } from "../../store/slices/chatSlice";

interface ChatBubbleProps {
  sender: "user" | "bot";
  content: string | Product | Product[];
  type: "text" | "product" | "recommendation" | "cart";
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ sender, content, type }) => {
  // Function to sanitize and format the content
  const dispatch = useDispatch();

  const formatContent = (text: string): string => {
    const formattedText = text.replace(/\n/g, "<br />");
    return DOMPurify.sanitize(formattedText);
  };


  const renderRawContent = (text: string) => {
    return <div dangerouslySetInnerHTML={{ __html: text }} />;
  };

  // Render product list with improved formatting
  const renderProductList = (text: string) => {
    const lines = text.split("\n");
    return (
      <div className="space-y-2">
        {lines.map((line, index) => {
          if (line.startsWith("🛍️")) {
            return (
              <p key={index} className="font-bold text-lg text-blue-600">
                {line}
              </p>
            );
          } else if (line.startsWith("Would you like to:")) {
            return (
              <div key={index} className="mt-4">
                <p className="font-semibold text-gray-700">{line}</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {lines
                    .slice(index + 1)
                    .map((action, actionIndex) => (
                      <button
                        key={actionIndex}
                        className="px-3 py-1 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                      >
                        {action}
                      </button>
                    ))}
                </div>
              </div>
            );
          } else if (line.match(/^\d+\./)) {
            const [name, ...details] = line.split("\n");
            return (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <p className="font-semibold text-gray-800">{name}</p>
                {details.map((detail, detailIndex) => (
                  <p key={detailIndex} className="text-sm text-gray-600">
                    {detail.trim()}
                  </p>
                ))}
              </div>
            );
          } else {
            return (
              <p key={index} className="text-gray-700">
                {line}
              </p>
            );
          }
        })}
      </div>
    );
  };

  const renderContent = () => {
    if (typeof content === "string" && content.includes("[[SHOW_PROFILE]]")) {
      dispatch(toggleProfileModal(true));
      return "Here's your profile details:";
    }
    switch (type) {
      case "product":
        const product = content as Product;
        return (
          <div className="bg-white rounded-lg shadow-md p-4">
            <img
              src={product.image}
              alt={product.title}
              className="w-32 h-32 object-contain mb-2"
            />
            <h3 className="font-semibold">{product.title}</h3>
            <p className="text-gray-600">${product.price}</p>
            <button className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              Add to Cart
            </button>
          </div>
        );

      case "recommendation":
        const products = content as Product[];
        return (
          <div className="grid grid-cols-2 gap-4">
            {products.map((product) => (
              <div key={product.id} className="bg-white p-2 rounded shadow">
                <img
                  src={product.image}
                  alt={product.title}
                  className="w-full h-24 object-contain"
                />
                <p className="text-sm font-medium">{product.title}</p>
                <p className="text-xs text-gray-500">${product.price}</p>
              </div>
            ))}
          </div>
        );

      default:
        // Render raw content for XSS testing
        return renderRawContent(content as string);
    }
  };

  return (
    <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] p-3 rounded-lg ${
          sender === "user"
            ? "bg-blue-500 text-white rounded-br-none"
            : "bg-gray-100 rounded-bl-none"
        }`}
      >
        {renderContent()}
      </div>
    </div>
  );
};

export default ChatBubble;