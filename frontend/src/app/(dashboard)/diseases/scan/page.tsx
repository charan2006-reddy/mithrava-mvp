"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const DiseaseScanContent = dynamic(() => import("./DiseaseScanContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function DiseaseScanPage() {
  return <DiseaseScanContent />;
}
