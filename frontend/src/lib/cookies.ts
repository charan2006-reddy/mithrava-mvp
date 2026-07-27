/**
 * Cookie helpers for auth tokens.
 *
 * Next.js middleware runs on the server/edge and cannot access localStorage.
 * We mirror auth tokens into HttpOnly-compatible cookies so middleware can
 * verify authentication state. The cookies are set/read by client-side code
 * and checked by middleware.
 */

const AUTH_TOKEN_COOKIE = "mithrava_access_token";
const AUTH_USER_COOKIE = "mithrava_user";

/** Set auth cookies (called on login/register/refresh) */
export function setAuthCookies(accessToken: string, userJson: string): void {
  if (typeof document === "undefined") return;

  // Access token — 7 day expiry to match refresh token lifecycle
  document.cookie = `${AUTH_TOKEN_COOKIE}=${encodeURIComponent(accessToken)}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;

  // User JSON (non-sensitive profile data)
  document.cookie = `${AUTH_USER_COOKIE}=${encodeURIComponent(userJson)}; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Lax`;
}

/** Clear auth cookies (called on logout) */
export function clearAuthCookies(): void {
  if (typeof document === "undefined") return;

  document.cookie = `${AUTH_TOKEN_COOKIE}=; path=/; max-age=0`;
  document.cookie = `${AUTH_USER_COOKIE}=; path=/; max-age=0`;
}

/**
 * Parse cookies from the Cookie header string (used in middleware).
 * Returns a key-value map.
 */
export function parseCookies(cookieHeader: string): Record<string, string> {
  const cookies: Record<string, string> = {};
  if (!cookieHeader) return cookies;

  for (const pair of cookieHeader.split(";")) {
    const [key, ...rest] = pair.split("=");
    if (key && rest.length > 0) {
      cookies[key.trim()] = decodeURIComponent(rest.join("=").trim());
    }
  }
  return cookies;
}

/** Get the auth token cookie name (for middleware) */
export const AUTH_TOKEN_NAME = AUTH_TOKEN_COOKIE;
