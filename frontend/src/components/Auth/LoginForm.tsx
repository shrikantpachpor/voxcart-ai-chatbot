// src/pages/Login.tsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { chatApi } from "../../services/api";
import { loginSuccess } from "../../store/slices/authSlice";

const Login: React.FC = () => {
  const [credentials, setCredentials] = useState({
    username: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await chatApi.login(credentials);
      localStorage.setItem("access_token", response.data.access_token);
      dispatch(loginSuccess({ username: credentials.username, email: "" }));
      navigate("/");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: unknown }; message?: string };
      const detail = axiosErr?.response?.data as { detail?: string } | undefined;
      if (!axiosErr?.response && axiosErr?.message) {
        setError(`Cannot reach API (${axiosErr.message}). Check backend is running and CORS allows ${window.location.origin}.`);
      } else {
        setError(detail?.detail ?? "Invalid username or password");
      }
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    // Implement password recovery logic
    alert("Password recovery feature coming soon!");
    setShowForgotPassword(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 pt-16">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-2 text-center">
          Welcome Back! 👋
        </h2>
        <p className="text-center text-gray-500 mb-6">Sign in to Voxbot</p>
        {error && <div className="text-red-500 mb-4 text-center">{error}</div>}

        {showForgotPassword ? (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full p-2 border rounded"
              required
            />
            <button
              type="submit"
              className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Reset Password
            </button>
            <button
              type="button"
              onClick={() => setShowForgotPassword(false)}
              className="w-full text-blue-500 hover:underline"
            >
              Back to Login
            </button>
          </form>
        ) : (
          <>
            <form onSubmit={handleLogin} className="space-y-4">
              <input
                type="text"
                placeholder="Username"
                className="w-full p-2 border rounded"
                value={credentials.username}
                onChange={(e) =>
                  setCredentials({ ...credentials, username: e.target.value })
                }
                required
              />
              <input
                type="password"
                placeholder="Password"
                className="w-full p-2 border rounded"
                value={credentials.password}
                onChange={(e) =>
                  setCredentials({ ...credentials, password: e.target.value })
                }
                required
              />
              <button
                type="submit"
                className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
              >
                Sign In
              </button>
            </form>
            <div className="mt-4 text-center space-y-2">
              <button
                onClick={() => setShowForgotPassword(true)}
                className="text-blue-500 hover:underline"
              >
                Forgot Password?
              </button>
              <p className="text-gray-600">
                Don't have an account?{" "}
                <Link to="/register" className="text-blue-500 hover:underline">
                  Register here
                </Link>
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Login;
