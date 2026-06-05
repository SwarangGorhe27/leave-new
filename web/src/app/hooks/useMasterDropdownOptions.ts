import { useMemo } from "react";
import { useMasterList } from "@/app/modules/masters/hooks";

/**
 * Hook to fetch master options for dropdown/select components
 * Automatically handles data transformation and null/undefined cases
 * 
 * @param masterName - The master type name (e.g., 'Gender', 'Department')
 * @param isActive - Whether to filter for active records only (default: true)
 * @returns Array of { value, label } objects ready for dropdown components
 */
export function useMasterDropdownOptions(masterName: string, isActive = true) {
  const query = useMemo(
    () => ({ is_active: isActive ? "true" : "false" } as const),
    [isActive]
  );
  const { data, isLoading, error } = useMasterList(masterName, query);

  return useMemo(
    () => {
      if (!data?.results || !Array.isArray(data.results)) {
        return [];
      }

      return data.results.map((item: any) => {
        const id = String(item.id ?? "");
        const label = String(
          item.label ?? item.name ?? item.title ?? item.code ?? id
        );
        return { value: id, label };
      });
    },
    [data?.results]
  );
}

/**
 * Hook to fetch master options with loading and error states
 * Use this when you need to handle loading/error UI
 * 
 * @param masterName - The master type name
 * @param isActive - Filter for active records
 * @returns { options, isLoading, error }
 */
export function useMasterDropdownOptionsWithState(masterName: string, isActive = true) {
  const query = useMemo(
    () => ({ is_active: isActive ? "true" : "false" } as const),
    [isActive]
  );
  const { data, isLoading, error } = useMasterList(masterName, query);

  const options = useMemo(
    () => {
      if (!data?.results || !Array.isArray(data.results)) {
        return [];
      }

      return data.results.map((item: any) => {
        const id = String(item.id ?? "");
        const label = String(
          item.label ?? item.name ?? item.title ?? item.code ?? id
        );
        return { value: id, label };
      });
    },
    [data?.results]
  );

  return { options, isLoading, error };
}

/**
 * Hook for multi-select dropdowns
 * Returns options that can be selected multiple times
 * 
 * @param masterName - The master type name
 * @param isActive - Filter for active records
 * @returns Array of { value, label } objects
 */
export function useMasterMultiSelectOptions(masterName: string, isActive = true) {
  return useMasterDropdownOptions(masterName, isActive);
}
