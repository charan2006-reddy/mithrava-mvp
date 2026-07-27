import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { LanguageCode } from "@/lib/constants";

interface UIStore {
  language: LanguageCode;
  sidebarOpen: boolean;
  theme: "light" | "dark" | "system";
  setLanguage: (lang: LanguageCode) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: "light" | "dark" | "system") => void;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      language: "en",
      sidebarOpen: false,
      theme: "light",

      setLanguage: (lang: LanguageCode) => {
        set({ language: lang });
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      setTheme: (theme: "light" | "dark" | "system") => {
        set({ theme });
      },
    }),
    {
      name: "mithrava-ui",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
