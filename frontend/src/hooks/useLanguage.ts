"use client";

import { useCallback, useMemo, useEffect, useState } from "react";
import { useUIStore } from "@/stores/uiStore";
import { translations as enTranslations } from "@/lib/languages";
import type { TranslationKeys } from "@/lib/languages";
import type { LanguageCode } from "@/lib/constants";

// ---------------------------------------------------------------------------
// Lazy-loading cache for non-English translations
// ---------------------------------------------------------------------------

const translationCache = new Map<LanguageCode, TranslationKeys>();

/** Register a language's translations (used for pre-warming the cache) */
export function registerTranslations(
  lang: LanguageCode,
  data: TranslationKeys
) {
  translationCache.set(lang, data);
}

/** Import map — language code → dynamic import function */
const languageLoaders: Record<
  string,
  () => Promise<{ default: TranslationKeys }>
> = {
  hi: () => import("@/lib/translations-hi"),
  te: () => import("@/lib/translations-te"),
  kn: () => import("@/lib/translations-kn"),
  ta: () => import("@/lib/translations-ta"),
};

async function loadTranslations(
  lang: LanguageCode
): Promise<TranslationKeys | null> {
  // Already cached?
  if (translationCache.has(lang)) {
    return translationCache.get(lang)!;
  }

  const loader = languageLoaders[lang];
  if (!loader) return null;

  try {
    const mod = await loader();
    translationCache.set(lang, mod.default);
    return mod.default;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useLanguage() {
  const { language, setLanguage: storeSetLanguage } = useUIStore();
  const [customTranslations, setCustomTranslations] =
    useState<TranslationKeys | null>(null);
  const [isLoadingLang, setIsLoadingLang] = useState(false);

  // Load non-English translations when language changes
  useEffect(() => {
    if (language === "en") {
      setCustomTranslations(null);
      return;
    }

    let cancelled = false;
    setIsLoadingLang(true);

    loadTranslations(language).then((data) => {
      if (cancelled) return;
      setCustomTranslations(data);
      setIsLoadingLang(false);
    });

    return () => {
      cancelled = true;
    };
  }, [language]);

  /** Get translation for a dot-separated key */
  const t = useCallback(
    (key: string): string => {
      const keys = key.split(".");
      const langData = customTranslations ?? enTranslations[language as LanguageCode] ?? enTranslations["en"];

      let result: unknown = langData;

      for (const k of keys) {
        if (
          result &&
          typeof result === "object" &&
          k in (result as Record<string, unknown>)
        ) {
          result = (result as Record<string, unknown>)[k];
        } else {
          // Fallback to English
          let fallback: unknown = enTranslations["en"];
          for (const fbKey of keys) {
            if (
              fallback &&
              typeof fallback === "object" &&
              fbKey in (fallback as Record<string, unknown>)
            ) {
              fallback = (fallback as Record<string, unknown>)[fbKey];
            } else {
              return key;
            }
          }
          return typeof fallback === "string" ? fallback : key;
        }
      }

      return typeof result === "string" ? result : key;
    },
    [language, customTranslations]
  );

  const setLanguage = useCallback(
    (lang: LanguageCode) => {
      storeSetLanguage(lang);
    },
    [storeSetLanguage]
  );

  /** Current language config */
  const currentLanguage = useMemo(
    () => ({
      code: language,
      name:
        language === "en"
          ? "English"
          : language === "hi"
          ? "हिंदी"
          : language === "te"
          ? "తెలుగు"
          : language === "kn"
          ? "ಕನ್ನಡ"
          : "தமிழ்",
    }),
    [language]
  );

  return {
    t,
    language,
    setLanguage,
    currentLanguage,
    isLoadingLang,
  };
}
