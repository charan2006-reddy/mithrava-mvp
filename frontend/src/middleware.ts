/**
 * Next.js Middleware — Protects dashboard and authenticated routes.
 *
 * Checks for the auth token cookie set by the client-side auth flow.
 * Unauthenticated users are redirected to /login with a return URL.
 *
 * Public routes (landing, login, register, static assets) are always allowed.
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/** Routes that require authentication */
const PROTECTED_ROUTES = [
  "/dashboard",
  "/crops",
  "/disease",
  "/diseases",
  "/finance",
  "/forum",
  "/knowledge",
  "/market",
  "/mitra",
  "/notifications",
  "/profile",
  "/support",
  "/vendors",
  "/weather",
  "/more",
  "/admin",
];

/** Routes that are always public (no auth required) */
const PUBLIC_ROUTES = [
  "/",
  "/login",
  "/register",
  "/api",
  "/_next",
  "/favicon.ico",
  "/robots.txt",
  "/sitemap.xml",
];

/** Auth token cookie name */
const AUTH_TOKEN_COOKIE = "mithrava_access_token";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public routes and static assets
  if (PUBLIC_ROUTES.some((route) => pathname === route || pathname.startsWith(route + "/"))) {
    return NextResponse.next();
  }

  // Allow static files
  if (
    pathname.includes(".") &&
    !pathname.endsWith(".json")
  ) {
    return NextResponse.next();
  }

  // Check for auth token cookie
  const authToken = request.cookies.get(AUTH_TOKEN_COOKIE)?.value;
  const isAuthenticated = Boolean(authToken);

  // Check if this is a protected route
  const isProtectedRoute = PROTECTED_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(route + "/")
  );

  if (isProtectedRoute && !isAuthenticated) {
    // Redirect to login with return URL
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("returnTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If authenticated and trying to access login/register, redirect to dashboard
  if (isAuthenticated && (pathname === "/login" || pathname === "/register")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (browser favicon)
     * - public folder files
     */
    "/((?!_next/static|_next/image|favicon.ico|public/).*)",
  ],
};
