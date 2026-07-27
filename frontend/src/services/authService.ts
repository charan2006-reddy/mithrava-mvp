import api from "./api";
import type { ApiResponse } from "@/types/api";
import type {
  LoginRequest,
  OTPRequest,
  TokenResponse,
  RegisterRequest,
  User,
} from "@/types/auth";
import { formatPhoneWithCode } from "@/lib/utils";

/**
 * Normalize phone number to +91XXXXXXXXXX format.
 * Backend stores phones with +91 prefix, so all lookups must match.
 */
function normalizePhone(phone: string): string {
  // If already has country code, return as-is
  if (phone.startsWith("+")) return phone;
  // Strip any non-digits and prepend +91
  const digits = phone.replace(/\D/g, "");
  return formatPhoneWithCode(digits);
}

export const authService = {
  /** Send OTP to phone number */
  async sendOtp(phone: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.post("/api/v1/auth/send-otp", { phone: normalizePhone(phone) } as LoginRequest);
    return response.data;
  },

  /** Verify OTP and get tokens */
  async verifyOtp(data: OTPRequest): Promise<ApiResponse<TokenResponse>> {
    // Backend schema expects `code`, not `otp`
    const response = await api.post("/api/v1/auth/verify-otp", {
      phone: normalizePhone(data.phone),
      code: data.otp,
    });
    return response.data;
  },

  /** Register new user */
  async register(data: RegisterRequest): Promise<ApiResponse<{ user: User; tokens: TokenResponse }>> {
    // Normalize phone number before sending to backend
    const response = await api.post("/api/v1/auth/register", {
      ...data,
      phone: normalizePhone(data.phone),
    });
    return response.data;
  },

  /** Login with phone and password */
  async login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    const response = await api.post("/api/v1/auth/login", {
      ...data,
      phone: normalizePhone(data.phone),
    });
    return response.data;
  },

  /** Refresh access token */
  async refresh(refreshToken: string): Promise<ApiResponse<TokenResponse>> {
    const response = await api.post("/api/v1/auth/refresh", { refresh_token: refreshToken });
    return response.data;
  },

  /** Logout */
  async logout(): Promise<void> {
    await api.post("/api/v1/auth/logout");
  },

  /** Get current user profile */
  async getMe(): Promise<ApiResponse<User>> {
    const response = await api.get("/api/v1/auth/me");
    return response.data;
  },
};
