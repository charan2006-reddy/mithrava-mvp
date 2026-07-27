"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Search, Star, MapPin, Phone, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useLanguage } from "@/hooks/useLanguage";
import { useVendors } from "@/hooks/useVendors";
import { VENDOR_TYPES } from "@/lib/constants";

const vendorTypeEmoji: Record<string, string> = {
  fertilizer_shop: "🧪",
  seed_shop: "🌱",
  equipment_rental: "🚜",
  mandi: "🏪",
  transport: "🚛",
  processor: "🏭",
  other: "📦",
};

/** Loading skeleton that mimics the vendor card grid */
function VendorCardSkeleton({ index }: { index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Skeleton className="h-12 w-12 shrink-0 rounded-xl" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function VendorsPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string | null>(null);

  const { data: vendors = [], isLoading, isError } = useVendors({
    ...(search && { city: search }),
    ...(selectedType && { vendor_type: selectedType }),
  });

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">{t("vendor.title")}</h1>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <Input
          placeholder={t("vendor.searchCity")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Type Filter */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setSelectedType(null)}
          className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors min-h-[40px] ${
            !selectedType
              ? "bg-mithrava-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {t("common.all")}
        </button>
        {VENDOR_TYPES.map((type) => (
          <button
            key={type.id}
            onClick={() => setSelectedType(selectedType === type.id ? null : type.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors min-h-[40px] ${
              selectedType === type.id
                ? "bg-mithrava-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {type.icon} {type.name}
          </button>
        ))}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <VendorCardSkeleton key={i} index={i} />
          ))}
        </div>
      )}

      {/* Error State */}
      {isError && (
        <EmptyState
          icon={<span className="text-3xl">⚠️</span>}
          title="Failed to load vendors"
          description="Please check your connection and try again."
        />
      )}

      {/* Vendor Grid */}
      {!isLoading && !isError && vendors.length === 0 && (
        <EmptyState
          icon={<span className="text-3xl">🏪</span>}
          title={t("vendor.noVendors")}
          description={t("vendor.noVendorsDesc")}
        />
      )}

      {!isLoading && !isError && vendors.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {vendors.map((vendor, index) => (
            <motion.div
              key={vendor.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => router.push(`/vendors/${vendor.id}`)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="h-12 w-12 rounded-xl bg-mithrava-50 flex items-center justify-center text-2xl shrink-0">
                      {vendorTypeEmoji[vendor.vendor_type] || "🏪"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-base truncate">{vendor.name}</h3>
                        {vendor.is_verified && (
                          <ShieldCheck className="h-4 w-4 text-mithrava-500 shrink-0" />
                        )}
                      </div>
                      <Badge variant="secondary" className="text-[10px] mt-1">
                        {VENDOR_TYPES.find((v) => v.id === vendor.vendor_type)?.name || vendor.vendor_type}
                      </Badge>
                      <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {vendor.city}
                        </span>
                        <span className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-amber-500" />
                          {vendor.rating} ({vendor.review_count})
                        </span>
                      </div>
                      {vendor.phone && (
                        <span className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                          <Phone className="h-3 w-3" />
                          {vendor.phone}
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
