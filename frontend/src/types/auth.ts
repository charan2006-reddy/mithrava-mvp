/** User model */
export interface User {
  id: string;
  name: string;
  phone: string;
  email?: string;
  city: string;
  state: string;
  language: string;
  avatar?: string;
  voiceEnabled?: boolean;
  notificationsEnabled?: boolean;
  role: "farmer" | "admin";
  createdAt: string;
  updatedAt: string;
}

/** Login request with phone */
export interface LoginRequest {
  phone: string;
}

/** OTP verification request */
export interface OTPRequest {
  phone: string;
  otp: string;
}

/** Token response */
export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
}

/** Register request */
export interface RegisterRequest {
  name: string;
  phone: string;
  email?: string;
  city: string;
  state: string;
  language: string;
}

/** Auth state */
export interface AuthState {
  user: User | null;
  tokens: TokenResponse | null;
  isAuthenticated: boolean;
}
