import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/authStore";
import { API_BASE_URL } from "@/lib/constants";

/** Auth endpoints where 401 is a valid response (wrong OTP, etc.) */
const AUTH_ENDPOINTS = [
  "/api/v1/auth/send-otp",
  "/api/v1/auth/verify-otp",
  "/api/v1/auth/register",
  "/api/v1/auth/login",
  "/api/v1/auth/refresh",
];

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/** Request interceptor - add auth token */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = useAuthStore.getState().tokens;
    if (tokens?.accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${tokens.accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/** Response interceptor - handle errors */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Skip token refresh for auth endpoints — 401 is expected there (wrong OTP, etc.)
    const url = originalRequest?.url ?? "";
    const isAuthEndpoint = AUTH_ENDPOINTS.some((ep) => url.includes(ep));

    // Handle 401 Unauthorized (only for non-auth endpoints)
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;

      const { tokens, setTokens, logout } = useAuthStore.getState();

      if (tokens?.refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: tokens.refreshToken,  // Backend expects snake_case
          });

          // Backend returns nested response: { success, data: { access_token, refresh_token, ... } }
          const rawTokens = response.data?.data ?? response.data;
          const newTokens = {
            accessToken: rawTokens.access_token,
            refreshToken: rawTokens.refresh_token,
            expiresIn: rawTokens.expires_in,
            tokenType: rawTokens.token_type,
          };
          setTokens(newTokens);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`;
          }
          return api(originalRequest);
        } catch {
          logout();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
        }
      } else {
        logout();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
