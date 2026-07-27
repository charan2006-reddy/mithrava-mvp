/** Vendor type — must match backend vendor_type values */
export type VendorType =
  | "fertilizer_shop"
  | "seed_shop"
  | "equipment_rental"
  | "mandi"
  | "transport"
  | "processor"
  | "other";

/** Vendor model — matches backend snake_case response */
export interface Vendor {
  id: string;
  name: string;
  vendor_type: VendorType;
  phone: string;
  email?: string;
  city: string;
  state?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  rating: number;
  review_count: number;
  is_verified: boolean;
  description?: string;
  services?: string[];
  operating_hours?: string;
  reviews?: VendorReview[];
  created_at?: string;
  updated_at?: string;
}

/** Vendor review — matches backend snake_case response */
export interface VendorReview {
  id: string;
  vendor_id: string;
  farmer_id: string;
  rating: number;
  comment?: string;
  created_at?: string;
}

/** Add vendor review request */
export interface AddReviewRequest {
  rating: number;
  comment: string;
}

/** Vendor filter — matches backend query params */
export interface VendorFilter {
  city?: string;
  vendor_type?: string;
}
