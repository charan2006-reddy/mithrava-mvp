/**
 * Tests for the vendor type constants — ensures alignment with backend values
 * and structural consistency.
 */

import { VENDOR_TYPES } from "@/lib/constants";

describe("VENDOR_TYPES", () => {
  it("should be a non-empty array", () => {
    expect(Array.isArray(VENDOR_TYPES)).toBe(true);
    expect(VENDOR_TYPES.length).toBeGreaterThan(0);
  });

  it("each entry should have id, name, and icon properties", () => {
    for (const vendorType of VENDOR_TYPES) {
      expect(vendorType).toHaveProperty("id");
      expect(vendorType).toHaveProperty("name");
      expect(vendorType).toHaveProperty("icon");
      expect(typeof vendorType.id).toBe("string");
      expect(typeof vendorType.name).toBe("string");
      expect(typeof vendorType.icon).toBe("string");
    }
  });

  it("should contain all backend vendor types", () => {
    const expectedIds = [
      "fertilizer_shop",
      "seed_shop",
      "equipment_rental",
      "mandi",
      "transport",
      "processor",
      "other",
    ];
    const actualIds = VENDOR_TYPES.map((v) => v.id);

    for (const expectedId of expectedIds) {
      expect(actualIds).toContain(expectedId);
    }
  });

  it("should have exactly 7 vendor types", () => {
    expect(VENDOR_TYPES.length).toBe(7);
  });

  it("should have no duplicate IDs", () => {
    const ids = VENDOR_TYPES.map((v) => v.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it("each name should be a non-empty string", () => {
    for (const vendorType of VENDOR_TYPES) {
      expect(vendorType.name.length).toBeGreaterThan(0);
    }
  });

  it("each icon should be a non-empty string (emoji)", () => {
    for (const vendorType of VENDOR_TYPES) {
      expect(vendorType.icon.length).toBeGreaterThan(0);
    }
  });

  it("should match the VendorType union type values", () => {
    // These are the exact values defined in types/vendor.ts
    const backendVendorTypes: readonly string[] = [
      "fertilizer_shop",
      "seed_shop",
      "equipment_rental",
      "mandi",
      "transport",
      "processor",
      "other",
    ];

    const actualIds = VENDOR_TYPES.map((v) => v.id);

    // No extra types beyond what the backend supports
    for (const actualId of actualIds) {
      expect(backendVendorTypes).toContain(actualId);
    }

    // No missing types from what the backend supports
    for (const backendType of backendVendorTypes) {
      expect(actualIds).toContain(backendType);
    }
  });
});
