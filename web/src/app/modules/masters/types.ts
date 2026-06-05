export type MasterFieldType = "text" | "textarea" | "number" | "select" | "boolean" | "date" | "time" | "multiselect" | "color";

export interface MasterFieldDisabledWhen {
  field: string;
  equals?: boolean | string | number;
  notEquals?: boolean | string | number;
}

export interface MasterFormBehaviorRule {
  when: { field: string; equals: string | boolean | number };
  set?: Record<string, unknown>;
}

export interface MasterFieldConfig {
  key: string;
  label: string;
  type: MasterFieldType;
  required?: boolean;
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  relationMaster?: string;
  relationLabelKey?: string;
  relationValueKey?: string;
  defaultValue?: unknown;
  disabledWhen?: MasterFieldDisabledWhen;
  section?: string;
  readOnly?: boolean;
  min?: number;
  max?: number;
}

export type MasterTableColumnRender = "code" | "label" | "status" | "datetime" | "boolean" | "default";

export interface MasterTableColumnConfig {
  key: string;
  label: string;
  sortable?: boolean;
  render?: MasterTableColumnRender;
  altKeys?: string[];
}

export interface MasterConfig {
  key: string;
  apiName: string;
  label: string;
  category: string;
  categoryKey?: string;
  categoryLabel?: string;
  constant?: boolean;
  companyScoped?: boolean;
  parentFieldKey?: string;
  formFields?: MasterFieldConfig[];
  listColumns?: Array<string | MasterTableColumnConfig>;
  defaultValues?: Record<string, unknown>;
  validationSchema?: import("zod").ZodTypeAny;
  searchPlaceholder?: string;
  formBehaviors?: MasterFormBehaviorRule[];
}

export interface MasterCategoryConfig {
  key: string;
  label: string;
  categoryKey?: string;
  categoryLabel?: string;
  masters: MasterConfig[];
}

export interface MasterRecord {
  id: string | number;
  code: string;
  label?: string;
  name?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  company?: string | number | null;
  company_name?: string;
  [key: string]: unknown;
}

export interface PaginatedMasterResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface MasterListQuery {
  search?: string;
  company?: string;
  is_active?: "true" | "false";
  page?: number;
  page_size?: number;
}
