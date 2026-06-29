import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { REHYDRATE } from "redux-persist";

interface AuthState {
  isLoggedIn: boolean;
  user: {
    username: string;
    email: string;
  } | null;
}

const initialState: AuthState = {
  isLoggedIn: !!localStorage.getItem("access_token"),
  user: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginSuccess: (
      state,
      action: PayloadAction<{ username: string; email: string }>,
    ) => {
      state.isLoggedIn = true;
      state.user = action.payload;
    },
    logout: (state) => {
      state.isLoggedIn = false;
      state.user = null;
      localStorage.removeItem("access_token");
    },
  },
  extraReducers: (builder) => {
    builder.addCase(REHYDRATE, (state, action) => {
      const incoming = (action as { payload?: { auth?: AuthState } }).payload?.auth;
      if (incoming) {
        state.user = incoming.user ?? state.user;
      }
      state.isLoggedIn = !!localStorage.getItem("access_token");
    });
  },
});

export const { loginSuccess, logout } = authSlice.actions;
export default authSlice.reducer;
