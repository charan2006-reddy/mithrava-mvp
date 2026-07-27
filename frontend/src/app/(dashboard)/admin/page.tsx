"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const AdminContent = dynamic(() => import("./AdminContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function AdminPage() {
  return <AdminContent />;
}
