"use client";

import { useState } from "react";
import { Globe, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { SUPPORTED_LANGUAGES } from "@/lib/constants";

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);

  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === language);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium transition-colors hover:bg-gray-50 min-h-[48px]"
        )}
        aria-label="Select language"
      >
        <Globe className="h-5 w-5 text-mithrava-500" />
        <span>{currentLang?.flag}</span>
        <span>{currentLang?.name}</span>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full z-50 mt-1 w-56 rounded-lg border bg-white shadow-lg overflow-hidden">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
                className={cn(
                  "flex w-full items-center gap-3 px-4 py-3 text-sm transition-colors",
                  language === lang.code
                    ? "bg-mithrava-50 text-mithrava-600 font-medium"
                    : "hover:bg-gray-50"
                )}
              >
                <span className="text-lg">{lang.flag}</span>
                <span className="flex-1 text-left">{lang.name}</span>
                {language === lang.code && (
                  <Check className="h-4 w-4 text-mithrava-500" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
