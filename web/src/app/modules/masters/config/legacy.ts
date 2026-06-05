import { LEGACY_LEAVE_MASTER_KEY_ALIASES } from "../leave";
import type { MasterSectionRoute } from "../types";
import { MASTER_CATEGORIES } from "./categories";
import { toKebabCase } from "./helpers";

/** Maps retired category URL segments to their replacement domain category. */
export const LEGACY_CATEGORY_ALIASES: Record<string, string> = {
  personal: "employee",
  education: "employee",
  employment: "employee",
  location: "organization",
  insurance: "employee",
  misc: "employee",
  "core-hr-setup": "organization",
  "attendance-leave": "attendance",
  "payroll-compliance": "payroll",
  "performance-training-asset": "performance",
  "workflow-security-notification": "workflow-security",
  "audit-addition": "employee",
};

/** Masters that lived under attendance-leave but belong to the leave domain. */
const LEAVE_DOMAIN_MASTER_KEYS = new Set([
  ...Object.keys(LEGACY_LEAVE_MASTER_KEY_ALIASES),
  ...Object.values(LEGACY_LEAVE_MASTER_KEY_ALIASES),
  "leave-type",
  "leave-policy",
  "leave-policy-rule",
  "leave-encashment-policy",
  "leave-reason",
  "calendar-period",
  "accrual-schedule",
]);

/** Masters that lived under core-hr-setup but belong to attendance. */
const CORE_HR_ATTENDANCE_MASTER_KEYS = new Set(
  ["Shift", "ShiftType", "ShiftRotation", "WorkWeekPolicy", "HolidayGroup"].map(toKebabCase),
);

/** Masters that lived under core-hr-setup but belong to leave (retired → aliased). */
const CORE_HR_LEAVE_MASTER_KEYS = new Set(["holiday-calendar", "holiday", "calendar-period"]);

/** Masters that lived under performance-training-asset but belong to training-asset. */
const PERFORMANCE_TRAINING_ASSET_MASTER_KEYS = new Set(
  [
    "TrainingCategory",
    "TrainingMode",
    "TrainerType",
    "Course",
    "AssetCategory",
    "AssetCondition",
    "AssetType",
    "AssetStatus",
    "AssetAllocationType",
    "Vendor",
  ].map(toKebabCase),
);

function resolveLeaveMasterKey(masterKey: string): string {
  return LEGACY_LEAVE_MASTER_KEY_ALIASES[masterKey] ?? masterKey;
}

function findCategoryForMaster(masterKey: string): string | undefined {
  const resolvedKey = resolveLeaveMasterKey(masterKey);
  return MASTER_CATEGORIES.find((category) => category.masters.some((master) => master.key === resolvedKey))?.key;
}

function resolveLegacyCategory(categoryKey: string, masterKey: string): string | undefined {
  if (categoryKey === "attendance-leave") {
    return LEAVE_DOMAIN_MASTER_KEYS.has(masterKey) ? "leave" : "attendance";
  }

  if (categoryKey === "core-hr-setup") {
    if (CORE_HR_LEAVE_MASTER_KEYS.has(masterKey)) return "leave";
    if (CORE_HR_ATTENDANCE_MASTER_KEYS.has(masterKey)) return "attendance";
    return "organization";
  }

  if (categoryKey === "performance-training-asset") {
    return PERFORMANCE_TRAINING_ASSET_MASTER_KEYS.has(masterKey) ? "training-asset" : "performance";
  }

  return LEGACY_CATEGORY_ALIASES[categoryKey];
}

export function getCategory(categoryKey: string) {
  return MASTER_CATEGORIES.find((category) => category.key === categoryKey);
}

export function getMasterConfig(categoryKey: string, masterKey: string) {
  const category = getCategory(categoryKey);
  const resolvedKey = resolveLeaveMasterKey(masterKey);
  return category?.masters.find((master) => master.key === resolvedKey);
}

/** Resolves category/master URL params with backward compatibility for retired paths. */
export function resolveMasterSection(categoryKey: string, masterKey: string): MasterSectionRoute | null {
  const resolvedMasterKey = resolveLeaveMasterKey(masterKey);

  if (getMasterConfig(categoryKey, resolvedMasterKey)) {
    return { categoryKey, masterKey: resolvedMasterKey };
  }

  const legacyCategory = resolveLegacyCategory(categoryKey, resolvedMasterKey);
  if (legacyCategory && getMasterConfig(legacyCategory, resolvedMasterKey)) {
    return { categoryKey: legacyCategory, masterKey: resolvedMasterKey };
  }

  const discoveredCategory = findCategoryForMaster(resolvedMasterKey);
  if (discoveredCategory) {
    return { categoryKey: discoveredCategory, masterKey: resolvedMasterKey };
  }

  return null;
}

export const MASTER_CONFIG_MAP = new Map(
  MASTER_CATEGORIES.flatMap((category) => category.masters.map((master) => [master.key, master] as const)),
);
