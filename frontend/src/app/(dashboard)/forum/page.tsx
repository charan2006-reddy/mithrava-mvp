"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const ForumContent = dynamic(() => import("./ForumContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function ForumPage() {
  return <ForumContent />;
}
