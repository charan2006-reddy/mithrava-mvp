"use client";

import dynamic from "next/dynamic";
import { PageSkeleton } from "@/components/shared/LoadingSkeleton";

const WeatherContent = dynamic(() => import("./WeatherContent"), {
  loading: () => <PageSkeleton />,
  ssr: false,
});

export default function WeatherPage() {
  return <WeatherContent />;
}
