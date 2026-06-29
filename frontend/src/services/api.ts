import axios from "axios";
import { store } from "../store/store";
import { logout } from "../store/slices/authSlice";
import { PaymentMethod, AddPaymentMethodRequest, PaymentRequest } from "../store/types/payment";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL environment variable is not set. Please configure your .env file.');
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      store.dispatch(logout());
      window.location.href = "/login";
    }
    if (error.response?.status === 400) {
      return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  },
);

export const chatApi = {
  sendMessage: (message: string) => api.post("/chat/", { message }),
  login: (credentials: { username: string; password: string }) =>
    api.post("/chat/login/", credentials),
  register: (userData: { username: string; email: string; password: string }) =>
    api.post("/chat/register/", userData),
  getCart: (response_format: string = "api") => 
    api.post("/chat/view-cart/", { response_format:"json" }), // Fixed URL and body
  updateCart: (productId: number, quantity: number) =>
    api.post("/chat/update-cart", { product_id: productId, quantity }),
  removeFromCart: (productId: number) =>
    api.post("/chat/remove-from-cart", { product_id: productId }),
  getRecommendations: () => api.get("/chat/recommendations/"),
  
  addPaymentMethod: (data: AddPaymentMethodRequest) =>
    api.post<PaymentMethod>("/payment/add-payment-method", data),
  processPayment: (data: PaymentRequest) =>
    api.post<{ status: string; order_id: string }>("/payment/charge", data),
  getPaymentMethods: () => api.get<PaymentMethod[]>("/payment/get-payment-methods"),
  checkout: () => api.post<{ order_id: string }>("/chat/checkout"),
  getProfile: () => api.post("/chat/profile"),
updateAddress: (address: object) => api.post("/chat/update-address", address),
getOrderStatus: (orderId: string) => 
  api.post("/chat/order-status", { order_id: orderId }),
};