"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

/**
 * Client-side providers wrapper.
 *
 * Wraps the app in React Query's QueryClientProvider so all useQuery /
 * useMutation hooks work. Separated into its own "use client" file so the
 * root layout can remain a Server Component.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute — data considered fresh
            gcTime: 5 * 60 * 1000, // 5 minutes — keep in cache
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
