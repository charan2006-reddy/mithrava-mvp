"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Plus } from "lucide-react";
import { CropCard } from "@/components/crops/CropCard";
import { SearchBar } from "@/components/shared/SearchBar";
import { EmptyState } from "@/components/shared/EmptyState";
import { useLanguage } from "@/hooks/useLanguage";
import { useCrops } from "@/hooks/useCrops";

/* ─── Filter Tabs ─── */

type FilterType = "all" | "planted" | "growing" | "harvested" | "failed";

const FILTER_TABS: { key: FilterType; label: string }[] = [
  { key: "all", label: "All" },
  { key: "planted", label: "Planted" },
  { key: "growing", label: "Growing" },
  { key: "harvested", label: "Harvest Ready" },
  { key: "failed", label: "Failed" },
];

/* ─── Loading Skeleton ─── */

function CropCardSkeleton({ index }: { index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.05 }}
    >
      <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3 animate-pulse">
        <div className="flex items-start justify-between">
          <div className="h-8 w-8 rounded-lg bg-gray-200" />
          <div className="h-5 w-16 rounded-full bg-gray-200" />
        </div>
        <div className="h-4 w-24 rounded bg-gray-200" />
        <div className="h-3 w-16 rounded bg-gray-100" />
        <div className="h-2 w-full rounded-full bg-gray-100" />
      </div>
    </motion.div>
  );
}

/* ─── Page ─── */

export default function CropsPage() {
  const { t } = useLanguage();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");

  const { data: crops, isLoading, isError } = useCrops();

  const filteredCrops = useMemo(() => {
    if (!crops) return [];
    return crops.filter((crop) => {
      const nameMatch = crop.name.toLowerCase().includes(search.toLowerCase());
      const varietyMatch = (crop.variety ?? "")
        .toLowerCase()
        .includes(search.toLowerCase());
      const matchesSearch = nameMatch || varietyMatch;
      const matchesFilter = filter === "all" || crop.status === filter;
      return matchesSearch && matchesFilter;
    });
  }, [crops, search, filter]);

  const cropCounts = useMemo(() => {
    if (!crops) return { all: 0, planted: 0, growing: 0, harvested: 0, failed: 0 };
    return {
      all: crops.length,
      planted: crops.filter((c) => c.status === "planted").length,
      growing: crops.filter((c) => c.status === "growing").length,
      harvested: crops.filter((c) => c.status === "harvested").length,
      failed: crops.filter((c) => c.status === "failed").length,
    };
  }, [crops]);

  return (
    <div className="p-4 space-y-4 pb-24">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <h1 className="text-2xl font-bold">{t("crops.title")}</h1>
        <Link href="/crops/add">
          <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-mithrava-500 text-white font-semibold text-sm hover:bg-mithrava-600 active:bg-mithrava-700 transition-colors min-h-[44px]">
            <Plus className="h-5 w-5" />
            <span className="hidden sm:inline">{t("crops.addCrop")}</span>
          </button>
        </Link>
      </motion.div>

      {/* Search */}
      <SearchBar
        placeholder="Search crops..."
        value={search}
        onChange={setSearch}
      />

      {/* Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        {FILTER_TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all min-h-[40px] ${
              filter === tab.key
                ? "bg-mithrava-500 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {tab.label}
            <span
              className={`ml-1.5 text-xs ${
                filter === tab.key ? "text-mithrava-100" : "text-gray-400"
              }`}
            >
              {cropCounts[tab.key]}
            </span>
          </button>
        ))}
      </div>

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CropCardSkeleton key={i} index={i} />
          ))}
        </div>
      )}

      {/* Error State */}
      {isError && (
        <EmptyState
          icon={<span className="text-4xl">⚠️</span>}
          title="Unable to load crops"
          description="Something went wrong while fetching your crops. Please try again."
          actionLabel="Retry"
          onAction={() => window.location.reload()}
        />
      )}

      {/* Crops Grid */}
      {!isLoading && !isError && (
        <>
          {filteredCrops.length === 0 ? (
            <EmptyState
              icon={<span className="text-4xl">🌾</span>}
              title={
                search || filter !== "all"
                  ? "No crops match your search"
                  : t("crops.noCrops")
              }
              description={
                search || filter !== "all"
                  ? "Try a different search or filter."
                  : t("crops.noCropsDesc")
              }
              actionLabel={
                !search && filter === "all" ? t("crops.addFirstCrop") : undefined
              }
              onAction={
                !search && filter === "all"
                  ? () => {
                      window.location.href = "/crops/add";
                    }
                  : undefined
              }
            />
          ) : (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredCrops.map((crop, index) => (
                <CropCard
                  key={crop.id}
                  id={crop.id}
                  name={crop.name}
                  variety={crop.variety}
                  area={crop.area}
                  sowingDate={crop.sowingDate}
                  status={crop.status}
                  expectedHarvestDate={crop.expectedHarvestDate}
                  nextAction={crop.nextAction}
                  index={index}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* FAB for mobile */}
      <Link
        href="/crops/add"
        className="fixed bottom-24 right-4 md:hidden z-30"
      >
        <motion.div
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="flex h-14 w-14 items-center justify-center rounded-full bg-mithrava-500 text-white shadow-lg hover:bg-mithrava-600 transition-colors"
        >
          <Plus className="h-6 w-6" />
        </motion.div>
      </Link>
    </div>
  );
}
