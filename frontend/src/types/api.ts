/** Base API response wrapper */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/** Paginated response */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/** API error response */
export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, string[]>;
}

/** Pagination request params */
export interface PaginationParams {
  /** Page number (1-indexed) — converted to skip/limit for backend */
  page?: number;
  /** Items per page — converted to skip/limit for backend */
  pageSize?: number;
  /** Backend-native skip parameter (takes precedence over page if both set) */
  skip?: number;
  /** Backend-native limit parameter (takes precedence over pageSize if both set) */
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

/** Weather condition */
export interface WeatherCondition {
  id: number;
  main: string;
  description: string;
  icon: string;
}

/** Coordinates */
export interface Coordinates {
  lat: number;
  lon: number;
}

/** Location info */
export interface LocationInfo {
  name: string;
  country: string;
  state?: string;
  coordinates: Coordinates;
}
