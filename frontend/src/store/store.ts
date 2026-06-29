import {
  configureStore,
  combineReducers,
  isAnyOf,
  Middleware,
} from "@reduxjs/toolkit";
import {
  persistReducer,
  persistStore,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import authReducer from "./slices/authSlice";
import chatReducer, {
  syncCart,
  updateCartItemQuantity,
  removeFromCart,
  addToCart,
} from "./slices/chatSlice";

const authPersistConfig = {
  key: "auth",
  storage,
  whitelist: ["isLoggedIn", "user"],
};

const chatPersistConfig = {
  key: "chat",
  storage,
  whitelist: ["cart", "messages", "isCartOpen"],
};

const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authReducer),
  chat: persistReducer(chatPersistConfig, chatReducer),
});

let persistorRef: ReturnType<typeof persistStore> | null = null;

const cartFlushMiddleware: Middleware = () => (next) => (action) => {
  const result = next(action);
  if (
    persistorRef &&
    isAnyOf(syncCart, updateCartItemQuantity, removeFromCart, addToCart)(action)
  ) {
    void persistorRef.flush();
  }
  return result;
};

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat(cartFlushMiddleware),
});

export const persistor = persistStore(store);
persistorRef = persistor;

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
