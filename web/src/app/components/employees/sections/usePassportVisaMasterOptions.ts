import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../../../api/client";

export type PassportVisaMasterResource = "passport-categories" | "passport-statuses";

export type MasterOption = { value: string; label: string };

function extractMasterRows(payload: unknown): Record<string, unknown>[] {
  if (Array.isArray(payload)) return payload as Record<string, unknown>[];
  if (!payload || typeof payload !== "object") return [];
  const obj = payload as Record<string, unknown>;
  if (Array.isArray(obj.results)) return obj.results as Record<string, unknown>[];
  if (obj.data && typeof obj.data === "object") {
    const inner = obj.data as Record<string, unknown>;
    if (Array.isArray(inner.results)) return inner.results as Record<string, unknown>[];
    if (Array.isArray(inner)) return inner as Record<string, unknown>[];
  }
  return [];
}

function mapRowsToOptions(rows: Record<string, unknown>[]): MasterOption[] {
  return rows.map((item) => {
    const id = String(item.id ?? "");
    const code = String(item.code ?? "");
    const label = String(item.label ?? item.name ?? item.title ?? code ?? id);
    return { value: id || code || label, label };
  });
}

/** Load passport/visa masters from dedicated API (with generic registry fallback). */
async function fetchPassportVisaMasterOptions(
  resource: PassportVisaMasterResource,
): Promise<MasterOption[]> {
  const genericName =
    resource === "passport-categories" ? "PassportCategory" : "PassportStatus";

  const attempts: Array<{ url: string; params?: Record<string, string | number> }> = [
    { url: `/masters/passport-visa/${resource}/dropdown/`, params: { limit: 200 } },
    {
      url: `/masters/passport-visa/${resource}/`,
      params: { page: 1, page_size: 200 },
    },
    { url: `/masters/${genericName}/`, params: { page: 1, page_size: 200 } },
  ];

  for (const { url, params } of attempts) {
    try {
      const res = await api.get(url, { params });
      const rows = extractMasterRows(res.data);
      const options = mapRowsToOptions(rows);
      if (options.length) return options;
      if (rows.length === 0 && res.status === 200) {
        return [];
      }
    } catch {
      /* try next path */
    }
  }

  return [];
}

export function usePassportVisaMasterOptions(resource: PassportVisaMasterResource) {
  const query = useQuery({
    queryKey: ["passport-visa-master", resource],
    queryFn: () => fetchPassportVisaMasterOptions(resource),
    staleTime: 5 * 60 * 1000,
  });

  const options = useMemo(() => query.data ?? [], [query.data]);

  return { options, isLoading: query.isLoading, isError: query.isError };
}
