import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type MessageType = "text" | "product" | "recommendation" | "cart";

export interface ProductRecommendation {
  title: string;
  description: string;
  image: string;
  price: number;
  id: number;
}
export interface ProductList {
  title: string;
  description: string;
  image: string;
  price: number;
  id: number;
  quantity: number;
  rating: number;
  category: string;
  reviews: number;
  recommendations: ProductRecommendation[];
  similar_products: ProductRecommendation[];
  related_products: ProductRecommendation[];
  product_url: string;
  product_id: number;
  product_name: string;
  product_price: number;    
}
export interface Product {
  id: number;
  title: string;
  price: number;
  quantity: number;
  image: string;
}

export interface ChatMessage {
  sender: "user" | "bot";
  content: string | Product | Product[];
  type: MessageType;
  timestamp: number;
}

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  isChatOpen: boolean;
  isCartOpen: boolean;
  isCartLoading: boolean;
  cart: Product[];
  profile: Record<string, unknown> | null;
  paymentMethods: any[];
  orders: any[];
  showProfileModal: boolean;
}

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  isChatOpen: false,
  isCartOpen: false,
  isCartLoading: false,
  cart: [],
  profile: null,
  paymentMethods: [],
  orders: [],
  showProfileModal: false
};


const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    toggleChat: (state) => {
      state.isChatOpen = !state.isChatOpen;
    },
    toggleCart: (state) => {
      state.isCartOpen = !state.isCartOpen;
    },
    setCartLoading: (state, action: PayloadAction<boolean>) => {
      state.isCartLoading = action.payload;
    },
    setProfile: (state, action) => {
      state.profile = action.payload;
    },
    setPaymentMethods: (state, action) => {
      state.paymentMethods = action.payload;
    },
    setOrders: (state, action) => {
      state.orders = action.payload;
    },
    addToCart: (state, action: PayloadAction<Product>) => {
      const existing = state.cart.find((item) => item.id === action.payload.id);
      if (existing) {
        existing.quantity += action.payload.quantity;
      } else {
        state.cart.push(action.payload);
      }
    },
    removeFromCart: (state, action: PayloadAction<number>) => {
      state.cart = state.cart.filter((item) => item.id !== action.payload);
    },
    toggleProfileModal: (state, action: PayloadAction<boolean | undefined>) => {
      state.showProfileModal = typeof action.payload !== 'undefined' 
        ? action.payload
        : !state.showProfileModal;
    },
    updateCartItemQuantity: (state, action: PayloadAction<{id: number, quantity: number}>) => {
      const item = state.cart.find((item) => item.id === action.payload.id);
      if (item) {
        item.quantity = action.payload.quantity;
      }
    },
    resetChatState: (state) => {
      state.messages = [];
      state.isLoading = false;
      state.isChatOpen = false;
    },
    syncCart: (state, action: PayloadAction<Product[]>) => {
      state.cart = action.payload;
    },
  },
});

export const {
  addMessage,
  setLoading,
  toggleChat,
  toggleCart,
  setCartLoading,
  addToCart,
  removeFromCart,
  updateCartItemQuantity,
  resetChatState,
  syncCart,
  toggleProfileModal,
  setProfile,
  setPaymentMethods,
  setOrders
} = chatSlice.actions;
export default chatSlice.reducer;