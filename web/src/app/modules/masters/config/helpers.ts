import type { MasterCategoryConfig, MasterConfig, MasterFieldConfig } from "../types";

export const BASE_FIELDS: MasterFieldConfig[] = [
  { key: "code", label: "Code", type: "text", required: true, placeholder: "Enter code" },
  { key: "label", label: "Label / Name", type: "text", required: true, placeholder: "Enter label" },
  { key: "is_active", label: "Active", type: "boolean" },
];

export const COMPANY_FIELDS: MasterFieldConfig[] = [
  ...BASE_FIELDS,
  { key: "company", label: "Company", type: "select", relationMaster: "Company", required: true },
];

export function toKebabCase(value: string) {
  return value.replace(/([a-z])([A-Z])/g, "$1-$2").replace(/\s+/g, "-").toLowerCase();
}

export function formatApiLabel(apiName: string) {
  return apiName.replace(/([a-z])([A-Z])/g, "$1 $2").trim();
}

export type MasterDef = string | { apiName: string; label?: string; opts?: Partial<Omit<MasterConfig, "key" | "apiName" | "category">> };

export function makeMaster(
  category: string,
  apiName: string,
  opts?: Partial<Omit<MasterConfig, "key" | "apiName" | "category">>,
): MasterConfig {
  return {
    key: toKebabCase(apiName),
    apiName,
    label: opts?.label ?? formatApiLabel(apiName),
    category,
    formFields: BASE_FIELDS,
    ...opts,
  };
}

export function buildMasters(categoryKey: string, defs: MasterDef[], overrides?: Record<string, Partial<MasterConfig>>): MasterConfig[] {
  return defs.map((def) => {
    const apiName = typeof def === "string" ? def : def.apiName;
    const baseOpts = typeof def === "string" ? undefined : { label: def.label, ...def.opts };
    const master = makeMaster(categoryKey, apiName, {
      ...baseOpts,
      ...overrides?.[apiName],
    });
    return {
      ...master,
      category: categoryKey,
      categoryKey,
    };
  });
}

export function makeCategory(
  categoryKey: string,
  label: string,
  defs: MasterDef[],
  overrides?: Record<string, Partial<MasterConfig>>,
): MasterCategoryConfig {
  return {
    key: categoryKey,
    label,
    categoryKey,
    categoryLabel: label,
    masters: buildMasters(categoryKey, defs, overrides),
  };
}
