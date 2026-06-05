import type { MasterFieldConfig } from "../types";
import { BASE_FIELDS, COMPANY_FIELDS } from "./helpers";

export const COMPANY_EXTRA_FIELDS: MasterFieldConfig[] = [
  ...BASE_FIELDS,
  { key: "pan", label: "PAN", type: "text", placeholder: "ABCDE1234F" },
  { key: "gstin", label: "GSTIN", type: "text" },
  { key: "cin", label: "CIN", type: "text" },
  { key: "registered_address", label: "Registered Address", type: "textarea" },
];

export const BRANCH_FIELDS: MasterFieldConfig[] = [
  ...COMPANY_FIELDS,
  {
    key: "branch_type",
    label: "Branch Type",
    type: "select",
    required: true,
    options: [
      { value: "HEAD_OFFICE", label: "Head Office" },
      { value: "BRANCH", label: "Branch" },
      { value: "REGIONAL", label: "Regional" },
      { value: "ZONAL", label: "Zonal" },
      { value: "DEPOT", label: "Depot" },
    ],
  },
  { key: "gstin", label: "GSTIN", type: "text" },
  { key: "pt_registration", label: "PT Registration", type: "text" },
  { key: "is_payroll_entity", label: "Payroll Entity", type: "boolean" },
];
