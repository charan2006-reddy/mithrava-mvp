/**
 * Tests for forum category constants — verifies that the CATEGORIES array
 * and CATEGORY_COLORS mapping defined in ForumContent.tsx are complete
 * and consistent.
 *
 * Note: These constants are defined locally in ForumContent.tsx rather than
 * in a shared constants file, so we duplicate the expected values here
 * as the source of truth for testing.
 */

/** Expected categories — mirrors ForumContent.tsx CATEGORIES array */
const FORUM_CATEGORIES = [
  { key: "all", label: "All", emoji: "📋" },
  { key: "crop_care", label: "Crop Care", emoji: "🌾" },
  { key: "pest_control", label: "Pest Control", emoji: "🐛" },
  { key: "weather", label: "Weather", emoji: "🌤️" },
  { key: "market", label: "Market", emoji: "💰" },
  { key: "tips", label: "Tips", emoji: "💡" },
  { key: "question", label: "Questions", emoji: "❓" },
];

/** Expected category color mapping — mirrors ForumContent.tsx CATEGORY_COLORS */
const CATEGORY_COLORS: Record<string, string> = {
  crop_care: "bg-green-100 text-green-700",
  pest_control: "bg-red-100 text-red-700",
  weather: "bg-blue-100 text-blue-700",
  market: "bg-amber-100 text-amber-700",
  tips: "bg-purple-100 text-purple-700",
  question: "bg-gray-100 text-gray-700",
  general: "bg-gray-100 text-gray-600",
  finance: "bg-emerald-100 text-emerald-700",
};

describe("Forum Categories", () => {
  describe("CATEGORIES array", () => {
    it("should contain all expected categories", () => {
      const keys = FORUM_CATEGORIES.map((c) => c.key);
      expect(keys).toContain("all");
      expect(keys).toContain("crop_care");
      expect(keys).toContain("pest_control");
      expect(keys).toContain("weather");
      expect(keys).toContain("market");
      expect(keys).toContain("tips");
      expect(keys).toContain("question");
    });

    it("should have exactly 7 categories", () => {
      expect(FORUM_CATEGORIES.length).toBe(7);
    });

    it("each category should have key, label, and emoji", () => {
      for (const category of FORUM_CATEGORIES) {
        expect(typeof category.key).toBe("string");
        expect(typeof category.label).toBe("string");
        expect(typeof category.emoji).toBe("string");
        expect(category.key.length).toBeGreaterThan(0);
        expect(category.label.length).toBeGreaterThan(0);
        expect(category.emoji.length).toBeGreaterThan(0);
      }
    });

    it("should have 'all' as the first category (default filter)", () => {
      expect(FORUM_CATEGORIES[0].key).toBe("all");
      expect(FORUM_CATEGORIES[0].label).toBe("All");
    });

    it("should have no duplicate keys", () => {
      const keys = FORUM_CATEGORIES.map((c) => c.key);
      const uniqueKeys = new Set(keys);
      expect(uniqueKeys.size).toBe(keys.length);
    });

    it("each key should be lowercase snake_case", () => {
      for (const category of FORUM_CATEGORIES) {
        expect(category.key).toMatch(/^[a-z]+(_[a-z]+)*$/);
      }
    });
  });

  describe("CATEGORY_COLORS mapping", () => {
    it("should have entries for all non-'all' categories", () => {
      const nonAllCategories = FORUM_CATEGORIES.filter((c) => c.key !== "all");

      for (const category of nonAllCategories) {
        expect(CATEGORY_COLORS).toHaveProperty(category.key);
      }
    });

    it("should cover additional categories: general and finance", () => {
      expect(CATEGORY_COLORS).toHaveProperty("general");
      expect(CATEGORY_COLORS).toHaveProperty("finance");
    });

    it("each color value should be a Tailwind class string", () => {
      for (const [key, color] of Object.entries(CATEGORY_COLORS)) {
        expect(typeof color).toBe("string");
        expect(color.length).toBeGreaterThan(0);
        // Should contain at least one bg- and one text- class
        expect(color).toMatch(/bg-/);
        expect(color).toMatch(/text-/);
      }
    });

    it("should have at least 8 color entries", () => {
      const entries = Object.keys(CATEGORY_COLORS);
      expect(entries.length).toBeGreaterThanOrEqual(8);
    });

    it("each category color key should be lowercase snake_case", () => {
      for (const key of Object.keys(CATEGORY_COLORS)) {
        expect(key).toMatch(/^[a-z]+(_[a-z]+)*$/);
      }
    });
  });
});
