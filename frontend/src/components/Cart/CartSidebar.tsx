// src/components/Cart/CartSidebar.tsx
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { useNavigate } from "react-router-dom";
import {
  removeFromCart,
  toggleCart,
  setCartLoading,
  syncCart,
  updateCartItemQuantity,
  setPaymentMethods,
} from "../../store/slices/chatSlice";
import { chatApi } from "../../services/api";
import LoadingSpinner from "../LoadingSpinner";
import { FaTimes } from "react-icons/fa";
import { PaymentMethod } from "../../store/types/payment";
import { mapApiCartToProducts, shouldApplyCartSync } from "../../utils/cart";

const CartSidebar: React.FC = () => {
  const { 
    cart = [], 
    isCartLoading,
    isCartOpen,
    paymentMethods 
  } = useSelector((state: RootState) => state.chat);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isInitializing, setIsInitializing] = useState(true);
  const [updatingProductId, setUpdatingProductId] = useState<number | null>(null);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<number | null>(null);
  const [cardDetails, setCardDetails] = useState({
    card_number: "",
    exp_month: "",
    exp_year: "",
    cvc: "",
    save_card: false,
  });

  useEffect(() => {
    if (!isCartOpen) return;

    const fetchCartAndPayments = async () => {
      try {
        setIsInitializing(true);
        
        const cartResponse = await chatApi.getCart();
        const products = mapApiCartToProducts(cartResponse.data);
        if (shouldApplyCartSync(cart, products)) {
          dispatch(syncCart(products));
        }

        const paymentResponse = await chatApi.getPaymentMethods();
        dispatch(setPaymentMethods(paymentResponse.data));
      } catch (error) {
        // Error loading cart and payment methods
      } finally {
        setIsInitializing(false);
      }
    };

    fetchCartAndPayments();
  }, [dispatch, isCartOpen]);

  const handleCheckout = async () => {
    try {
      if (!selectedPaymentMethod && !cardDetails.card_number) {
        alert("Please select a payment method or enter card details");
        return;
      }

      dispatch(setCartLoading(true));
      let paymentMethodId = selectedPaymentMethod;

      // Handle new card
      if (!paymentMethodId) {
        const response = await chatApi.addPaymentMethod({
          card_number: cardDetails.card_number,
          exp_month: parseInt(cardDetails.exp_month),
          exp_year: parseInt(cardDetails.exp_year),
          cvc: cardDetails.cvc,
          save_card: cardDetails.save_card
        });
        
        paymentMethodId = response.data.id;
        if (cardDetails.save_card) {
          dispatch(setPaymentMethods([...paymentMethods, response.data]));
        }
      }

      // Process payment
      const paymentResponse = await chatApi.processPayment({
        amount: cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
        payment_method_id: paymentMethodId!
      });

      if (paymentResponse.data.status === "succeeded") {
        await chatApi.checkout();
        dispatch(syncCart([]));
        navigate(`/order/${paymentResponse.data.order_id}`);
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : "Payment processing failed");
    } finally {
      dispatch(setCartLoading(false));
    }
  };

  const handleRemoveItem = async (productId: number) => {
    if (updatingProductId === productId) return;

    const previousCart = cart.map((item) => ({ ...item }));
    dispatch(removeFromCart(productId));
    setUpdatingProductId(productId);

    try {
      await chatApi.removeFromCart(productId);
    } catch (error) {
      dispatch(syncCart(previousCart));
    } finally {
      setUpdatingProductId(null);
    }
  };

  const handleQuantityChange = async (productId: number, quantity: number) => {
    if (updatingProductId === productId) return;

    if (quantity < 1) {
      await handleRemoveItem(productId);
      return;
    }

    const previousCart = cart.map((item) => ({ ...item }));
    dispatch(updateCartItemQuantity({ id: productId, quantity }));
    setUpdatingProductId(productId);

    try {
      await chatApi.updateCart(productId, quantity);
    } catch (error) {
      dispatch(syncCart(previousCart));
    } finally {
      setUpdatingProductId(null);
    }
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <div className="w-80 bg-white p-6 border-l shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          Your Cart ({cart.reduce((sum, item) => sum + item.quantity, 0)})
        </h3>
        <button
          onClick={() => dispatch(toggleCart(false))}
          className="text-gray-500 hover:text-gray-700"
          aria-label="Close cart"
        >
          <FaTimes className="w-5 h-5" />
        </button>
      </div>

      {isInitializing ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : cart.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Your cart is empty
        </div>
      ) : (
        <>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
            {cart.map((item) => (
              <div
                key={item.id}
                className={`flex items-center justify-between group hover:bg-gray-50 p-2 rounded-lg transition-colors ${
                  updatingProductId === item.id ? "opacity-60" : ""
                }`}
              >
                <div className="flex items-center space-x-4 flex-1">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="w-14 h-14 object-contain rounded-lg"
                  />
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-500">
                      ${item.price.toFixed(2)} × {item.quantity}
                    </p>
                    <div className="flex items-center mt-1">
                      <button
                        onClick={() =>
                          item.quantity <= 1
                            ? handleRemoveItem(item.id)
                            : handleQuantityChange(item.id, item.quantity - 1)
                        }
                        className="px-2 py-1 bg-gray-100 rounded-l hover:bg-gray-200 disabled:opacity-50"
                        disabled={updatingProductId === item.id}
                        aria-label={item.quantity <= 1 ? "Remove item" : "Decrease quantity"}
                      >
                        -
                      </button>
                      <span className="px-3 py-1 bg-gray-50">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                        className="px-2 py-1 bg-gray-100 rounded-r hover:bg-gray-200 disabled:opacity-50"
                        disabled={updatingProductId === item.id}
                      >
                        +
                      </button>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleRemoveItem(item.id)}
                  className="text-red-500 hover:text-red-600 ml-2 transition-opacity disabled:opacity-50"
                  disabled={updatingProductId === item.id}
                  aria-label={`Remove ${item.title} from cart`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t">
            <div className="flex justify-between font-semibold text-gray-900">
              <span>Total:</span>
              <span>${totalAmount.toFixed(2)}</span>
            </div>
          </div>

          <div className="mt-4 space-y-4">
            {paymentMethods.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Saved Payment Methods
                </label>
                <select
                  className="w-full p-2 border rounded"
                  value={selectedPaymentMethod ?? ''}
                  onChange={(e) => setSelectedPaymentMethod(Number(e.target.value))}
                >
                  <option value="">Select a saved method</option>
                  {paymentMethods.map((method) => (
                    <option key={method.id} value={method.id}>
                      {method.brand} ****{method.last4} 
                      (Exp: {method.exp_month}/{method.exp_year})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Or enter new card details
              </h4>
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Card Number"
                  className="w-full p-2 border rounded"
                  value={cardDetails.card_number}
                  onChange={(e) => setCardDetails(prev => ({...prev, card_number: e.target.value}))}
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="MM"
                    className="w-1/3 p-2 border rounded"
                    value={cardDetails.exp_month}
                    onChange={(e) => setCardDetails(prev => ({...prev, exp_month: e.target.value}))}
                  />
                  <input
                    type="text"
                    placeholder="YY"
                    className="w-1/3 p-2 border rounded"
                    value={cardDetails.exp_year}
                    onChange={(e) => setCardDetails(prev => ({...prev, exp_year: e.target.value}))}
                  />
                  <input
                    type="text"
                    placeholder="CVC"
                    className="w-1/3 p-2 border rounded"
                    value={cardDetails.cvc}
                    onChange={(e) => setCardDetails(prev => ({...prev, cvc: e.target.value}))}
                  />
                </div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={cardDetails.save_card}
                    onChange={(e) => setCardDetails(prev => ({...prev, save_card: e.target.checked}))}
                  />
                  <span className="text-sm">Save this card</span>
                </label>
              </div>
            </div>
          </div>

          <button
            onClick={handleCheckout}
            className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            disabled={cart.length === 0 || isCartLoading}
          >
            {isCartLoading ? "Processing..." : "Proceed to Checkout"}
          </button>
        </>
      )}
    </div>
  );
};

export default CartSidebar;