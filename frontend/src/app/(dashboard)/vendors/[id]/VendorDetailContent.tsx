"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  ArrowLeft,
  Star,
  MapPin,
  Phone,
  Mail,
  Clock,
  ShieldCheck,
  MessageCircle,
  Send,
  Loader2,
  AlertCircle,
  Store,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { vendorService } from "@/services/vendorService";
import { VENDOR_TYPES } from "@/lib/constants";
import { timeAgo } from "@/lib/utils";
import type { Vendor, VendorReview } from "@/types/vendor";

// ---------------------------------------------------------------------------
// Star rating display helper
// ---------------------------------------------------------------------------

function StarRating({
  rating,
  size = "sm",
  interactive = false,
  onChange,
}: {
  rating: number;
  size?: "sm" | "md" | "lg";
  interactive?: boolean;
  onChange?: (rating: number) => void;
}) {
  const [hovered, setHovered] = useState(0);
  const sizeClass = size === "sm" ? "h-4 w-4" : size === "md" ? "h-5 w-5" : "h-6 w-6";

  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => {
        const starIndex = i + 1;
        const filled = interactive ? starIndex <= (hovered || rating) : starIndex <= Math.round(rating);
        return (
          <button
            key={i}
            type="button"
            disabled={!interactive}
            className={`${interactive ? "cursor-pointer hover:scale-110 transition-transform" : "cursor-default"} disabled:cursor-default`}
            onMouseEnter={() => interactive && setHovered(starIndex)}
            onMouseLeave={() => interactive && setHovered(0)}
            onClick={() => interactive && onChange?.(starIndex)}
          >
            <Star
              className={`${sizeClass} ${
                filled ? "fill-amber-400 text-amber-400" : "fill-gray-200 text-gray-200"
              } transition-colors`}
            />
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Skeleton loader
// ---------------------------------------------------------------------------

function VendorDetailSkeleton() {
  return (
    <div className="p-4 space-y-4">
      <Skeleton className="h-10 w-10 rounded-lg" />
      <div className="space-y-3">
        <Skeleton className="h-7 w-3/4" />
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-4 w-1/2" />
      </div>
      <Card>
        <CardContent className="p-4 space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 space-y-3">
          <Skeleton className="h-4 w-24" />
          <div className="flex gap-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4 space-y-3">
          <Skeleton className="h-4 w-32" />
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="flex items-start gap-3">
              <Skeleton className="h-8 w-8 rounded-full shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-3 w-24" />
                <Skeleton className="h-3 w-full" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function VendorDetailContent({ vendorId }: { vendorId: string }) {
  const { t } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  // Review form state
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState("");

  // Fetch vendor detail
  const {
    data: vendor,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["vendor", vendorId],
    queryFn: async () => {
      const res = await vendorService.getDetail(vendorId);
      return res.data;
    },
    enabled: !!vendorId,
  });

  // Submit review mutation
  const submitReviewMutation = useMutation({
    mutationFn: async () => {
      if (!vendorId || reviewRating === 0) return;
      return vendorService.addReview(vendorId, {
        rating: reviewRating,
        comment: reviewComment.trim(),
      });
    },
    onSuccess: () => {
      toast.success("Review submitted successfully!");
      queryClient.invalidateQueries({ queryKey: ["vendor", vendorId] });
      setShowReviewForm(false);
      setReviewRating(0);
      setReviewComment("");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to submit review. Please try again.");
    },
  });

  const handleSubmitReview = useCallback(() => {
    if (reviewRating === 0) {
      toast.error("Please select a rating");
      return;
    }
    submitReviewMutation.mutate();
  }, [reviewRating, submitReviewMutation]);

  // --- Loading state ---
  if (isLoading) {
    return <VendorDetailSkeleton />;
  }

  // --- Error state ---
  if (error) {
    return (
      <div className="p-4">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6 flex flex-col items-center gap-3 text-center">
            <AlertCircle className="h-10 w-10 text-red-500" />
            <p className="font-semibold text-red-700">Failed to load vendor details</p>
            <p className="text-sm text-red-500">
              {error instanceof Error ? error.message : "Please check your connection and try again."}
            </p>
            <Button variant="outline" size="sm" onClick={() => router.back()}>
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // --- Not found ---
  if (!vendor) {
    return (
      <div className="p-4">
        <Card className="border-dashed border-gray-300">
          <CardContent className="p-6 flex flex-col items-center gap-3 text-center">
            <Store className="h-10 w-10 text-gray-400" />
            <p className="font-semibold text-gray-700">Vendor not found</p>
            <p className="text-sm text-gray-500">This vendor may have been removed or does not exist.</p>
            <Button variant="outline" size="sm" onClick={() => router.back()}>
              Go Back
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // --- Resolve vendor type label ---
  const vendorTypeLabel =
    VENDOR_TYPES.find((v) => v.id === vendor.vendor_type)?.name || vendor.vendor_type;

  // --- Reviews ---
  const reviews: VendorReview[] = vendor.reviews ?? [];

  return (
    <div className="p-4 space-y-4 pb-8">
      {/* Back button */}
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors min-h-[44px]"
        >
          <ArrowLeft className="h-5 w-5" />
          Back
        </button>
      </motion.div>

      {/* Header section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <Card>
          <CardContent className="p-4 space-y-3">
            <div className="flex items-start gap-3">
              <div className="h-14 w-14 rounded-xl bg-mithrava-50 flex items-center justify-center text-2xl shrink-0">
                {VENDOR_TYPES.find((v) => v.id === vendor.vendor_type)?.icon || "🏪"}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="text-xl font-bold truncate">{vendor.name}</h1>
                  {vendor.is_verified && (
                    <ShieldCheck className="h-5 w-5 text-mithrava-500 shrink-0" />
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <Badge variant="secondary" className="text-xs">
                    {vendorTypeLabel}
                  </Badge>
                  <div className="flex items-center gap-1">
                    <StarRating rating={vendor.rating} size="sm" />
                    <span className="text-sm font-medium text-gray-700">
                      {vendor.rating.toFixed(1)}
                    </span>
                    <span className="text-sm text-gray-400">
                      ({vendor.review_count} {vendor.review_count === 1 ? "review" : "reviews"})
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Info section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardContent className="p-4 space-y-3">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
              Contact & Details
            </h2>

            {/* Phone */}
            {vendor.phone && (
              <a
                href={`tel:${vendor.phone}`}
                className="flex items-center gap-3 text-sm text-gray-700 hover:text-mithrava-500 transition-colors group"
              >
                <Phone className="h-4 w-4 text-gray-400 group-hover:text-mithrava-500 shrink-0" />
                <span>{vendor.phone}</span>
              </a>
            )}

            {/* Email */}
            {vendor.email && (
              <a
                href={`mailto:${vendor.email}`}
                className="flex items-center gap-3 text-sm text-gray-700 hover:text-mithrava-500 transition-colors group"
              >
                <Mail className="h-4 w-4 text-gray-400 group-hover:text-mithrava-500 shrink-0" />
                <span>{vendor.email}</span>
              </a>
            )}

            {/* Location */}
            {(vendor.city || vendor.state || vendor.address) && (
              <div className="flex items-start gap-3 text-sm text-gray-700">
                <MapPin className="h-4 w-4 text-gray-400 shrink-0 mt-0.5" />
                <span>
                  {[vendor.address, vendor.city, vendor.state].filter(Boolean).join(", ")}
                </span>
              </div>
            )}

            {/* Operating hours */}
            {vendor.operating_hours && (
              <div className="flex items-start gap-3 text-sm text-gray-700">
                <Clock className="h-4 w-4 text-gray-400 shrink-0 mt-0.5" />
                <span>{vendor.operating_hours}</span>
              </div>
            )}

            {/* Description */}
            {vendor.description && (
              <p className="text-sm text-gray-600 leading-relaxed pt-1 border-t border-gray-100 mt-2">
                {vendor.description}
              </p>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Services section */}
      {vendor.services && vendor.services.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          <Card>
            <CardContent className="p-4 space-y-3">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Services
              </h2>
              <div className="flex flex-wrap gap-2">
                {vendor.services.map((service) => (
                  <Badge key={service} variant="outline" className="text-xs">
                    {service}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Reviews section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardContent className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
                Reviews ({reviews.length})
              </h2>
              {isAuthenticated && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowReviewForm(!showReviewForm)}
                  className="gap-1.5"
                >
                  <MessageCircle className="h-3.5 w-3.5" />
                  Write a Review
                </Button>
              )}
            </div>

            {/* Review form */}
            <AnimatePresence>
              {showReviewForm && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="border border-gray-200 rounded-lg p-4 space-y-3 bg-gray-50">
                    <p className="text-sm font-medium text-gray-700">Your Rating</p>
                    <StarRating
                      rating={reviewRating}
                      size="lg"
                      interactive
                      onChange={setReviewRating}
                    />
                    <textarea
                      placeholder="Share your experience (optional)..."
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      rows={3}
                      className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-mithrava-500 resize-none"
                    />
                    <div className="flex items-center gap-2 justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setShowReviewForm(false);
                          setReviewRating(0);
                          setReviewComment("");
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        size="sm"
                        onClick={handleSubmitReview}
                        disabled={reviewRating === 0 || submitReviewMutation.isPending}
                        className="gap-1.5"
                      >
                        {submitReviewMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Send className="h-3.5 w-3.5" />
                        )}
                        Submit
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Not authenticated prompt */}
            {!isAuthenticated && reviews.length > 0 && (
              <p className="text-xs text-gray-400 text-center">
                Log in to write a review
              </p>
            )}

            {/* Reviews list */}
            {reviews.length === 0 && !showReviewForm && (
              <div className="text-center py-6">
                <MessageCircle className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No reviews yet</p>
                {isAuthenticated && (
                  <p className="text-xs text-gray-400 mt-1">Be the first to share your experience!</p>
                )}
              </div>
            )}

            {reviews.length > 0 && (
              <div className="space-y-3">
                {reviews.map((review, index) => (
                  <motion.div
                    key={review.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                    className="border-t border-gray-100 pt-3 first:border-0 first:pt-0"
                  >
                    <div className="flex items-start gap-3">
                      <div className="h-8 w-8 rounded-full bg-mithrava-50 flex items-center justify-center text-xs font-semibold text-mithrava-600 shrink-0">
                        {review.farmer_id.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium text-gray-800">
                            Farmer {review.farmer_id.slice(0, 8)}
                          </span>
                          <span className="text-xs text-gray-400">•</span>
                          {review.created_at && (
                            <span className="text-xs text-gray-400">
                              {timeAgo(review.created_at)}
                            </span>
                          )}
                        </div>
                        <StarRating rating={review.rating} size="sm" />
                        {review.comment && (
                          <p className="text-sm text-gray-600 mt-1 leading-relaxed">
                            {review.comment}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
