/** Crop status — maps 1:1 with backend status values */
export type CropStatus = "planted" | "growing" | "harvested" | "failed";

/**
 * Raw crop object returned by the backend API (snake_case fields).
 * Use the `mapBackendCrop` helper in hooks/useCrops.ts to convert
 * this into the shape expected by CropCard / CropDetail pages.
 */
export interface BackendCrop {
  id: string;
  name: string;
  variety?: string;
  area_acres: number;
  status: CropStatus;
  planting_date: string;
  expected_harvest_date?: string;
  current_stage?: string;
  days_since_sowing?: number;
  week_number?: number;
  next_action?: string;
  created_at?: string;
  updated_at?: string;
  /* Optional nested data returned by the detail endpoint */
  stages?: CropStage[];
  tasks?: CropTask[];
  expenses?: CropExpense[];
  disease_scans?: CropDiseaseScan[];
}

/** Backend list response shape: `{ success, data: CropListResponse }` */
export interface CropListResponse {
  crops: BackendCrop[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

/** Crop model */
export interface Crop {
  id: string;
  farmerId: string;
  name: string;
  variety?: string;
  landId?: string;
  landName?: string;
  sowingDate: string;
  expectedHarvestDate?: string;
  actualHarvestDate?: string;
  area: number;
  areaUnit: "acres" | "hectares";
  status: CropStatus;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/** Crop calendar entry */
export interface CropCalendar {
  id: string;
  cropId: string;
  activity: string;
  date: string;
  completed: boolean;
  notes?: string;
}

/** Create crop request */
export interface CreateCropRequest {
  name: string;
  variety?: string;
  landId?: string;
  sowingDate: string;
  expectedHarvestDate?: string;
  area: number;
  areaUnit: "acres" | "hectares";
  notes?: string;
}

/** Update crop request */
export interface UpdateCropRequest extends Partial<CreateCropRequest> {
  status?: CropStatus;
  actualHarvestDate?: string;
}

/** Crop lifecycle stage */
export interface CropStage {
  id: string;
  name: string;
  weekStart: number;
  weekEnd: number;
  tasksCount: number;
  completed: boolean;
  current: boolean;
}

/** Crop calendar item with stages and tasks */
export interface CropCalendarItem {
  cropId: string;
  cropName: string;
  emoji: string;
  currentStage: string;
  stages: CropStage[];
  upcomingTasks: CropTask[];
}

/** Individual task in the crop calendar */
export interface CropTask {
  id: string;
  cropId: string;
  cropName: string;
  emoji: string;
  activity: string;
  date: string;
  completed: boolean;
  priority: "high" | "medium" | "low";
}

/** Daily action for the farmer */
export interface DailyAction {
  id: string;
  cropId: string;
  cropName: string;
  emoji: string;
  actionText: string;
  timeOfDay: "morning" | "afternoon" | "evening";
  priority: "high" | "medium" | "low";
  completed: boolean;
  details?: string;
}

/** Full crop detail response */
export interface CropDetailResponse {
  crop: Crop;
  calendar: CropCalendarItem;
  expenses: CropExpense[];
  diseaseScans: CropDiseaseScan[];
  progress: number;
  daysSinceSowing: number;
  nextAction?: string;
}

/** Expense for a specific crop */
export interface CropExpense {
  id: string;
  category: string;
  icon: string;
  amount: number;
  date: string;
  description?: string;
}

/** Disease scan for a specific crop */
export interface CropDiseaseScan {
  id: string;
  diseaseName?: string;
  confidence: number;
  severity?: "high" | "medium" | "low";
  imageUrl: string;
  createdAt: string;
}

/** Market price summary for dashboard */
export interface MarketPriceSummary {
  cropName: string;
  emoji: string;
  currentPrice: number;
  unit: string;
  trend: "up" | "down" | "stable";
  changePercent: number;
}

/** Crop calendar response from API */
export interface CropCalendarResponse {
  calendars: CropCalendarItem[];
  todayTasks: CropTask[];
}

/** Crop list item with computed fields for display */
export interface CropListItem extends Crop {
  emoji: string;
  daysSinceSowing: number;
  progress: number;
  nextAction?: string;
}
