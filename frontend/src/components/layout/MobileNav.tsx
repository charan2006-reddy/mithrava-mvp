"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Sprout,
  Microscope,
  CloudSun,
  TrendingUp,
  Wallet,
  Store,
  Users,
  Phone,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { useUIStore } from "@/stores/uiStore";

const iconMap: Record<string, React.ElementType> = {
  home: Home,
  crops: Sprout,
  disease: Microscope,
  weather: CloudSun,
  market: TrendingUp,
  finance: Wallet,
  vendors: Store,
  forum: Users,
  support: Phone,
};

const MOBILE_NAV_ITEMS = [
  { id: "home", labelKey: "nav.home", path: "/" },
  { id: "crops", labelKey: "nav.crops", path: "/crops" },
  { id: "disease", labelKey: "nav.disease", path: "/disease" },
  { id: "weather", labelKey: "nav.weather", path: "/weather" },
  { id: "market", labelKey: "nav.market", path: "/market" },
  { id: "finance", labelKey: "nav.finance", path: "/finance" },
  { id: "vendors", labelKey: "nav.vendors", path: "/vendors" },
  { id: "forum", labelKey: "nav.forum", path: "/forum" },
  { id: "support", labelKey: "nav.support", path: "/support" },
];

export function MobileNav() {
  const pathname = usePathname();
  const { t } = useLanguage();
  const { sidebarOpen, setSidebarOpen } = useUIStore();

  if (!sidebarOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/50 md:hidden"
        onClick={() => setSidebarOpen(false)}
      />

      {/* Slide-out Menu */}
      <div className="fixed inset-y-0 left-0 z-50 w-72 bg-white shadow-xl md:hidden animate-in slide-in-from-left duration-300">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-mithrava-500 text-white text-xl font-bold">
              🌾
            </div>
            <span className="text-xl font-bold text-mithrava-600">Mithrava</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="overflow-y-auto py-4">
          {MOBILE_NAV_ITEMS.map((item) => {
            const Icon = iconMap[item.id] || Home;
            const isActive =
              pathname === item.path ||
              (item.path !== "/" && pathname.startsWith(item.path));

            return (
              <Link
                key={item.id}
                href={item.path}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-6 py-4 transition-colors min-h-[52px]",
                  isActive
                    ? "bg-mithrava-50 text-mithrava-600 font-medium border-r-4 border-mithrava-500"
                    : "text-gray-600 hover:bg-gray-50"
                )}
              >
                <Icon className={cn("h-5 w-5", isActive && "text-mithrava-500")} />
                <span className="text-base">{t(item.labelKey)}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </>
  );
}
