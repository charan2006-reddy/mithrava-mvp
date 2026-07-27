"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { WifiOff, RefreshCw, Leaf } from "lucide-react";

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    if (isOnline) {
      window.location.href = "/";
    }
  }, [isOnline]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center p-4">
      <Card className="max-w-md w-full shadow-lg">
        <CardContent className="p-8 text-center">
          <div className="mb-6">
            <Leaf className="h-12 w-12 text-green-600 mx-auto" />
          </div>

          <div className="mb-4 p-3 bg-amber-50 rounded-full w-fit mx-auto">
            <WifiOff className="h-8 w-8 text-amber-500" />
          </div>

          <h1 className="text-xl font-bold text-gray-900 mb-2">
            You&apos;re Offline
          </h1>
          <p className="text-sm text-gray-600 mb-6">
            It seems you&apos;ve lost your internet connection. Some features
            may not be available until you&apos;re back online.
          </p>

          <div className="space-y-3">
            <Button
              onClick={() => window.location.reload()}
              className="w-full bg-green-600 hover:bg-green-700 gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </Button>

            <p className="text-xs text-gray-400">
              Mithrava works best with an internet connection for AI features
              and real-time market data.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
