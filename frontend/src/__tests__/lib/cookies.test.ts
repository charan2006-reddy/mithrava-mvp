/**
 * Tests for the cookie utility functions.
 */

import { setAuthCookies, clearAuthCookies, parseCookies, AUTH_TOKEN_NAME } from "@/lib/cookies";

describe("Cookie Helpers", () => {
  beforeEach(() => {
    // Clear all cookies before each test
    document.cookie.split(";").forEach((c) => {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  });

  describe("setAuthCookies", () => {
    it("should set the access token cookie", () => {
      setAuthCookies("test-token-123", '{"id":"1","name":"Test"}');

      const cookies = parseCookies(document.cookie);
      expect(cookies[AUTH_TOKEN_NAME]).toBe("test-token-123");
    });

    it("should set the user cookie with encoded JSON", () => {
      const userJson = JSON.stringify({ id: "1", name: "Test User" });
      setAuthCookies("token", userJson);

      const cookies = parseCookies(document.cookie);
      expect(cookies["mithrava_user"]).toBe(userJson);
    });
  });

  describe("clearAuthCookies", () => {
    it("should remove both auth cookies", () => {
      setAuthCookies("token", "user");
      clearAuthCookies();

      const cookies = parseCookies(document.cookie);
      expect(cookies[AUTH_TOKEN_NAME]).toBeUndefined();
      expect(cookies["mithrava_user"]).toBeUndefined();
    });
  });

  describe("parseCookies", () => {
    it("should parse a cookie header string", () => {
      const result = parseCookies("foo=bar; baz=qux");
      expect(result).toEqual({ foo: "bar", baz: "qux" });
    });

    it("should handle empty string", () => {
      expect(parseCookies("")).toEqual({});
    });

    it("should handle URI-encoded values", () => {
      const result = parseCookies("key=" + encodeURIComponent("hello world"));
      expect(result.key).toBe("hello world");
    });
  });
});
