export { MASTER_CATEGORIES } from "./config/categories";
export { BASE_FIELDS, COMPANY_FIELDS, buildMasters, formatApiLabel, makeCategory, makeMaster, toKebabCase } from "./config/helpers";
export type { MasterDef } from "./config/helpers";
export { BRANCH_FIELDS, COMPANY_EXTRA_FIELDS } from "./config/fieldPresets";
export type { MasterConfig } from "./types";
import { MASTER_CATEGORIES } from "./config/categories";

export const MASTER_CONFIG_MAP = new Map(
  MASTER_CATEGORIES.flatMap((category) => category.masters.map((master) => [master.key, master] as const)),
);

export function getCategory(categoryKey: string) {
  return MASTER_CATEGORIES.find((category) => category.key === categoryKey);
}

export function getMasterConfig(categoryKey: string, masterKey: string) {
  const category = getCategory(categoryKey);
  return category?.masters.find((master) => master.key === masterKey);
}
