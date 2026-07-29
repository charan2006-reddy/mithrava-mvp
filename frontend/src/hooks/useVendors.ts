"use client";

import { useQuery } from "@tanstack/react-query";
import { vendorService } from "@/services/vendorService";
import type { Vendor, VendorFilter } from "@/types/vendor";

/**
 * Fetch vendors from the API, with optional type/city filters.
 * Returns the unwrapped `items` array from the paginated response.
 */
export function useVendors(filter?: VendorFilter) {
  return useQuery({
    queryKey: ["vendors", filter],
    queryFn: async () => {
      const res = await vendorService.list(filter);
      return ((res.data as unknown) as { vendors: Vendor[] })?.vendors ?? [];
    },
  });
}
