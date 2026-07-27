"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { NAVIGATION_ITEMS } from "@/lib/constants";

export function BottomNav() {
  const pathname = usePathname();
  const { t } = useLanguage();

  const navLabelMap: Record<string, string> = {
    home: "nav.home",
    disease: "nav.disease",
    mitra: "mitra.title",
    market: "nav.market",
    more: "nav.settings",
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-gray-200 bg-white md:hidden safe-area-bottom">
      <div className="flex items-center justify-around px-2 py-1">
        {NAVIGATION_ITEMS.map((item) => {
          const isActive =
            pathname === item.path ||
            (item.path !== "/" && pathname.startsWith(item.path));

          if (item.isCenter) {
            return (
              <Link
                key={item.id}
                href={item.path}
                className="relative -mt-6"
              >
                <div
                  className={cn(
                    "flex h-16 w-16 items-center justify-center rounded-full shadow-lg transition-all duration-200",
                    isActive
                      ? "bg-mithrava-600 scale-110"
                      : "bg-mithrava-500 hover:bg-mithrava-600"
                  )}
                >
                  <span className="text-2xl">{item.emoji}</span>
                </div>
              </Link>
            );
          }

          return (
            <Link
              key={item.id}
              href={item.path}
              className={cn(
                "flex flex-col items-center gap-0.5 px-3 py-2 min-w-[56px] min-h-[48px] justify-center rounded-lg transition-colors",
                isActive
                  ? "text-mithrava-600"
                  : "text-gray-500 hover:text-gray-700"
              )}
            >
              <span className="text-xl">{item.emoji}</span>
              <span className="text-[10px] font-medium leading-tight">
                {t(navLabelMap[item.id] || "")}
              </span>
              {isActive && (
                <div className="absolute bottom-1 h-1 w-8 rounded-full bg-mithrava-500" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
