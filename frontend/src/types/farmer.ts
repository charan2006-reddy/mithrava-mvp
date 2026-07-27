/** Farmer model */
export interface Farmer {
  id: string;
  userId: string;
  name: string;
  phone: string;
  email?: string;
  city: string;
  state: string;
  language: string;
  totalLand: number;
  landUnit: "acres" | "hectares";
  createdAt: string;
  updatedAt: string;
}

/** Land model */
export interface Land {
  id: string;
  farmerId: string;
  name: string;
  area: number;
  areaUnit: "acres" | "hectares";
  soilType?: string;
  irrigationType?: string;
  location?: string;
  latitude?: number;
  longitude?: number;
  createdAt: string;
  updatedAt: string;
}

/** Dashboard statistics */
export interface FarmerStats {
  activeCrops: number;
  totalLand: number;
  totalLandUnit: "acres" | "hectares";
  readyToHarvest: number;
  monthlyProfit: number;
  isProfit: boolean;
  totalExpenses: number;
  totalIncome: number;
}

/** Farmer profile update request */
export interface FarmerProfileUpdate {
  name?: string;
  email?: string;
  city?: string;
  state?: string;
  language?: string;
  voiceEnabled?: boolean;
  notificationsEnabled?: boolean;
  theme?: "light" | "dark";
}

/** Farmer profile response */
export interface FarmerProfile {
  id: string;
  userId: string;
  name: string;
  phone: string;
  email?: string;
  city: string;
  state: string;
  language: string;
  avatar?: string;
  voiceEnabled: boolean;
  notificationsEnabled: boolean;
  theme: "light" | "dark";
  totalLand: number;
  landUnit: "acres" | "hectares";
  createdAt: string;
  updatedAt: string;
}
