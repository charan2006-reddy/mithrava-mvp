"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const CropDetailContent = dynamic(() => import("./CropDetailContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function CropDetailPage() {
  return <CropDetailContent />;
}
