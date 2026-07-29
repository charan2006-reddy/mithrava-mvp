"use client";

import dynamic from "next/dynamic";
import { Skeleton } from "@/components/ui/skeleton";

const VendorDetailContent = dynamic(() => import("./VendorDetailContent"), {
  ssr: false,
  loading: () => (
    <div className="p-4 space-y-4">
      <Skeleton className="h-10 w-10 rounded-lg" />
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-40 w-full rounded-lg" />
      <Skeleton className="h-32 w-full rounded-lg" />
    </div>
  ),
});

export default function VendorDetailWrapper({ vendorId }: { vendorId: string }) {
  return <VendorDetailContent vendorId={vendorId} />;
}
