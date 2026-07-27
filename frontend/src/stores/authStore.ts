import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User, TokenResponse } from "@/types/auth";
import { setAuthCookies, clearAuthCookies } from "@/lib/cookies";

interface AuthStore {
  user: User | null;
  tokens: TokenResponse | null;
  isAuthenticated: boolean;
  login: (tokens: TokenResponse, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setTokens: (tokens: TokenResponse) => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,

      login: (tokens: TokenResponse, user: User) => {
        set({
          tokens,
          user,
          isAuthenticated: true,
        });
        // Mirror to cookies so middleware can check auth state
        setAuthCookies(tokens.accessToken, JSON.stringify(user));
      },

      logout: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        });
        // Clear auth cookies
        clearAuthCookies();
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          const updated = { ...currentUser, ...userData };
          set({ user: updated });
          // Update user cookie
          const tokens = get().tokens;
          if (tokens?.accessToken) {
            setAuthCookies(tokens.accessToken, JSON.stringify(updated));
          }
        }
      },

      setTokens: (tokens: TokenResponse) => {
        set({ tokens });
        // Mirror updated tokens to cookies
        const user = get().user;
        if (user) {
          setAuthCookies(tokens.accessToken, JSON.stringify(user));
        }
      },
    }),
    {
      name: "mithrava-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
