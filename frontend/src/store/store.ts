import { configureStore, combineReducers } from "@reduxjs/toolkit";
import { persistReducer, persistStore } from "redux-persist";
import storage from "redux-persist/lib/storage";
import authReducer from "./slices/authSlice";
import chatReducer, { resetChatState } from "./slices/chatSlice";

const authPersistConfig = {
  key: "auth",
  storage,
  whitelist: ["isLoggedIn", "user"],
};

const chatPersistConfig = {
  key: "chat",
  storage,
  whitelist: ["cart", "messages"],
  migrate: (state: any) =>
    Promise.resolve({
      ...state,
      cart: state?.cart || [],
      messages: state?.messages || [],
    }),
};

const rootReducer = combineReducers({
  auth: persistReducer(authPersistConfig, authReducer),
  chat: persistReducer(chatPersistConfig, chatReducer),
});

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
