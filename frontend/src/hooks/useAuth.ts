"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";
import type { User, TokenResponse } from "@/types/auth";

export function useAuth() {
  const router = useRouter();
  const { user, tokens, isAuthenticated, login: storeLogin, logout: storeLogout, updateUser } = useAuthStore();

  const sendOtp = useCallback(
    async (phone: string): Promise<boolean> => {
      try {
        await authService.sendOtp(phone);
        toast.success("OTP sent to your phone");
        return true;
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Failed to send OTP";
        toast.error(message);
        return false;
      }
    },
    []
  );

  const verifyOtp = useCallback(
    async (phone: string, otp: string): Promise<boolean> => {
      try {
        const response = await authService.verifyOtp({ phone, otp });
        const rawData = response.data as unknown as Record<string, string | number | boolean>;

        // Handle needs_registration response (unregistered phone)
        if (rawData.needs_registration) {
          toast.info("Phone not registered. Please register first.");
          router.push("/register");
          return false;
        }

        // Backend returns snake_case: { access_token, refresh_token, token_type, expires_in }
        // Map to frontend camelCase TokenResponse
        const tokenData: TokenResponse = {
          accessToken: rawData.access_token as string,
          refreshToken: rawData.refresh_token as string,
          expiresIn: rawData.expires_in as number,
          tokenType: rawData.token_type as string,
        };
        // Store tokens first, then fetch user profile
        storeLogin(tokenData, null as unknown as User);
        // Fetch user profile to complete login
        try {
          const meResponse = await authService.getMe();
          // Map backend snake_case user to frontend camelCase User type
          const rawUser = meResponse.data as unknown as Record<string, string>;
          updateUser({
            id: rawUser.id,
            name: rawUser.name,
            phone: rawUser.phone,
            email: rawUser.email || undefined,
            city: rawUser.city || "",
            state: rawUser.state || "",
            language: rawUser.preferred_language || "en",
            avatar: rawUser.profile_image_url || undefined,
            role: (rawUser.role as "farmer" | "admin") || "farmer",
            createdAt: rawUser.created_at || "",
            updatedAt: rawUser.created_at || "",
          });
        } catch {
          // Token works but user fetch failed — still logged in
        }
        toast.success("Welcome back!");
        router.push("/");
        return true;
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Invalid OTP";
        toast.error(message);
        return false;
      }
    },
    [router, storeLogin, updateUser]
  );

  const register = useCallback(
    async (data: {
      name: string;
      phone: string;
      email?: string;
      city: string;
      state: string;
      language: string;
    }): Promise<boolean> => {
      try {
        const response = await authService.register(data);
        // Backend returns { farmer: {...}, tokens: {...} } with snake_case
        const backendData = response.data as unknown as {
          tokens: { access_token: string; refresh_token: string; token_type: string; expires_in: number };
          farmer: Record<string, string>;
        };
        const tokenData: TokenResponse = {
          accessToken: backendData.tokens.access_token,
          refreshToken: backendData.tokens.refresh_token,
          expiresIn: backendData.tokens.expires_in,
          tokenType: backendData.tokens.token_type,
        };
        const userData: User = {
          id: backendData.farmer.id,
          name: backendData.farmer.name,
          phone: backendData.farmer.phone,
          email: backendData.farmer.email || undefined,
          city: backendData.farmer.city || "",
          state: backendData.farmer.state || "",
          language: backendData.farmer.preferred_language || "en",
          role: (backendData.farmer.role as "farmer" | "admin") || "farmer",
          createdAt: "",
          updatedAt: "",
        };
        storeLogin(tokenData, userData);
        toast.success("Registration successful!");
        router.push("/");
        return true;
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Registration failed";
        toast.error(message);
        return false;
      }
    },
    [router, storeLogin]
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // Continue with local logout even if API fails
    } finally {
      storeLogout();
      toast.success("Logged out successfully");
      router.push("/login");
    }
  }, [router, storeLogout]);

  const refreshUser = useCallback(async () => {
    try {
      const response = await authService.getMe();
      updateUser(response.data);
    } catch {
      // Silently fail - will be caught by interceptor
    }
  }, [updateUser]);

  return {
    user,
    tokens,
    isAuthenticated,
    sendOtp,
    verifyOtp,
    register,
    logout,
    refreshUser,
    updateUser,
  };
}
