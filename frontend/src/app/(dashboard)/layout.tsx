"use client";

import { DashboardShell } from "@/components/layout/DashboardShell";
import { PageErrorBoundary } from "@/components/shared/PageErrorBoundary";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardShell>
      <PageErrorBoundary>{children}</PageErrorBoundary>
    </DashboardShell>
  );
}
