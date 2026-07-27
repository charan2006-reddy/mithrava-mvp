"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { cropService } from "@/services/cropService";
import type {
  BackendCrop,
  CropStage,
  CropTask,
  CropExpense,
  CropDiseaseScan,
  CreateCropRequest,
  UpdateCropRequest,
} from "@/types/crop";

/* ─── Backend → Frontend mapping helpers ─── */

/** Map a BackendCrop (snake_case) to the flat display shape used by CropCard */
export function mapBackendCrop(crop: BackendCrop) {
  return {
    id: crop.id,
    name: crop.name,
    variety: crop.variety,
    area: crop.area_acres,
    sowingDate: crop.planting_date,
    status: crop.status,
    expectedHarvestDate: crop.expected_harvest_date,
    nextAction: crop.next_action,
  };
}

/** Map a BackendCrop to the full detail shape used by [id]/page.tsx */
export function mapBackendCropDetail(crop: BackendCrop) {
  return {
    id: crop.id,
    name: crop.name,
    variety: crop.variety ?? "",
    status: crop.status,
    area: crop.area_acres,
    areaUnit: "acres" as const,
    sowingDate: crop.planting_date,
    expectedHarvestDate: crop.expected_harvest_date ?? "",
    currentStage: crop.current_stage ?? "Seedling",
    daysSinceSowing: crop.days_since_sowing ?? 0,
    weekNumber: crop.week_number ?? 0,
    nextAction: crop.next_action ?? "",
    stages: crop.stages,
    tasks: crop.tasks,
    expenses: crop.expenses,
    diseaseScans: crop.disease_scans,
  };
}

/** Compute days since sowing from an ISO date string */
export function daysSince(sowingDate: string): number {
  const sowing = new Date(sowingDate);
  const now = new Date();
  const diffMs = now.getTime() - sowing.getTime();
  return Math.max(0, Math.floor(diffMs / (1000 * 60 * 60 * 24)));
}

/* ─── React Query Hooks ─── */

/**
 * Fetch the full list of crops for the current farmer.
 * Returns an array of display-ready crop objects.
 */
export function useCrops() {
  return useQuery({
    queryKey: ["crops"],
    queryFn: async () => {
      const res = await cropService.list();
      return (res.data?.crops ?? []).map(mapBackendCrop);
    },
  });
}

/**
 * Fetch a single crop by ID.
 * Returns the mapped detail object or undefined while loading.
 */
export function useCropDetail(id: string | null) {
  return useQuery({
    queryKey: ["crops", id],
    queryFn: async () => {
      const res = await cropService.getById(id!);
      const raw = (res as unknown as { data?: BackendCrop }).data;
      return raw ? mapBackendCropDetail(raw) : null;
    },
    enabled: !!id,
  });
}

/** Create a new crop and invalidate the list cache on success */
export function useCreateCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateCropRequest) => cropService.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["crops"] }),
  });
}

/** Update an existing crop and invalidate the list + detail caches */
export function useUpdateCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateCropRequest }) =>
      cropService.update(id, data),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["crops"] });
      qc.invalidateQueries({ queryKey: ["crops", variables.id] });
    },
  });
}

/** Delete a crop and invalidate the list cache */
export function useDeleteCrop() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cropService.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["crops"] }),
  });
}
