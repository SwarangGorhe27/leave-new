import type { MasterRecord, MasterTableColumnConfig } from "./types";

export function normalizeTableColumns(
  columns?: Array<string | MasterTableColumnConfig>,
): MasterTableColumnConfig[] {
  if (!columns?.length) {
    return [
      { key: "code", label: "Code", sortable: true, render: "code" },
      { key: "label", label: "Label / Name", sortable: true, render: "label", altKeys: ["name"] },
      { key: "is_active", label: "Active", render: "status" },
    ];
  }

  return columns.map((col) => (typeof col === "string" ? { key: col, label: col.replaceAll("_", " ") } : col));
}

export function getCellValue(record: MasterRecord, column: MasterTableColumnConfig): string {
  const keys = [column.key, ...(column.altKeys ?? [])];
  for (const key of keys) {
    const value = record[key];
    if (value !== undefined && value !== null && value !== "") return String(value);
  }
  return "-";
}

export function formatDateTime(value: unknown) {
  if (!value) return "-";
  const date = new Date(String(value));
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

export function sortRecords(records: MasterRecord[], column: MasterTableColumnConfig, direction: "asc" | "desc") {
  const factor = direction === "asc" ? 1 : -1;
  return [...records].sort((a, b) => {
    const av = getCellValue(a, column).toLowerCase();
    const bv = getCellValue(b, column).toLowerCase();
    if (av < bv) return -1 * factor;
    if (av > bv) return 1 * factor;
    return 0;
  });
}
