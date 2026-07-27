/** Disease severity level */
export type DiseaseSeverity = "low" | "medium" | "high" | "critical";

/** Treatment plan with categorized treatments */
export interface TreatmentPlan {
  organic: string[];
  chemical: string[];
  prevention: string[];
  urgency: "immediate" | "within_days" | "preventive";
}

/** Disease scan result */
export interface DiseaseScan {
  id: string;
  farmerId: string;
  cropId?: string;
  imageUrl: string;
  diseaseName?: string;
  confidence: number;
  severity?: DiseaseSeverity;
  isHealthy: boolean;
  description?: string;
  treatment?: string;
  treatmentJson?: TreatmentPlan;
  preventionJson?: string[];
  notes?: string;
  analyzedAt: string;
  createdAt: string;
}

/** Disease detection result */
export interface DiseaseResult {
  diseaseName: string;
  confidence: number;
  severity: DiseaseSeverity;
  description: string;
  treatment: string;
  prevention: string[];
  imagePreviewUrl?: string;
}

/** Disease scan history */
export interface DiseaseHistory {
  scans: DiseaseScan[];
  total: number;
}

/** Upload disease scan request */
export interface DiseaseScanRequest {
  imageUrl: string;
  cropName?: string;
  cropId?: string;
}

/** Full scan detail response from API */
export interface DiseaseScanDetail {
  id: string;
  imageUrl: string;
  diseaseName: string;
  confidence: number;
  severity: DiseaseSeverity;
  isHealthy: boolean;
  description: string;
  treatmentPlan: TreatmentPlan;
  cropId?: string;
  cropName?: string;
  cropEmoji?: string;
  analyzedAt: string;
  beforeImageUrl?: string;
  afterImageUrl?: string;
}

/** Simplified scan item for history cards */
export interface ScanHistoryItem {
  id: string;
  imageUrl: string;
  diseaseName: string;
  confidence: number;
  severity: DiseaseSeverity;
  isHealthy: boolean;
  cropName?: string;
  analyzedAt: string;
}
