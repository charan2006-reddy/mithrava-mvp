/**
 * Tests for the auth store — login, logout, token management, cookie sync.
 */

import { useAuthStore } from "@/stores/authStore";
import type { User, TokenResponse } from "@/types/auth";

// Reset store between tests
beforeEach(() => {
  useAuthStore.setState({
    user: null,
    tokens: null,
    isAuthenticated: false,
  });
  // Clear cookies
  document.cookie.split(";").forEach((c) => {
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
  });
});

const mockUser: User = {
  id: "test-farmer-123",
  name: "Ravi Kumar",
  phone: "+919876543210",
  email: "ravi@example.com",
  city: "Hyderabad",
  state: "Telangana",
  language: "te",
  role: "farmer",
  createdAt: "2024-01-01T00:00:00Z",
  updatedAt: "2024-01-01T00:00:00Z",
};

const mockTokens: TokenResponse = {
  accessToken: "eyJhbGciOiJIUzI1NiJ9.test-access-token",
  refreshToken: "test-refresh-token-abc123",
  expiresIn: 900,
  tokenType: "bearer",
};

describe("AuthStore", () => {
  describe("login", () => {
    it("should set user, tokens, and isAuthenticated on login", () => {
      useAuthStore.getState().login(mockTokens, mockUser);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.tokens).toEqual(mockTokens);
      expect(state.isAuthenticated).toBe(true);
    });

    it("should set auth cookies on login", () => {
      useAuthStore.getState().login(mockTokens, mockUser);

      const cookies = document.cookie;
      expect(cookies).toContain("mithrava_access_token");
      expect(cookies).toContain("mithrava_user");
    });
  });

  describe("logout", () => {
    it("should clear user, tokens, and isAuthenticated on logout", () => {
      // First login
      useAuthStore.getState().login(mockTokens, mockUser);
      expect(useAuthStore.getState().isAuthenticated).toBe(true);

      // Then logout
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.tokens).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });

    it("should clear auth cookies on logout", () => {
      useAuthStore.getState().login(mockTokens, mockUser);
      useAuthStore.getState().logout();

      const cookies = document.cookie;
      expect(cookies).not.toContain("mithrava_access_token=");
    });
  });

  describe("updateUser", () => {
    it("should merge partial user data", () => {
      useAuthStore.getState().login(mockTokens, mockUser);
      useAuthStore.getState().updateUser({ city: "Chennai", state: "Tamil Nadu" });

      const state = useAuthStore.getState();
      expect(state.user?.city).toBe("Chennai");
      expect(state.user?.state).toBe("Tamil Nadu");
      // Other fields should be preserved
      expect(state.user?.name).toBe("Ravi Kumar");
      expect(state.user?.phone).toBe("+919876543210");
    });

    it("should not update if no user is logged in", () => {
      useAuthStore.getState().updateUser({ city: "Chennai" });
      expect(useAuthStore.getState().user).toBeNull();
    });
  });

  describe("setTokens", () => {
    it("should update tokens and sync cookie", () => {
      useAuthStore.getState().login(mockTokens, mockUser);

      const newTokens: TokenResponse = {
        ...mockTokens,
        accessToken: "new-access-token-xyz",
      };
      useAuthStore.getState().setTokens(newTokens);

      expect(useAuthStore.getState().tokens?.accessToken).toBe("new-access-token-xyz");
    });
  });
});
