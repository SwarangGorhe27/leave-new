import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Employee } from "@/app/components/employees/mockData";
import {
  assignManager,
  exportOrgChart,
  fetchDirectReportees,
  fetchOrgChartTree,
  fetchUnassignedEmployees,
  flattenOrgChartTree,
  massTransfer,
  searchOrgChartEmployees,
  setTopLevelManager,
} from "@/app/modules/org-chart/orgChartApi";

export const orgChartKeys = {
  all: ["org-chart"] as const,
  tree: (team?: string) => [...orgChartKeys.all, "tree", team ?? "all"] as const,
  unassigned: (query?: string) => [...orgChartKeys.all, "unassigned", query ?? ""] as const,
  search: (q?: string, team?: string) =>
    [...orgChartKeys.all, "search", q ?? "", team ?? "all"] as const,
  reportees: (managerId?: string) =>
    [...orgChartKeys.all, "reportees", managerId ?? ""] as const,
};

export function useOrgChartTree(team?: string) {
  return useQuery({
    queryKey: orgChartKeys.tree(team),
    queryFn: async () => {
      const tree = await fetchOrgChartTree({
        team: team && team !== "All" ? team : undefined,
      });
      const employees = flattenOrgChartTree(tree.roots);
      const topLevelIds = new Set<string>();
      if (tree.top_level_manager_id) {
        topLevelIds.add(tree.top_level_manager_id);
      }
      tree.roots.forEach((root) => {
        if (root.is_top_level) topLevelIds.add(root.id);
      });
      return { tree, employees, topLevelIds };
    },
    staleTime: 30_000,
  });
}

export function useOrgChartUnassigned(query?: string) {
  return useQuery({
    queryKey: orgChartKeys.unassigned(query),
    queryFn: () => fetchUnassignedEmployees(query),
    staleTime: 30_000,
  });
}

export function useDirectReportees(managerId?: string, enabled = true) {
  return useQuery({
    queryKey: orgChartKeys.reportees(managerId),
    queryFn: () => fetchDirectReportees(managerId!),
    enabled: enabled && Boolean(managerId),
    staleTime: 15_000,
  });
}

export function useOrgChartEmployeeSearch(q?: string, team?: string, enabled = true) {
  return useQuery({
    queryKey: orgChartKeys.search(q, team),
    queryFn: () =>
      searchOrgChartEmployees({
        q: q?.trim() || undefined,
        team,
      }),
    enabled,
    staleTime: 15_000,
  });
}

export function useOrgChartMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: orgChartKeys.all });
  };

  const assignManagerMutation = useMutation({
    mutationFn: ({
      employeeId,
      managerId,
    }: {
      employeeId: string;
      managerId: string | null;
    }) => assignManager(employeeId, managerId),
    onSuccess: invalidate,
  });

  const setTopLevelMutation = useMutation({
    mutationFn: (managerId: string) => setTopLevelManager(managerId),
    onSuccess: invalidate,
  });

  const massTransferMutation = useMutation({
    mutationFn: massTransfer,
    onSuccess: invalidate,
  });

  const exportMutation = useMutation({
    mutationFn: exportOrgChart,
  });

  return {
    assignManagerMutation,
    setTopLevelMutation,
    massTransferMutation,
    exportMutation,
    invalidate,
  };
}

export type OrgChartTreeData = {
  tree: Awaited<ReturnType<typeof fetchOrgChartTree>>;
  employees: Employee[];
  topLevelIds: Set<string>;
};
