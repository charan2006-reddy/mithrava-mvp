import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4 text-center">
      <div className="text-6xl mb-6">🌾</div>
      <h1 className="text-4xl font-bold text-gray-900 mb-2">404</h1>
      <p className="text-lg text-gray-500 mb-1">Page Not Found</p>
      <p className="text-sm text-gray-400 mb-6 max-w-md">
        The page you are looking for does not exist or has been moved. Let&apos;s get you back on track.
      </p>
      <Link href="/">
        <Button size="lg" className="min-h-[48px]">
          Go to Home
        </Button>
      </Link>
    </div>
  );
}
