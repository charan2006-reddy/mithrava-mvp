/** API base URL from environment */
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Supported languages */
export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English", flag: "🇮🇳" },
  { code: "hi", name: "हिंदी", flag: "🇮🇳" },
  { code: "te", name: "తెలుగు", flag: "🇮🇳" },
  { code: "kn", name: "ಕನ್ನಡ", flag: "🇮🇳" },
  { code: "ta", name: "தமிழ்", flag: "🇮🇳" },
] as const;

export type LanguageCode = (typeof SUPPORTED_LANGUAGES)[number]["code"];

/** Major Indian crops */
export const CROP_LIST = [
  "Rice (Paddy)",
  "Wheat",
  "Maize (Corn)",
  "Cotton",
  "Sugarcane",
  "Groundnut",
  "Soybean",
  "Tomato",
  "Potato",
  "Onion",
  "Chilli",
  "Turmeric",
  "Ginger",
  "Cardamom",
  "Black Pepper",
  "Coconut",
  "Banana",
  "Mango",
  "Grapes",
  "Pomegranate",
  "Watermelon",
  "Brinjal (Eggplant)",
  "Okra (Lady Finger)",
  "Cabbage",
  "Cauliflower",
  "Carrot",
  "Green Gram (Moong)",
  "Black Gram (Urad)",
  "Bengal Gram (Chana)",
  "Pigeon Pea (Toor)",
] as const;

/** Expense categories */
export const EXPENSE_CATEGORIES = [
  { id: "seeds", name: "Seeds", icon: "🌱" },
  { id: "fertilizer", name: "Fertilizer", icon: "🧪" },
  { id: "pesticide", name: "Pesticide", icon: "🧴" },
  { id: "irrigation", name: "Irrigation", icon: "💧" },
  { id: "labor", name: "Labor", icon: "👷" },
  { id: "equipment", name: "Equipment", icon: "🚜" },
  { id: "transport", name: "Transport", icon: "🚛" },
  { id: "storage", name: "Storage", icon: "🏭" },
  { id: "land_rent", name: "Land Rent", icon: "🏞️" },
  { id: "other", name: "Other", icon: "📦" },
] as const;

/** Vendor types — must match backend vendor_type values */
export const VENDOR_TYPES = [
  { id: "fertilizer_shop", name: "Fertilizer Dealer", icon: "🧪" },
  { id: "seed_shop", name: "Seed Shop", icon: "🌱" },
  { id: "equipment_rental", name: "Equipment Dealer", icon: "🚜" },
  { id: "mandi", name: "Buyer / Mandi", icon: "🏪" },
  { id: "transport", name: "Transport Provider", icon: "🚛" },
  { id: "processor", name: "Processor", icon: "🏭" },
  { id: "other", name: "Other", icon: "📦" },
] as const;

/** Navigation items for bottom nav */
export const NAVIGATION_ITEMS = [
  { id: "home", label: "Home", icon: "home", path: "/", emoji: "🏠", isCenter: false },
  { id: "disease", label: "Disease", icon: "microscope", path: "/diseases", emoji: "🔬", isCenter: false },
  { id: "mitra", label: "Mitra", icon: "bot", path: "/mitra", emoji: "🤖", isCenter: true },
  { id: "market", label: "Market", icon: "trending-up", path: "/market", emoji: "💰", isCenter: false },
  { id: "more", label: "More", icon: "more-horizontal", path: "/more", emoji: "⋯", isCenter: false },
] as const;

/** Sidebar navigation items */
export const SIDEBAR_NAVIGATION = [
  { id: "home", label: "Home", icon: "home", path: "/", emoji: "🏠" },
  { id: "crops", label: "My Crops", icon: "sprout", path: "/crops", emoji: "🌾" },
  { id: "disease", label: "Disease Detection", icon: "microscope", path: "/diseases", emoji: "🔬" },
  { id: "weather", label: "Weather", icon: "cloud-sun", path: "/weather", emoji: "⛅" },
  { id: "market", label: "Market Prices", icon: "trending-up", path: "/market", emoji: "💰" },
  { id: "finance", label: "Finance", icon: "wallet", path: "/finance", emoji: "📊" },
  { id: "vendors", label: "Vendors", icon: "store", path: "/vendors", emoji: "🏪" },
  { id: "forum", label: "Forum", icon: "users", path: "/forum", emoji: "💬" },
  { id: "support", label: "Expert Support", icon: "phone", path: "/support", emoji: "📞" },
] as const;

/** Quick actions for Mitra */
export const MITRA_QUICK_ACTIONS = [
  { id: "weather", label: "Check weather", emoji: "⛅", prompt: "What is the weather today?" },
  { id: "crops", label: "My crops", emoji: "🌾", prompt: "Show me my crops status" },
  { id: "market", label: "Market prices", emoji: "💰", prompt: "What are today's market prices?" },
  { id: "disease", label: "Report disease", emoji: "🔬", prompt: "I want to report a crop disease" },
  { id: "help", label: "Help", emoji: "📞", prompt: "I need help from an expert" },
] as const;
