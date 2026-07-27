import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge class names with Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format amount in Indian Rupees (INR)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format date in localized format
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(d);
}

/**
 * Format date in short format
 */
export function formatDateShort(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
  }).format(d);
}

/**
 * Get initials from a name
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Truncate text to a specified length
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length).trim() + "...";
}

/**
 * Sleep utility for delays
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Generate a random ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}

/**
 * Validate Indian phone number
 */
export function isValidIndianPhone(phone: string): boolean {
  return /^[6-9]\d{9}$/.test(phone);
}

/**
 * Format phone number with country code
 */
export function formatPhoneWithCode(phone: string): string {
  return `+91${phone}`;
}

/**
 * Convert a date to a relative time string (e.g., "2 hours ago")
 */
export function timeAgo(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);
  const diffWeek = Math.floor(diffDay / 7);
  const diffMonth = Math.floor(diffDay / 30);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return diffMin === 1 ? "1 min ago" : `${diffMin} mins ago`;
  if (diffHr < 24) return diffHr === 1 ? "1 hour ago" : `${diffHr} hours ago`;
  if (diffDay < 7) return diffDay === 1 ? "yesterday" : `${diffDay} days ago`;
  if (diffWeek < 4) return diffWeek === 1 ? "1 week ago" : `${diffWeek} weeks ago`;
  if (diffMonth < 12) return diffMonth === 1 ? "1 month ago" : `${diffMonth} months ago`;
  return formatDate(d);
}

/**
 * Get severity color config (tailwind classes)
 */
export function getSeverityConfig(severity: string): {
  label: string;
  bg: string;
  text: string;
  border: string;
  ring: string;
} {
  switch (severity) {
    case "critical":
      return {
        label: "Critical",
        bg: "bg-red-100",
        text: "text-red-800",
        border: "border-red-300",
        ring: "ring-red-500",
      };
    case "high":
      return {
        label: "High",
        bg: "bg-orange-100",
        text: "text-orange-800",
        border: "border-orange-300",
        ring: "ring-orange-500",
      };
    case "medium":
      return {
        label: "Medium",
        bg: "bg-amber-100",
        text: "text-amber-800",
        border: "border-amber-300",
        ring: "ring-amber-500",
      };
    case "low":
      return {
        label: "Low",
        bg: "bg-green-100",
        text: "text-green-800",
        border: "border-green-300",
        ring: "ring-green-500",
      };
    default:
      return {
        label: "Unknown",
        bg: "bg-gray-100",
        text: "text-gray-800",
        border: "border-gray-300",
        ring: "ring-gray-500",
      };
  }
}
