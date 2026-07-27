"use client";

import { Header } from "@/components/layout/Header";
import { BottomNav } from "@/components/layout/BottomNav";
import { Sidebar } from "@/components/layout/Sidebar";
import { MobileNav } from "@/components/layout/MobileNav";
import { MitraWidget } from "@/components/mitra/MitraWidget";
import { VoiceBar } from "@/components/voice/VoiceBar";
import { useAuth } from "@/hooks/useAuth";
import { useVoiceStore } from "@/stores/voiceStore";

/**
 * Shared dashboard shell layout providing sidebar, header, bottom nav,
 * floating Mitra widget, and global voice bar. Used by both the dashboard
 * route group layout and the root page (for authenticated users).
 */
export function DashboardShell({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const { voiceEnabled } = useVoiceStore();

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Mobile Nav Overlay */}
      <MobileNav />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto pb-20 md:pb-4">
          {children}
        </main>
      </div>

      {/* Bottom Navigation (Mobile) */}
      <BottomNav />

      {/* Floating widgets — stacked vertically to avoid overlap */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3">
        <MitraWidget />
        {isAuthenticated && voiceEnabled && <VoiceBar />}
      </div>
    </div>
  );
}
