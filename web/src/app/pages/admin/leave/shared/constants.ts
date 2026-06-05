export const EXPORT_FORMATS = ["CSV", "Excel", "PDF"] as const;
export type ExportFormat = (typeof EXPORT_FORMATS)[number];

export const DEFAULT_PAGE_SIZE = 10;

