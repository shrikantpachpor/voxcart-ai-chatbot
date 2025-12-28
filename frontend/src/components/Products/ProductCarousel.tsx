import React from "react";
import { Product } from "../../store/slices/chatSlice";
import { useDispatch } from "react-redux";
import { addToCart } from "../../store/slices/chatSlice";

interface ProductCarouselProps {
  products: Product[];
}

const ProductCarousel: React.FC<ProductCarouselProps> = ({ products }) => {
  const dispatch = useDispatch();

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex space-x-4">
        {products.map((product) => (
          <div
            key={product.id}
            className="min-w-[220px] bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="relative aspect-square mb-3">
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="font-semibold text-sm truncate mb-1 text-gray-800">
              {product.title}
            </h3>
            <p className="text-gray-600 text-sm mb-3">
              ${product.price.toFixed(2)}
            </p>
            <button
              onClick={() => dispatch(addToCart(product))}
              className="w-full bg-green-500 text-white px-3 py-2 rounded-md text-sm hover:bg-green-600 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              aria-label={`Add ${product.title} to cart`}
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductCarousel;
