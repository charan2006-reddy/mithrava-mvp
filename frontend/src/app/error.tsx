"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4 text-center">
      <div className="text-6xl mb-6">⚠️</div>
      <h1 className="text-4xl font-bold text-gray-900 mb-2">Oops!</h1>
      <p className="text-lg text-gray-500 mb-1">Something went wrong</p>
      <p className="text-sm text-gray-400 mb-6 max-w-md">
        We encountered an unexpected error. Please try again or contact support if the issue persists.
      </p>
      {error.digest && (
        <p className="text-xs text-gray-300 mb-4 font-mono">Error ID: {error.digest}</p>
      )}
      <div className="flex gap-3">
        <Button onClick={reset} size="lg" className="min-h-[48px]">
          Try Again
        </Button>
        <Button
          onClick={() => (window.location.href = "/")}
          variant="outline"
          size="lg"
          className="min-h-[48px]"
        >
          Go to Home
        </Button>
      </div>
    </div>
  );
}
