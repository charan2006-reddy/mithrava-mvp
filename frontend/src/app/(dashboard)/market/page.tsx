"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const MarketContent = dynamic(() => import("./MarketContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function MarketPage() {
  return <MarketContent />;
}
