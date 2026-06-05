import { useMemo } from "react";
import { useMasterList } from "../../../modules/masters/hooks";

export function useMasterOptions(masterName: string) {
  const query = useMemo(
    () => ({ is_active: "true" as const, page: 1, page_size: 200 }),
    [],
  );
  const { data } = useMasterList(masterName, query);

  return useMemo(
    () =>
      (data?.results ?? []).map((item) => {
        const id = String(item.id ?? "");
        const label = String(item.label ?? item.name ?? item.title ?? item.code ?? id);
        return { value: id, label };
      }),
    [data?.results],
  );
}
