import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createMaster, deleteMaster, getMasterList, patchMaster } from "./api";
import type { MasterListQuery } from "./types";

function queryKey(masterApiName: string, query: MasterListQuery) {
  return ["masters", masterApiName, query] as const;
}

export function useMasterList(masterApiName: string, query: MasterListQuery, enabled = true) {
  return useQuery({
    queryKey: queryKey(masterApiName, query),
    queryFn: () => getMasterList(masterApiName, query),
    enabled,
  });
}

export function useMasterCreate(masterApiName: string, _query: MasterListQuery) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => createMaster(masterApiName, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["masters", masterApiName] }),
  });
}

export function useMasterUpdate(masterApiName: string, _query: MasterListQuery) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string | number; payload: Record<string, unknown> }) =>
      patchMaster(masterApiName, id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["masters", masterApiName] }),
  });
}

export function useMasterToggleActive(masterApiName: string, _query: MasterListQuery) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_active }: { id: string | number; is_active: boolean }) =>
      patchMaster(masterApiName, id, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["masters", masterApiName] }),
  });
}

export function useMasterDelete(masterApiName: string, _query: MasterListQuery) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string | number) => deleteMaster(masterApiName, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["masters", masterApiName] }),
  });
}

