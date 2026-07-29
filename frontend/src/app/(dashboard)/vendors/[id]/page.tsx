import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import VendorDetailWrapper from "./VendorDetailWrapper";

export default async function VendorDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <Suspense
      fallback={
        <div className="p-4 space-y-4">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-40 w-full rounded-lg" />
        </div>
      }
    >
      <VendorDetailWrapper vendorId={id} />
    </Suspense>
  );
}
