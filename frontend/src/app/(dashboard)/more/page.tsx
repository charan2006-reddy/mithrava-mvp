"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { motion } from "framer-motion";
import {
  User,
  Bell,
  BookOpen,
  Shield,
  Phone,
  Globe,
  Moon,
  LogOut,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/stores/uiStore";
import { LanguageSwitcher } from "@/components/shared/LanguageSwitcher";

const MORE_ITEMS = [
  {
    id: "profile",
    labelKey: "nav.profile",
    icon: User,
    href: "/profile",
    color: "bg-mithrava-50 text-mithrava-600",
  },
  {
    id: "notifications",
    labelKey: "notifications.title",
    labelFallback: "Notifications",
    icon: Bell,
    href: "/notifications",
    color: "bg-amber-50 text-amber-600",
  },
  {
    id: "knowledge",
    labelKey: "knowledge.title",
    labelFallback: "Knowledge Base",
    icon: BookOpen,
    href: "/knowledge",
    color: "bg-blue-50 text-blue-600",
  },
  {
    id: "admin",
    labelKey: "nav.admin",
    icon: Shield,
    href: "/admin",
    color: "bg-red-50 text-red-600",
  },
  {
    id: "support",
    labelKey: "nav.support",
    icon: Phone,
    href: "/support",
    color: "bg-green-50 text-green-600",
  },
];

export default function MorePage() {
  const { t } = useLanguage();
  const { logout } = useAuth();
  const { theme, setTheme } = useUIStore();
  const router = useRouter();

  const handleLogout = useCallback(() => {
    if (confirm(t("auth.logoutSuccess") + "?")) {
      logout();
    }
  }, [logout, t]);

  const handleThemeToggle = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [theme, setTheme]);

  return (
    <div className="p-4 space-y-4 pb-8">
      <h1 className="text-2xl font-bold">⚙️ {t("nav.settings")}</h1>

      {/* ── Navigation Grid ── */}
      <div className="grid grid-cols-2 gap-3">
        {MORE_ITEMS.map((item, index) => {
          const Icon = item.icon;
          const label = t(item.labelKey) || item.labelFallback || item.id;
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link href={item.href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer border-gray-200">
                  <CardContent className="p-4 flex flex-col items-center gap-3 text-center">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-xl ${item.color}`}
                    >
                      <Icon className="h-6 w-6" />
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      {label}
                    </span>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* ── Language Switcher ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50">
                <Globe className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-sm font-medium">{t("auth.languageLabel")}</p>
                <p className="text-xs text-gray-500">Change app language</p>
              </div>
            </div>
            <LanguageSwitcher />
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Dark Mode Toggle ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
      >
        <Card className="border-gray-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
                <Moon className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Dark Mode</p>
                <p className="text-xs text-gray-500">
                  {theme === "dark" ? "Dark mode enabled" : "Light mode enabled"}
                </p>
              </div>
            </div>
            <button
              onClick={handleThemeToggle}
              className="relative h-7 w-12 rounded-full transition-colors min-h-[44px] min-w-[44px] flex items-center"
              role="switch"
              aria-checked={theme === "dark"}
            >
              <span
                className={`absolute h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${
                  theme === "dark"
                    ? "translate-x-6 bg-mithrava-500"
                    : "translate-x-1"
                }`}
              />
            </button>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Logout Button ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="border-gray-200">
          <CardContent className="p-0">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-red-50 transition-colors rounded-lg"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-50">
                <LogOut className="h-5 w-5 text-red-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-red-600">
                  {t("nav.logout")}
                </p>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-400" />
            </button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
