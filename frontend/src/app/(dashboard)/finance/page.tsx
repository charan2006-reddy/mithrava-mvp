"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const FinanceContent = dynamic(() => import("./FinanceContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function FinancePage() {
  return <FinanceContent />;
}
