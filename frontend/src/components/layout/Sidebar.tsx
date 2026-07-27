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
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { useUIStore } from "@/stores/uiStore";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { getInitials } from "@/lib/utils";

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

const SIDEBAR_ITEMS = [
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

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const { t } = useLanguage();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r border-gray-200 bg-white transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      {/* Collapse Toggle */}
      <button
        onClick={toggleSidebar}
        className="flex h-12 items-center justify-center border-b border-gray-200 hover:bg-gray-50 transition-colors"
        aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
      >
        {sidebarOpen ? (
          <PanelLeftClose className="h-5 w-5 text-gray-500" />
        ) : (
          <PanelLeft className="h-5 w-5 text-gray-500" />
        )}
      </button>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4">
        {SIDEBAR_ITEMS.map((item) => {
          const Icon = iconMap[item.id] || Home;
          const isActive =
            pathname === item.path ||
            (item.path !== "/" && pathname.startsWith(item.path));

          return (
            <Link
              key={item.id}
              href={item.path}
              className={cn(
                "flex items-center gap-3 px-4 py-3 mx-2 rounded-lg transition-colors min-h-[48px]",
                isActive
                  ? "bg-mithrava-50 text-mithrava-600 font-medium"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <Icon className={cn("h-5 w-5 shrink-0", isActive && "text-mithrava-500")} />
              {sidebarOpen && (
                <span className="text-sm">{t(item.labelKey)}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Info at Bottom */}
      {user && (
        <div className="border-t border-gray-200 p-4">
          <div className={cn("flex items-center gap-3", !sidebarOpen && "justify-center")}>
            <Avatar className="h-9 w-9 shrink-0">
              <AvatarImage src={user.avatar} alt={user.name} />
              <AvatarFallback className="text-sm">
                {getInitials(user.name)}
              </AvatarFallback>
            </Avatar>
            {sidebarOpen && (
              <div className="overflow-hidden">
                <p className="text-sm font-medium truncate">{user.name}</p>
                <p className="text-xs text-gray-500 truncate">{user.city}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
